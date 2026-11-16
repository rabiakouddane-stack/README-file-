"""Un premier agent IA en Python, construit avec l'API Claude.

Un « agent », c'est un modèle d'IA qui peut décider tout seul d'utiliser des
outils (des fonctions Python) pour accomplir une tâche, puis qui regarde le
résultat et continue jusqu'à avoir fini. Ce fichier montre la boucle complète :

    1. on envoie la question de l'utilisateur à Claude, avec la liste des outils ;
    2. Claude répond, soit avec du texte (il a fini), soit en demandant un outil ;
    3. on exécute l'outil demandé et on renvoie le résultat à Claude ;
    4. on recommence à l'étape 2.

Lancer :  python agents/assistant.py
"""

import ast
import operator
from datetime import datetime
from pathlib import Path

import anthropic

MODELE = "claude-opus-5-5"

# Dossier dans lequel l'agent a le droit de lire et d'écrire (la racine du projet).
DOSSIER_PROJET = Path(__file__).resolve().parent.parent
FICHIER_NOTES = DOSSIER_PROJET / "notes.md"

CONSIGNES = """Tu es un assistant francophone, clair et bienveillant.
Tu peux utiliser des outils pour faire des calculs, connaître la date,
lire les fichiers du projet et prendre des notes. Utilise un outil
dès qu'il te donne une réponse plus fiable que ta mémoire (calculs, date,
contenu d'un fichier). Réponds toujours en français, de façon concise."""


# ---------------------------------------------------------------------------
# 1. Les outils : de simples fonctions Python
# ---------------------------------------------------------------------------

_OPERATEURS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.Mod: operator.mod,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}


def _evaluer(noeud):
    if isinstance(noeud, ast.Constant) and isinstance(noeud.value, (int, float)):
        return noeud.value
    if isinstance(noeud, ast.BinOp) and type(noeud.op) in _OPERATEURS:
        return _OPERATEURS[type(noeud.op)](_evaluer(noeud.left), _evaluer(noeud.right))
    if isinstance(noeud, ast.UnaryOp) and type(noeud.op) in _OPERATEURS:
        return _OPERATEURS[type(noeud.op)](_evaluer(noeud.operand))
    raise ValueError("expression non autorisée")


def calculer(expression: str) -> str:
    """Calcule une expression mathématique simple, sans exécuter de code."""
    return str(_evaluer(ast.parse(expression, mode="eval").body))


def date_et_heure() -> str:
    """Donne la date et l'heure actuelles."""
    return datetime.now().strftime("%A %d %B %Y, %H:%M")


def _chemin_sur(nom: str) -> Path:
    chemin = (DOSSIER_PROJET / nom).resolve()
    if not chemin.is_relative_to(DOSSIER_PROJET) or ".git" in chemin.parts:
        raise ValueError("accès refusé : le fichier doit être dans le projet")
    return chemin


def lister_fichiers() -> str:
    """Liste les fichiers du projet."""
    fichiers = sorted(
        str(f.relative_to(DOSSIER_PROJET))
        for f in DOSSIER_PROJET.rglob("*")
        if f.is_file() and ".git" not in f.parts and "__pycache__" not in f.parts
    )
    return "\n".join(fichiers)


def lire_fichier(nom: str) -> str:
    """Lit un fichier texte du projet."""
    return _chemin_sur(nom).read_text(encoding="utf-8")[:20000]


def prendre_note(texte: str) -> str:
    """Ajoute une note datée dans notes.md."""
    with FICHIER_NOTES.open("a", encoding="utf-8") as f:
        f.write(f"- {datetime.now():%Y-%m-%d %H:%M} — {texte}\n")
    return "Note enregistrée dans notes.md"


# ---------------------------------------------------------------------------
# 2. La description des outils, pour que Claude sache quand les utiliser
# ---------------------------------------------------------------------------

OUTILS = [
    {
        "name": "calculer",
        "description": "Calcule une expression mathématique (+, -, *, /, **, %, parenthèses). "
        "Exemple : '(12.5 * 4) / 3'.",
        "input_schema": {
            "type": "object",
            "properties": {"expression": {"type": "string", "description": "L'expression à calculer."}},
            "required": ["expression"],
        },
    },
    {
        "name": "date_et_heure",
        "description": "Renvoie la date et l'heure actuelles.",
        "input_schema": {"type": "object", "properties": {}},
    },
    {
        "name": "lister_fichiers",
        "description": "Liste les fichiers présents dans le projet.",
        "input_schema": {"type": "object", "properties": {}},
    },
    {
        "name": "lire_fichier",
        "description": "Lit le contenu d'un fichier texte du projet (chemin relatif, ex. 'README.md').",
        "input_schema": {
            "type": "object",
            "properties": {"nom": {"type": "string", "description": "Chemin relatif du fichier."}},
            "required": ["nom"],
        },
    },
    {
        "name": "prendre_note",
        "description": "Enregistre une note dans le fichier notes.md quand l'utilisateur demande de retenir quelque chose.",
        "input_schema": {
            "type": "object",
            "properties": {"texte": {"type": "string", "description": "Le texte de la note."}},
            "required": ["texte"],
        },
    },
]

FONCTIONS = {
    "calculer": calculer,
    "date_et_heure": date_et_heure,
    "lister_fichiers": lister_fichiers,
    "lire_fichier": lire_fichier,
    "prendre_note": prendre_note,
}


def executer_outil(nom: str, arguments: dict) -> dict:
    """Exécute l'outil demandé par Claude et prépare le résultat à lui renvoyer."""
    try:
        resultat = FONCTIONS[nom](**arguments)
        return {"content": resultat}
    except Exception as erreur:  # on renvoie l'erreur à Claude, qui pourra corriger
        return {"content": f"Erreur : {erreur}", "is_error": True}


# ---------------------------------------------------------------------------
# 3. La boucle de l'agent
# ---------------------------------------------------------------------------

def tour_agent(client: anthropic.Anthropic, messages: list) -> str:
    """Fait travailler l'agent jusqu'à ce qu'il ait une réponse finale."""
    while True:
        reponse = client.beta.messages.create(
            model=MODELE,
            max_tokens=16000,
            system=CONSIGNES,
            tools=OUTILS,
            messages=messages,
            thinking={"type": "adaptive"},
            output_config={"effort": "medium"},
            # Si le modèle décline une demande, l'API réessaie avec un autre modèle.
            betas=["server-side-fallback-2026-07-01"],
            fallbacks="default",
        )
        # On garde toujours la réponse complète dans l'historique.
        messages.append({"role": "assistant", "content": reponse.content})

        if reponse.stop_reason == "refusal":
            return "(L'agent a refusé de répondre à cette demande.)"
        if reponse.stop_reason == "pause_turn":
            continue
        if reponse.stop_reason != "tool_use":
            return "".join(b.text for b in reponse.content if b.type == "text")

        # Claude demande un ou plusieurs outils : on les exécute tous...
        resultats = []
        for bloc in reponse.content:
            if bloc.type == "tool_use":
                print(f"  🔧 {bloc.name}({bloc.input})")
                resultats.append(
                    {"type": "tool_result", "tool_use_id": bloc.id, **executer_outil(bloc.name, bloc.input)}
                )
        # ...et on lui renvoie tous les résultats en un seul message.
        messages.append({"role": "user", "content": resultats})


def main():
    client = anthropic.Anthropic()  # lit la clé dans la variable ANTHROPIC_API_KEY
    messages = []
    print("Agent prêt ! Pose ta question (ou tape « quitter »).\n")
    while True:
        question = input("Toi > ").strip()
        if question.lower() in {"quitter", "exit", "q"}:
            break
        if not question:
            continue
        messages.append({"role": "user", "content": question})
        print(f"Agent > {tour_agent(client, messages)}\n")


if __name__ == "__main__":
    main()
