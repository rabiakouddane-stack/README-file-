# Agents IA

Ce dossier contient :

- `assistant.py` : un premier agent simple, pour comprendre le principe ;
- `flypark/` : **l'équipe d'agents de FlyPark** (responsable + 7 spécialistes), voir `flypark/README.md`.

## C'est quoi, un agent IA ?

Un agent, c'est un modèle d'IA qui peut **utiliser des outils** (des fonctions
Python) pour accomplir une tâche. Il fonctionne en boucle :

1. il reçoit ta question ;
2. il décide s'il a besoin d'un outil (calculatrice, lecture de fichier…) ;
3. le programme exécute l'outil et lui renvoie le résultat ;
4. il recommence jusqu'à pouvoir te donner une réponse finale.

## L'agent `assistant.py`

Un assistant en français qui sait :

| Outil             | Ce qu'il fait                                   |
|-------------------|-------------------------------------------------|
| `calculer`        | Faire des calculs exacts                        |
| `date_et_heure`   | Donner la date et l'heure                       |
| `lister_fichiers` | Lister les fichiers du projet                   |
| `lire_fichier`    | Lire un fichier du projet (et seulement du projet) |
| `prendre_note`    | Enregistrer une note dans `notes.md`            |

## Le lancer

1. Créer une clé API sur <https://console.anthropic.com> (le service est payant à l'usage).
2. Dans un terminal, à la racine du projet :

   ```bash
   pip install -r agents/requirements.txt
   export ANTHROPIC_API_KEY="ta-clé"     # Windows : set ANTHROPIC_API_KEY=ta-clé
   python agents/assistant.py
   ```

3. Essayer par exemple : « Combien font 15 % de 240 ? », « Résume le README »,
   « Note que je dois finir la page d'accueil ».

Ne jamais mettre la clé API dans un fichier du dépôt.

## Créer ton propre agent

Pour ajouter un outil, trois étapes dans `assistant.py` :

1. écrire une fonction Python (section 1) ;
2. la décrire dans la liste `OUTILS` (section 2) — la description dit à Claude *quand* l'utiliser ;
3. l'ajouter au dictionnaire `FONCTIONS`.

Pour changer la personnalité ou le rôle de l'agent (traducteur, coach, prof…),
il suffit de modifier le texte `CONSIGNES`.
