"""Données, contrôles et file des décisions de FlyPark.

Tout ce fichier est du code « classique », sans IA : les comparaisons (caméra,
paiements, reçus, caisse) doivent être exactes, donc elles sont calculées ici.
Les agents IA s'en servent comme d'outils, puis expliquent les résultats.
"""

import csv
import json
import shutil
import threading
from collections import defaultdict
from datetime import date, datetime
from pathlib import Path

DOSSIER = Path(__file__).resolve().parent
DONNEES = DOSSIER / "donnees"
FICHIER_DECISIONS = DOSSIER / "decisions.json"
FICHIER_ALERTES = DOSSIER / "alertes.log"
_verrou = threading.Lock()


# --- Lecture des fichiers ---------------------------------------------------

def lire_csv(nom: str) -> list[dict]:
    chemin = DONNEES / nom
    if not chemin.exists():
        return []
    with chemin.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def config() -> dict:
    return json.loads((DOSSIER / "config.json").read_text(encoding="utf-8"))


def lire_texte(nom: str) -> str:
    return (DOSSIER / nom).read_text(encoding="utf-8")


def normaliser_plaque(plaque: str) -> str:
    return "".join(c for c in plaque.upper() if c.isalnum())


def _montant(valeur) -> float:
    try:
        return float(str(valeur).replace(",", "."))
    except ValueError:
        return 0.0


# --- Alertes au gérant ------------------------------------------------------

def alerter_gerant(message: str, niveau: str = "important") -> str:
    """Envoie une alerte au gérant (pour l'instant : écran + fichier alertes.log).

    C'est ici qu'on branchera plus tard un SMS, un WhatsApp ou une notification.
    """
    ligne = f"{datetime.now():%Y-%m-%d %H:%M} [{niveau.upper()}] {message}"
    with _verrou, FICHIER_ALERTES.open("a", encoding="utf-8") as f:
        f.write(ligne + "\n")
    print(f"\a🚨 ALERTE : {ligne}")
    return "Alerte envoyée au gérant."


# --- File des décisions (rien ne s'exécute sans le gérant) ------------------

def _charger_decisions() -> list[dict]:
    if not FICHIER_DECISIONS.exists():
        return []
    return json.loads(FICHIER_DECISIONS.read_text(encoding="utf-8"))


def _sauver_decisions(decisions: list[dict]) -> None:
    FICHIER_DECISIONS.write_text(json.dumps(decisions, ensure_ascii=False, indent=2), encoding="utf-8")


def proposer_decision(agent: str, type_decision: str, resume: str, details: str, montant: float | None = None) -> str:
    with _verrou:
        decisions = _charger_decisions()
        identifiant = f"D{len(decisions) + 1:03d}"
        decisions.append({
            "id": identifiant, "agent": agent, "type": type_decision, "resume": resume,
            "details": details, "montant": montant, "statut": "en attente",
            "proposee_le": f"{datetime.now():%Y-%m-%d %H:%M}", "commentaire_gerant": "",
        })
        _sauver_decisions(decisions)
    return f"Décision {identifiant} ajoutée : elle attend la validation du gérant. Rien n'a été exécuté."


def lister_decisions(statut: str = "en attente") -> list[dict]:
    return [d for d in _charger_decisions() if statut == "toutes" or d["statut"] == statut]


def trancher_decision(identifiant: str, statut: str, commentaire: str = "") -> str:
    """Réservé au gérant (appelé depuis la ligne de commande, jamais par un agent)."""
    with _verrou:
        decisions = _charger_decisions()
        for d in decisions:
            if d["id"] == identifiant:
                d["statut"], d["commentaire_gerant"] = statut, commentaire
                d["tranchee_le"] = f"{datetime.now():%Y-%m-%d %H:%M}"
                _sauver_decisions(decisions)
                return f"{identifiant} : {statut}."
    return f"Décision {identifiant} introuvable."


# --- Réservations -----------------------------------------------------------

def chercher_reservation(recherche: str) -> list[dict]:
    r = recherche.lower()
    plaque = normaliser_plaque(recherche)
    return [
        res for res in lire_csv("reservations.csv")
        if r in (res["id"].lower(), res["email"].lower())
        or r in res["client"].lower()
        or (plaque and normaliser_plaque(res["plaque"]) == plaque)
    ]


def importer_reservations() -> str:
    """Fait entrer dans FlyPark les réservations déposées dans donnees/entrant/.

    Chaque plateforme (ou le site) dépose un CSV avec les mêmes colonnes que
    reservations.csv. Les doublons (même id) sont ignorés.
    """
    entrant = DONNEES / "entrant"
    fichiers = sorted(entrant.glob("*.csv"))
    if not fichiers:
        return "Aucune nouvelle réservation à importer."
    existantes = lire_csv("reservations.csv")
    colonnes = list(existantes[0].keys()) if existantes else [
        "id", "plaque", "client", "email", "source", "date_arrivee", "date_depart", "montant", "statut"]
    ids = {r["id"] for r in existantes}
    ajoutees = 0
    (entrant / "traites").mkdir(exist_ok=True)
    with _verrou:
        with (DONNEES / "reservations.csv").open("a", encoding="utf-8", newline="") as sortie:
            ecrivain = csv.DictWriter(sortie, fieldnames=colonnes, extrasaction="ignore")
            for fichier in fichiers:
                with fichier.open(encoding="utf-8", newline="") as f:
                    for ligne in csv.DictReader(f):
                        if ligne.get("id") and ligne["id"] not in ids:
                            ecrivain.writerow(ligne)
                            ids.add(ligne["id"])
                            ajoutees += 1
                shutil.move(str(fichier), entrant / "traites" / fichier.name)
    return f"{ajoutees} réservation(s) importée(s) depuis {len(fichiers)} fichier(s)."


# --- Contrôle caméra --------------------------------------------------------

def verifier_entrees(jour: str | None = None) -> list[dict]:
    """Compare les voitures vues à l'entrée avec les réservations et les paiements."""
    jour = jour or date.today().isoformat()
    reservations = [r for r in lire_csv("reservations.csv") if r["statut"] != "annulée"]
    paiements = lire_csv("paiements.csv")
    payees_resa = {p["reservation_id"] for p in paiements if p["reservation_id"]}
    payees_plaque = {normaliser_plaque(p["plaque"]) for p in paiements if p["date"] == jour}

    anomalies = []
    for passage in lire_csv("passages_camera.csv"):
        if passage["sens"] != "entree" or not passage["horodatage"].startswith(jour):
            continue
        plaque = normaliser_plaque(passage["plaque"])
        resa = next((r for r in reservations if normaliser_plaque(r["plaque"]) == plaque
                     and r["date_arrivee"] <= jour <= r["date_depart"]), None)
        if resa and resa["id"] in payees_resa:
            continue
        if not resa and plaque in payees_plaque:
            continue  # client sur place, payé au guichet
        anomalies.append({
            "horodatage": passage["horodatage"], "plaque": passage["plaque"],
            "confiance_lecture": passage["confiance"],
            "probleme": "réservation non payée" if resa else "aucune réservation ni paiement",
            "reservation": resa["id"] if resa else None,
        })
    return anomalies


def controle_et_alertes(jour: str | None = None) -> str:
    anomalies = verifier_entrees(jour)
    for a in anomalies:
        alerter_gerant(f"Voiture {a['plaque']} entrée à {a['horodatage']} : {a['probleme']} "
                       f"(lecture caméra {a['confiance_lecture']}).")
    return f"{len(anomalies)} anomalie(s) détectée(s)."


# --- Compta & caisse --------------------------------------------------------

def rapprochement_jour(jour: str | None = None) -> dict:
    """Compare voitures, paiements et reçus d'une journée. Donne des faits, pas de jugement."""
    jour = jour or date.today().isoformat()
    entrees = [p for p in lire_csv("passages_camera.csv")
               if p["sens"] == "entree" and p["horodatage"].startswith(jour)]
    paiements = [p for p in lire_csv("paiements.csv") if p["date"] == jour]
    recus = {r["id"]: r for r in lire_csv("recus.csv") if r["date"] == jour}

    par_employe = defaultdict(lambda: {"especes_encaissees": 0.0, "especes_avec_recu": 0.0,
                                       "paiements_sans_recu": []})
    for p in paiements:
        if p["moyen"] != "especes":
            continue
        e = par_employe[p["employe"] or "inconnu"]
        e["especes_encaissees"] += _montant(p["montant"])
        if p["recu_id"] and p["recu_id"] in recus:
            e["especes_avec_recu"] += _montant(recus[p["recu_id"]]["montant"])
        else:
            e["paiements_sans_recu"].append({"paiement": p["id"], "plaque": p["plaque"], "montant": p["montant"]})
    for e in par_employe.values():
        e["ecart"] = round(e["especes_encaissees"] - e["especes_avec_recu"], 2)

    return {
        "jour": jour,
        "voitures_entrees": len(entrees),
        "paiements": len(paiements),
        "total_encaisse": sum(_montant(p["montant"]) for p in paiements),
        "recus_emis": len(recus),
        "entrees_sans_paiement": verifier_entrees(jour),
        "especes_par_employe": dict(par_employe),
        "rappel": "Ce sont des faits. Un écart peut avoir une explication (oubli, erreur de saisie, panne).",
    }


def export_mois(mois: str) -> str:
    """Prépare l'export du mois (AAAA-MM) pour le comptable."""
    paiements = [p for p in lire_csv("paiements.csv") if p["date"].startswith(mois)]
    dossier = DOSSIER / "exports"
    dossier.mkdir(exist_ok=True)
    chemin = dossier / f"compta-{mois}.csv"
    with chemin.open("w", encoding="utf-8", newline="") as f:
        colonnes = ["id", "reservation_id", "plaque", "date", "montant", "moyen", "employe", "recu_id"]
        ecrivain = csv.DictWriter(f, fieldnames=colonnes, extrasaction="ignore")
        ecrivain.writeheader()
        ecrivain.writerows(paiements)
    totaux = defaultdict(float)
    for p in paiements:
        totaux[p["moyen"]] += _montant(p["montant"])
    return f"Export écrit dans {chemin.relative_to(DOSSIER)} — {len(paiements)} paiements, totaux : {dict(totaux)}"


# --- Stratégie & ventes -----------------------------------------------------

def enregistrer_prix_concurrent(concurrent: str, duree_jours: int, prix: float, source: str) -> str:
    with _verrou, (DONNEES / "prix_concurrents.csv").open("a", encoding="utf-8", newline="") as f:
        csv.writer(f).writerow([date.today().isoformat(), concurrent, duree_jours, prix, source])
    return f"Prix enregistré : {concurrent}, {duree_jours} j, {prix} €."


def comparer_prix(duree_jours: int) -> dict:
    """Dernier prix connu de chaque concurrent pour une durée, et le prix suggéré par ta règle."""
    derniers = {}
    for ligne in lire_csv("prix_concurrents.csv"):
        if int(ligne["duree_jours"]) == duree_jours:
            if ligne["concurrent"] not in derniers or ligne["date"] >= derniers[ligne["concurrent"]]["date"]:
                derniers[ligne["concurrent"]] = ligne
    cfg = config()
    actuel = cfg["tarifs_flypark"].get(str(duree_jours))
    if not derniers:
        return {"duree_jours": duree_jours, "prix_actuel_flypark": actuel, "concurrents": {}, "suggestion": None}
    moins_cher = min(derniers.values(), key=lambda l: _montant(l["prix"]))
    return {
        "duree_jours": duree_jours,
        "prix_actuel_flypark": actuel,
        "concurrents": {c: {"prix": _montant(l["prix"]), "releve_le": l["date"]} for c, l in derniers.items()},
        "moins_cher": moins_cher["concurrent"],
        "suggestion": _montant(moins_cher["prix"]) - cfg["ecart_prix_euros"],
    }


def revenu_net_plateformes(mois: str | None = None) -> dict:
    """Ce que rapporte chaque canal une fois la commission retirée."""
    commissions = {p["nom"]: p for p in config()["plateformes"]}
    resultat = defaultdict(lambda: {"reservations": 0, "brut": 0.0, "commission": 0.0, "net": 0.0})
    for r in lire_csv("reservations.csv"):
        if r["statut"] == "annulée" or (mois and not r["date_arrivee"].startswith(mois)):
            continue
        p = commissions.get(r["source"], {"commission_pct": None, "frais_fixes": 0})
        brut = _montant(r["montant"])
        commission = brut * (p["commission_pct"] or 0) / 100 + p.get("frais_fixes", 0)
        ligne = resultat[r["source"]]
        ligne["reservations"] += 1
        ligne["brut"] += brut
        ligne["commission"] += round(commission, 2)
        ligne["net"] += round(brut - commission, 2)
        if p["commission_pct"] is None:
            ligne["attention"] = "commission inconnue : ajoute cette plateforme dans config.json"
    return dict(resultat)


# --- Support ----------------------------------------------------------------

def lire_messages() -> list[dict]:
    """Emails et WhatsApp reçus (pour l'instant : donnees/messages.json)."""
    chemin = DONNEES / "messages.json"
    return json.loads(chemin.read_text(encoding="utf-8")) if chemin.exists() else []


def enregistrer_document(dossier: str, titre: str, contenu: str) -> str:
    """Enregistre un brouillon ou un dossier (jamais publié automatiquement)."""
    cible = DOSSIER / dossier
    cible.mkdir(exist_ok=True)
    nom = "".join(c if c.isalnum() or c in "-_" else "-" for c in titre.lower())[:60] or "document"
    chemin = cible / f"{date.today().isoformat()}-{nom}.md"
    chemin.write_text(contenu, encoding="utf-8")
    return f"Enregistré dans {chemin.relative_to(DOSSIER)} (brouillon : rien n'est publié ni envoyé)."
