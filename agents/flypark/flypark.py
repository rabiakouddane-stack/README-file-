"""FlyPark : ton équipe d'agents IA, en ligne de commande.

  python flypark.py                     discuter avec le responsable de l'équipe
  python flypark.py decisions           voir les décisions qui attendent ton accord
  python flypark.py valider D001 [note] valider une décision
  python flypark.py refuser D001 [motif] refuser une décision
  python flypark.py controle [AAAA-MM-JJ]   contrôle caméra + alertes (sans IA, à lancer souvent)
  python flypark.py import              importer les réservations du site et des plateformes
  python flypark.py caisse [AAAA-MM-JJ] rapprochement voitures / paiements / reçus (sans IA)
  python flypark.py export AAAA-MM      préparer l'export du mois pour le comptable
  python flypark.py tache "demande"     confier une tâche à l'équipe sans discuter (pour l'automatique) ;
                                        le compte rendu est enregistré dans rapports/
"""

import json
import sys

import donnees_flypark as d


def afficher_decisions():
    decisions = d.lister_decisions("en attente")
    if not decisions:
        print("Aucune décision en attente.")
    for x in decisions:
        montant = f" — {x['montant']} €" if x.get("montant") is not None else ""
        print(f"\n[{x['id']}] {x['type'].upper()}{montant} (proposé par {x['agent']}, {x['proposee_le']})")
        print(f"  {x['resume']}\n  {x['details']}")


def discuter():
    from equipe import Responsable

    responsable = Responsable()
    print("Équipe FlyPark prête. Exemples : « Fais le point du jour », « Relève les prix des concurrents "
          "pour 7 jours », « Traite les messages clients ». Tape « quitter » pour sortir.\n")
    while True:
        try:
            demande = input("Gérant > ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if demande.lower() in {"quitter", "exit", "q"}:
            break
        if demande:
            print(f"\nResponsable > {responsable.demander(demande)}\n")


def main(args):
    commande = args[0] if args else "discuter"
    reste = args[1:]
    if commande == "discuter":
        discuter()
    elif commande == "decisions":
        afficher_decisions()
    elif commande in {"valider", "refuser"} and reste:
        statut = "validée" if commande == "valider" else "refusée"
        print(d.trancher_decision(reste[0], statut, " ".join(reste[1:])))
        print("Rappel : l'action elle-même (remboursement, publication…) reste à faire par toi "
              "tant qu'elle n'est pas branchée à un outil.")
    elif commande == "controle":
        print(d.controle_et_alertes(reste[0] if reste else None))
    elif commande == "import":
        print(d.importer_reservations())
    elif commande == "caisse":
        print(json.dumps(d.rapprochement_jour(reste[0] if reste else None), ensure_ascii=False, indent=2))
    elif commande == "tache" and reste:
        from datetime import datetime
        from equipe import Responsable

        demande = " ".join(reste)
        compte_rendu = Responsable().demander(demande)
        print(compte_rendu)
        print(d.enregistrer_document("rapports", demande[:40],
                                     f"# {demande}\n\n{datetime.now():%Y-%m-%d %H:%M}\n\n{compte_rendu}\n"))
    elif commande == "export" and reste:
        print(d.export_mois(reste[0]))
    else:
        print(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
