"""L'équipe d'agents IA de FlyPark : un responsable et 7 spécialistes.

Le responsable reçoit tes demandes, confie le travail aux bons spécialistes
(en parallèle si possible), vérifie que tout colle avec ton plan, puis te
présente une synthèse et la liste des décisions à prendre.

Règle d'or : aucun agent ne rembourse, ne publie, n'envoie, ne dépense ni ne
change un prix. Ils PROPOSENT des décisions, que toi seul valides.
"""

import json
from concurrent.futures import ThreadPoolExecutor

import anthropic

import donnees_flypark as d

MODELE = "claude-opus-5-5"

REGLES_COMMUNES = """
Tu fais partie de l'équipe d'agents IA de FlyPark, un parking près de l'aéroport.
Le gérant décide de tout. Règles absolues :
- Tu ne rembourses jamais, tu ne publies rien, tu n'envoies rien, tu ne dépenses rien,
  tu ne changes aucun prix. Pour tout cela, tu utilises l'outil proposer_decision
  et c'est le gérant qui valide.
- Tu t'appuies sur les outils et les données. Si une information manque, dis-le
  au lieu de l'inventer.
- Réponds en français, de façon claire et concise, avec les chiffres utiles.
"""


# ---------------------------------------------------------------------------
# Les outils : description pour Claude + fonction Python correspondante
# ---------------------------------------------------------------------------

def _outil(nom, description, **params):
    """params : nom=(type, description) ; préfixer le type par '?' s'il est facultatif."""
    proprietes, requis = {}, []
    for p, (typ, desc) in params.items():
        if not typ.startswith("?"):
            requis.append(p)
        proprietes[p] = {"type": typ.lstrip("?"), "description": desc}
    return {"name": nom, "description": description,
            "input_schema": {"type": "object", "properties": proprietes, "required": requis}}


def _json(objet):
    return json.dumps(objet, ensure_ascii=False, indent=1)


OUTILS = {
    "proposer_decision": (
        _outil("proposer_decision",
               "Ajoute une décision dans la file du gérant (remboursement, prix, publication, envoi, "
               "dépense, offre…). C'est la SEULE façon de faire agir FlyPark : le gérant valide ou refuse.",
               type_decision=("string", "remboursement, refus, prix, publication, envoi, dépense, offre, autre"),
               resume=("string", "Une phrase, ex. « Rembourser 31 € à client4 (R004) »."),
               details=("string", "Justification, règle appliquée, chiffres, texte proposé."),
               montant=("?number", "Montant en euros si la décision en a un.")),
        None,  # rempli plus bas : on a besoin du nom de l'agent
    ),
    "alerter_gerant": (
        _outil("alerter_gerant", "Envoie immédiatement une alerte au gérant (ex. voiture entrée sans paiement).",
               message=("string", "Le message d'alerte, avec plaque et heure."),
               niveau=("?string", "« urgent », « important » ou « info ».")),
        lambda message, niveau="important": d.alerter_gerant(message, niveau),
    ),
    "lire_plan": (
        _outil("lire_plan", "Lit le plan et les objectifs du gérant."),
        lambda: d.lire_texte("plan.md"),
    ),
    "lire_config": (
        _outil("lire_config", "Lit la configuration : concurrents, tarifs FlyPark, plateformes et commissions."),
        lambda: _json(d.config()),
    ),
    "comparer_prix": (
        _outil("comparer_prix", "Derniers prix relevés chez chaque concurrent pour une durée, prix actuel "
               "de FlyPark et prix suggéré par la règle du gérant (moins cher − écart).",
               duree_jours=("integer", "Durée du séjour en jours, ex. 7.")),
        lambda duree_jours: _json(d.comparer_prix(int(duree_jours))),
    ),
    "enregistrer_prix_concurrent": (
        _outil("enregistrer_prix_concurrent", "Enregistre un prix relevé chez un concurrent.",
               concurrent=("string", "Nom du concurrent."), duree_jours=("integer", "Durée en jours."),
               prix=("number", "Prix en euros TTC."), source=("string", "D'où vient le prix (URL, appel…).")),
        lambda concurrent, duree_jours, prix, source: d.enregistrer_prix_concurrent(concurrent, int(duree_jours), prix, source),
    ),
    "revenu_net_plateformes": (
        _outil("revenu_net_plateformes", "Ce que rapporte chaque canal (site, plateformes) une fois la commission retirée.",
               mois=("?string", "Mois au format AAAA-MM. Vide = tout.")),
        lambda mois=None: _json(d.revenu_net_plateformes(mois)),
    ),
    "chercher_reservation": (
        _outil("chercher_reservation", "Cherche une réservation par numéro, plaque, nom ou email.",
               recherche=("string", "Numéro, plaque, nom ou email.")),
        lambda recherche: _json(d.chercher_reservation(recherche)),
    ),
    "lire_messages": (
        _outil("lire_messages", "Lit les emails et messages WhatsApp reçus des clients."),
        lambda: _json(d.lire_messages()),
    ),
    "lire_politique": (
        _outil("lire_politique", "Lit la politique d'annulation et de remboursement du gérant."),
        lambda: d.lire_texte("politique.md"),
    ),
    "enregistrer_brouillon": (
        _outil("enregistrer_brouillon", "Enregistre un brouillon (post, campagne, email, affiche, page, FAQ, offre). "
               "Rien n'est publié : le gérant relit.",
               titre=("string", "Titre court."), contenu=("string", "Le texte complet, en Markdown.")),
        lambda titre, contenu: d.enregistrer_document("brouillons", titre, contenu),
    ),
    "preparer_dossier_litige": (
        _outil("preparer_dossier_litige", "Enregistre un dossier de litige ou de contestation bancaire Stripe "
               "(faits, chronologie, preuves disponibles, réponse proposée).",
               titre=("string", "Ex. « litige R004 »."), contenu=("string", "Le dossier complet, en Markdown.")),
        lambda titre, contenu: d.enregistrer_document("dossiers", titre, contenu),
    ),
    "verifier_entrees": (
        _outil("verifier_entrees", "Compare les plaques lues par la caméra avec les réservations et paiements.",
               jour=("?string", "Date AAAA-MM-JJ. Vide = aujourd'hui.")),
        lambda jour=None: _json(d.verifier_entrees(jour)),
    ),
    "importer_reservations": (
        _outil("importer_reservations", "Fait entrer dans FlyPark les réservations reçues du site et des plateformes."),
        d.importer_reservations,
    ),
    "rapprochement_jour": (
        _outil("rapprochement_jour", "Compare voitures, paiements, reçus et espèces par employé pour une journée.",
               jour=("?string", "Date AAAA-MM-JJ. Vide = aujourd'hui.")),
        lambda jour=None: _json(d.rapprochement_jour(jour)),
    ),
    "export_mois": (
        _outil("export_mois", "Prépare le fichier du mois pour le comptable.", mois=("string", "Mois AAAA-MM.")),
        d.export_mois,
    ),
    "decisions_en_attente": (
        _outil("decisions_en_attente", "Liste les décisions qui attendent la validation du gérant."),
        lambda: _json(d.lister_decisions("en attente")),
    ),
}

RECHERCHE_WEB = {"type": "web_search_20260209", "name": "web_search", "max_uses": 10}


# ---------------------------------------------------------------------------
# Les 7 spécialistes
# ---------------------------------------------------------------------------

SPECIALISTES = {
    "strategie": {
        "titre": "Stratégie & veille",
        "consignes": """Tu es l'agent Stratégie & veille.
- Relève les prix des concurrents (Tilt, JT Parking, Air Parking, Aeropark 60, P1 à P4, particuliers)
  avec la recherche web quand c'est possible, et enregistre chaque prix trouvé avec sa source.
  Si un prix n'est pas trouvable en ligne, dis-le clairement.
- Compare avec comparer_prix et propose un nouveau prix au gérant via proposer_decision
  (règle par défaut : 1 € de moins que le moins cher comparable), en vérifiant que ça respecte le plan.
- Étudie les nouveaux revenus (click & collect, stockage, gardiennage) : idée, clients visés,
  prix possible, coûts, risques, première étape simple.""",
        "outils": ["comparer_prix", "enregistrer_prix_concurrent", "lire_config", "lire_plan",
                   "proposer_decision", "enregistrer_brouillon"],
        "web": True,
    },
    "marketing": {
        "titre": "Marketing",
        "consignes": """Tu es l'agent Marketing.
- Prépare les campagnes Google Ads, Instagram, Facebook et TikTok : objectif, cible, textes,
  idées de visuels, budget proposé (dans la limite du plan), durée.
- Prépare l'emailing aux anciens clients (objet, texte, offre).
- Enregistre chaque campagne en brouillon, puis crée une décision « dépense » ou « envoi »
  pour que le gérant valide. Tu ne publies et ne dépenses jamais rien toi-même.""",
        "outils": ["lire_plan", "lire_config", "enregistrer_brouillon", "proposer_decision"],
        "web": False,
    },
    "ventes": {
        "titre": "Ventes & partenaires",
        "consignes": """Tu es l'agent Ventes & partenaires.
- Suis l'état des demandes d'API auprès des plateformes (dans la config) et propose des relances.
- Calcule ce que rapporte chaque plateforme une fois la commission retirée, et compare au site.
- Prépare des offres pour les pros (agences de voyage, loueurs, entreprises) : tarif, conditions,
  arguments. Enregistre-les en brouillon ; tout envoi passe par proposer_decision.""",
        "outils": ["lire_config", "revenu_net_plateformes", "lire_plan", "enregistrer_brouillon", "proposer_decision"],
        "web": False,
    },
    "contenu": {
        "titre": "Contenu",
        "consignes": """Tu es l'agent Contenu.
- Rédige les affiches (« Exigez votre reçu », information sur la caméra de vidéoprotection
  avec les mentions d'information obligatoires à faire vérifier par le gérant).
- Écris les posts, la FAQ et les pages du site, dans un ton simple et rassurant.
- Tout est enregistré en brouillon ; pour publier, crée une décision « publication ».""",
        "outils": ["lire_config", "lire_politique", "lire_plan", "enregistrer_brouillon", "proposer_decision"],
        "web": False,
    },
    "support": {
        "titre": "Support, réservations & litiges",
        "consignes": """Tu es l'agent Support, réservations & litiges.
- Lis les emails et WhatsApp, retrouve la réservation concernée, et prépare une réponse.
- Applique la politique d'annulation et de remboursement À LA LETTRE, en citant la règle utilisée.
- Pour chaque demande d'argent, crée une décision : « rembourser X € » ou « refuser, motif : … »,
  avec le brouillon de réponse au client dans les détails.
- Prépare les dossiers de litige et de contestation bancaire Stripe (faits, chronologie, preuves).
- Tu ne rembourses JAMAIS seul et tu n'envoies aucune réponse toi-même.""",
        "outils": ["lire_messages", "chercher_reservation", "lire_politique", "preparer_dossier_litige",
                   "proposer_decision"],
        "web": False,
    },
    "controle": {
        "titre": "Automatisation & contrôle",
        "consignes": """Tu es l'agent Automatisation & contrôle.
- Importe les réservations du site et des plateformes dans FlyPark.
- Vérifie les entrées vues par la caméra contre les réservations et les paiements.
- Pour chaque voiture entrée sans paiement, envoie une alerte au gérant (plaque, heure, problème).
  Signale aussi quand la lecture de la plaque est peu fiable (confiance < 0,9).""",
        "outils": ["importer_reservations", "verifier_entrees", "chercher_reservation", "alerter_gerant"],
        "web": False,
    },
    "compta": {
        "titre": "Compta & caisse",
        "consignes": """Tu es l'agent Compta & caisse.
- Compare chaque jour voitures, paiements et reçus avec rapprochement_jour.
- Repère les écarts d'espèces par employé et présente-les comme des FAITS, avec les explications
  possibles (oubli de reçu, erreur de saisie…). Tu n'accuses JAMAIS personne : c'est le gérant qui décide.
- Prépare l'export du mois pour le comptable.""",
        "outils": ["rapprochement_jour", "export_mois", "chercher_reservation"],
        "web": False,
    },
}

CONSIGNES_RESPONSABLE = REGLES_COMMUNES + """
Tu es le RESPONSABLE de l'équipe. Tu ne fais pas le travail toi-même : tu le confies.
1. Reçois la demande du gérant et choisis le ou les bons spécialistes :
   """ + "\n   ".join(f"- {k} : {v['titre']}" for k, v in SPECIALISTES.items()) + """
2. Confie à chacun une tâche précise avec l'outil deleguer. Quand plusieurs tâches sont
   indépendantes, délègue-les toutes dans la même réponse pour qu'elles avancent en parallèle.
3. Lis le plan du gérant et vérifie que les propositions le respectent (prix plancher, budget…).
   Si quelque chose ne colle pas, dis-le ou redemande au spécialiste.
4. Termine par une synthèse courte :
   - ce qui a été fait ;
   - les ALERTES éventuelles ;
   - les DÉCISIONS À PRENDRE (numéro, résumé, montant), en rappelant qu'elles se valident avec
     « python flypark.py valider <numéro> » ou « refuser <numéro> ».
"""


# ---------------------------------------------------------------------------
# Le moteur : la boucle d'un agent
# ---------------------------------------------------------------------------

def _appeler_claude(client, consignes, outils, messages):
    return client.beta.messages.create(
        model=MODELE,
        max_tokens=16000,
        system=consignes,
        tools=outils,
        messages=messages,
        thinking={"type": "adaptive"},
        output_config={"effort": "medium"},
        # Si le modèle décline une demande, l'API réessaie avec un autre modèle.
        betas=["server-side-fallback-2026-07-01"],
        fallbacks="default",
    )


def faire_travailler(client, consignes, outils, fonctions, messages, nom="agent", retrait=""):
    """Boucle d'agent : Claude répond ou demande des outils, jusqu'à la réponse finale."""
    while True:
        reponse = _appeler_claude(client, consignes, outils, messages)
        messages.append({"role": "assistant", "content": reponse.content})

        if reponse.stop_reason == "refusal":
            return f"({nom} n'a pas pu traiter cette demande.)"
        if reponse.stop_reason == "pause_turn":  # recherche web longue : on laisse continuer
            continue
        if reponse.stop_reason != "tool_use":
            return "".join(b.text for b in reponse.content if b.type == "text")

        appels = [b for b in reponse.content if b.type == "tool_use"]
        for b in appels:
            apercu = ", ".join(f"{k}={str(v)[:50]!r}" for k, v in b.input.items())
            print(f"{retrait}🔧 {nom} → {b.name}({apercu})")

        def executer(bloc):
            try:
                return {"type": "tool_result", "tool_use_id": bloc.id, "content": str(fonctions[bloc.name](**bloc.input))}
            except Exception as erreur:
                return {"type": "tool_result", "tool_use_id": bloc.id, "content": f"Erreur : {erreur}", "is_error": True}

        # Les outils demandés ensemble tournent en parallèle ; tous les résultats repartent ensemble.
        with ThreadPoolExecutor() as pool:
            resultats = list(pool.map(executer, appels))
        messages.append({"role": "user", "content": resultats})


def _construire(nom_agent, noms_outils, web=False):
    outils, fonctions = [], {}
    for n in noms_outils:
        schema, fonction = OUTILS[n]
        if n == "proposer_decision":
            fonction = lambda type_decision, resume, details, montant=None: d.proposer_decision(
                nom_agent, type_decision, resume, details, montant)
        outils.append(schema)
        fonctions[n] = fonction
    if web:
        outils.append(RECHERCHE_WEB)
    return outils, fonctions


def lancer_specialiste(client, nom, tache):
    agent = SPECIALISTES[nom]
    outils, fonctions = _construire(nom, agent["outils"], agent["web"])
    print(f"  ▶ {agent['titre']} : {tache[:90]}")
    return faire_travailler(client, REGLES_COMMUNES + agent["consignes"], outils, fonctions,
                            [{"role": "user", "content": tache}], nom=agent["titre"], retrait="    ")


class Responsable:
    """Le chef d'équipe, avec qui le gérant discute. Il garde la mémoire de la conversation."""

    def __init__(self, client=None):
        self.client = client or anthropic.Anthropic()
        self.messages = []
        outil_deleguer = {
            "name": "deleguer",
            "description": "Confie une tâche à un spécialiste et renvoie son compte rendu.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "agent": {"type": "string", "enum": list(SPECIALISTES), "description": "Le spécialiste."},
                    "tache": {"type": "string", "description": "Tâche précise, avec tout le contexte utile "
                              "(le spécialiste ne voit pas la conversation)."},
                },
                "required": ["agent", "tache"],
            },
        }
        self.outils, self.fonctions = _construire("responsable", ["lire_plan", "decisions_en_attente"])
        self.outils.append(outil_deleguer)
        self.fonctions["deleguer"] = lambda agent, tache: lancer_specialiste(self.client, agent, tache)

    def demander(self, demande: str) -> str:
        self.messages.append({"role": "user", "content": demande})
        return faire_travailler(self.client, CONSIGNES_RESPONSABLE, self.outils, self.fonctions,
                                self.messages, nom="Responsable")
