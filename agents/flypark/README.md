# FlyPark — l'équipe d'agents IA

Une équipe de 8 agents IA (un responsable et 7 spécialistes) pour gérer le parking.
**Règle d'or : les agents proposent, toi seul décides.** Aucun agent ne peut rembourser,
publier, envoyer, dépenser ou changer un prix : il ajoute une *décision* dans ta file,
que tu valides ou refuses.

```
                         Toi, le gérant
             (valide tout · reçoit les alertes directement)
                               │
                     Responsable de l'équipe
        (répartit le travail · vérifie le plan · fait la synthèse)
   ┌─────────┬─────────┬────────┼────────┬──────────┬──────────┐
Stratégie Marketing  Ventes  Contenu  Support  Contrôle   Compta
 & veille           & parten.         & litiges caméra    & caisse
```

| Agent | Ce qu'il fait | Ce qu'il ne fait jamais seul |
|---|---|---|
| **Responsable** | Choisit les agents, leur répartit le travail (en parallèle), vérifie le plan, fait la synthèse | — |
| **Stratégie & veille** | Relève les prix des concurrents et sur les plateformes (Allopark, Parkmundo, Free2Move…), propose un prix (ex. −1 €), étudie click & collect, stockage, gardiennage | Changer un prix |
| **Marketing** | Prépare les campagnes Google, Instagram, Facebook, TikTok et l'emailing | Publier, dépenser, envoyer |
| **Ventes & partenaires** | Suit les demandes d'API, calcule le revenu net par plateforme, prépare les offres pros | Envoyer une offre |
| **Contenu** | Rédige affiches, posts, FAQ, pages du site (brouillons) | Publier |
| **Support & litiges** | Lit emails et WhatsApp, applique ta politique, propose « rembourser X € » ou « refuser, motif », prépare les dossiers Stripe | Rembourser, répondre |
| **Contrôle** | Importe les réservations dans FlyPark, compare plaques / réservations / paiements, t'alerte | — |
| **Compta & caisse** | Rapprochement voitures / paiements / reçus, écarts d'espèces par employé, export du mois | Accuser quelqu'un (il donne des faits) |

Les contrôles (caméra, caisse, export) sont calculés **sans IA**, par du code exact :
l'IA ne sert qu'à expliquer, rédiger et proposer.

## Installation

```bash
pip install -r ../requirements.txt
export ANTHROPIC_API_KEY="ta-clé"      # clé créée sur console.anthropic.com (payant à l'usage)
cd agents/flypark
```

## Utilisation

| Commande | Rôle |
|---|---|
| `python flypark.py` | Discuter avec le responsable (« Fais le point du jour », « Relève les prix 7 jours », « Traite les messages clients ») |
| `python flypark.py decisions` | Voir les décisions qui attendent ton accord |
| `python flypark.py valider D001` / `refuser D001 motif` | Trancher une décision |
| `python flypark.py controle` | Contrôle caméra + alertes, sans IA (à lancer automatiquement toutes les 5 min) |
| `python flypark.py import` | Faire entrer dans FlyPark les réservations du site et des plateformes |
| `python flypark.py caisse 2026-11-16` | Rapprochement de la journée, sans IA |
| `python flypark.py export 2026-11` | Export du mois pour le comptable |

Les brouillons arrivent dans `brouillons/`, les dossiers de litige dans `dossiers/`,
les alertes dans `alertes.log` et l'écran.

## À personnaliser

- `plan.md` : tes objectifs (prix plancher, budget…). Le responsable vérifie tout avec.
- `politique.md` : ta politique d'annulation et de remboursement.
- `config.json` : tes tarifs, l'écart de prix voulu, tes plateformes et leurs commissions.
- `donnees/` : **données d'exemple** à remplacer par les vraies.

## Ce qui reste à brancher

Pour l'instant, les agents lisent des fichiers dans `donnees/`. Chaque branchement
se fait à un seul endroit, dans `donnees_flypark.py` :

| Source réelle | Fichier actuel | À brancher |
|---|---|---|
| Caméra de lecture de plaques | `passages_camera.csv` | export ou API de la caméra |
| Paiements | `paiements.csv` | Stripe + saisie caisse |
| Réservations site / plateformes | `reservations.csv`, `entrant/` | API FlyPark et plateformes |
| Emails / WhatsApp | `messages.json` | boîte mail, WhatsApp Business |
| Alertes | écran + `alertes.log` | SMS / WhatsApp vers ton téléphone |

Même une fois branché, valider une décision ne fait que la marquer « validée » :
c'est toi qui fais le remboursement ou la publication, sauf si tu choisis plus tard
de brancher cette action-là aussi.
