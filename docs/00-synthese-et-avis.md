# Synthèse générale et mon avis

> Portefeuille de 3 projets de contenu, produit par une équipe d'agents IA. Toi, tu es la directrice : tu choisis les thèmes et tu valides avant publication.

---

## 1. Mon avis honnête, en bref

Le projet tient la route : il est cohérent (enfants + valeurs + Coran) et les trois chaînes peuvent se renforcer entre elles. Mais **quatre points peuvent tout faire échouer** si on ne les traite pas dès le départ :

| ⚠️ Risque | Pourquoi c'est grave | Ce qu'on fait |
|---|---|---|
| **« Dessins animés de Disney »** | Les personnages, les musiques et les styles déposés de Disney sont protégés. Une chaîne qui les utilise se fait retirer ses vidéos pour violation de droits d'auteur, puis supprimer. | On crée **nos propres personnages**, dans un rendu 3D doux « qualité cinéma ». Jamais de nom, de personnage ni de musique Disney dans les prompts ou les titres. |
| **Contenu IA « produit à la chaîne »** | YouTube démonétise les chaînes au contenu répétitif ou produit en masse (règle sur le contenu « inauthentique »). Beaucoup de chaînes IA pour enfants ont été démonétisées. | Personnages récurrents, vrai scénario, vraie valeur éducative, ta touche humaine (ta voix ou ta validation visible), formats variés. **La qualité avant la quantité.** |
| **Chaîne « conçue pour les enfants » (Made for Kids)** | C'est obligatoire par la loi (COPPA) pour un public de 2 à 4 ans. Conséquences : pas de commentaires, pas de publicités personnalisées (donc des revenus publicitaires **bien plus faibles**), pas d'abonnements payants à la chaîne. | Les revenus publicitaires YouTube ne seront **qu'une source parmi d'autres**. Le vrai argent viendra des produits (voir §5). |
| **Projet Coran : la justesse religieuse** | Une erreur sur un verset, un hadith ou une histoire de prophète détruit la confiance de la communauté, et c'est une responsabilité. Selon l'avis majoritaire des savants, **on ne représente pas les prophètes** (ni leurs visages, ni leurs corps). La récitation du Coran par une voix IA est très mal acceptée. | On valide chaque script avec **une personne de science humaine** (imam ou enseignant qualifié). Les prophètes ne sont jamais montrés : on utilise la lumière, les décors, les animaux de l'histoire et un narrateur. La récitation vient de **vrais récitateurs**, avec autorisation. |

**Note santé** : l'OMS recommande **pas d'écran avant 2 ans**, et au plus **1 h par jour entre 2 et 4 ans**. Je te conseille de cibler **3 à 5 ans** (plutôt que 2 ans) et d'assumer un positionnement « écran calme et utile ». C'est éthique, et en plus c'est un **argument marketing** fort auprès des parents.

---

## 2. Une seule équipe ou une équipe par projet ?

**Ma recommandation : UNE seule équipe d'agents, avec un « dossier de marque » par projet.**

C'est exactement ce que tu préfères, et c'est le bon choix au départ :
- les métiers sont les mêmes pour les 3 projets (recherche, script, visuels, voix, montage, SEO, réseaux sociaux) ;
- ce qui change, c'est **le contexte**, pas l'équipe. Chaque agent lit le dossier de marque du projet en cours (ton, personnages, langues, règles) ;
- c'est moins cher et plus simple à piloter pour toi.

**Exception :** le projet Coran a besoin d'un agent en plus, le **Gardien de la conformité religieuse**, qui bloque tout contenu non sourcé. Il reste toujours suivi d'une validation humaine par une personne de science.

Plus tard, si une chaîne décolle (plus de 3 vidéos par semaine), on pourra la dupliquer en équipe dédiée.

### L'équipe (11 agents)

```
                         TOI (Directrice — valide)
                                   │
                    ┌──────── 1. ORCHESTRATEUR ────────┐
                    │  (chef de projet, planning,       │
                    │   te pose les questions)          │
   ┌────────────┬───┴────────┬────────────┬────────────┼─────────────┐
2. Veille &   3. Scénariste 4. Conformité 5. Directeur 6. Voix &     7. Montage
   Recherche     (scripts     & Sécurité    artistique   Musique       & Assemblage
   marché        multilingues) enfants/droits (prompts   (TTS FR/EN/AR,
                                 + 4bis Gardien  images/vidéo,  musiques libres)
                                 religieux      personnages)
   ┌────────────┬────────────┬────────────┐
8. SEO        9. Réseaux    10. Analyse &  11. Designer
   YouTube       sociaux       Monétisation   fiches (Projet 3)
   (titres,      (TikTok/IG,   (stats, revenus,  (carrousels
   miniatures)   calendrier)   produits)          Instagram/TikTok)
```

Le détail de chaque agent est dans [`../.claude/agents/`](../.claude/agents/). Chaque fichier est un « prompt système » prêt à l'emploi.

### Le circuit de production (une vidéo)

1. **Toi** → tu donnes un thème (ex. « se brosser les dents »).
2. **Orchestrateur** → te pose 3 à 5 questions ciblées, puis crée la fiche de production.
3. **Veille** → regarde ce qui existe déjà sur ce thème, repère le manque, propose l'angle.
4. **Scénariste** → écrit le script (durée, chanson, répétitions, langues).
5. **Conformité** (et **Gardien religieux** pour le projet 2) → contrôle, corrige, bloque si besoin.
6. **Directeur artistique** → découpe en plans et écrit les prompts image et vidéo, avec des personnages cohérents d'un épisode à l'autre.
7. **Voix & Musique** → prépare les voix (FR/EN/AR) et la musique.
8. **Montage** → assemble, sous-titre, exporte en 16:9 (2 min) et en 9:16 (Short/Reel/TikTok).
9. **SEO + Réseaux sociaux** → titre, description, miniature, hashtags, horaires.
10. **✅ TOI** → **une seule validation finale** (OUI / NON / à corriger avec un commentaire).
11. Publication programmée → **Analyse** chaque semaine → les idées suivantes s'adaptent aux chiffres.

> **Ce qui est automatisable aujourd'hui :** les étapes 2 à 9 jusqu'à environ 80 %. La génération vidéo IA demande encore souvent 2 ou 3 essais par plan. Prévois au début **2 à 4 heures par vidéo de 2 minutes**, puis moins quand les personnages et les modèles de prompts seront stabilisés.

---

## 3. Les outils (la « boîte à outils » de l'équipe)

| Fonction | Outils possibles (à choisir selon ton budget) |
|---|---|
| Cerveau des agents | Claude (Projets ou Claude Code), avec un projet par chaîne qui contient le dossier de marque |
| Images et personnages cohérents | Midjourney (référence de personnage), GPT-Image, Ideogram, Leonardo |
| Vidéo IA | Kling, Runway, Google Veo, Hailuo/MiniMax, Pika |
| Voix | ElevenLabs (FR/EN/AR, voix d'enfant ou de conteur) ; **jamais pour réciter le Coran** |
| Musique | Suno ou Udio (vérifie la licence commerciale), bibliothèque audio YouTube, Epidemic Sound |
| Montage | CapCut, Canva Vidéo, DaVinci Resolve, Descript |
| Fiches (Projet 3) | Canva (modèles de marque), Figma |
| Automatisation | n8n ou Make (enchaîne les étapes, envoie la validation sur ton téléphone) |
| Planification | YouTube Studio, Metricool, Buffer, Later |
| Suivi | Notion ou Airtable (tableau de production : idée → script → validation → publié) |

Budget indicatif pour démarrer : **80 à 200 € par mois** (abonnements vidéo IA, voix, image et planification).

---

## 4. Comment se différencier : le principe général

Le marché des dessins animés IA pour enfants est **saturé de contenus rapides, bruyants et sans fond** (beaucoup de copies du style Cocomelon). Les parents commencent à les rejeter. Notre différence tient en **3 mots : CALME, VRAI, FAMILLE**.

1. **Calme** : rythme lent, couleurs douces, pas de stimulation excessive. C'est la tendance « slow TV pour enfants » (comme *Bluey*, *Hey Bear Sensory* ou *Ms Rachel*, que les parents adorent).
2. **Vrai** : chaque épisode a un objectif éducatif clair, écrit pour les parents dans la description (« ce que votre enfant apprend »).
3. **Famille** : les mêmes personnages dans les 3 projets, ou du moins un univers commun. Une marque reconnaissable, ça se vend ensuite en livres, coloriages et peluches.

Les angles propres à chaque projet sont détaillés dans chaque fiche projet.

---

## 5. Gagner de l'argent : la vérité

| Source | Projet 1 | Projet 2 | Projet 3 | Commentaire |
|---|:-:|:-:|:-:|---|
| Pub YouTube (YPP) | ✅ faible | ✅ faible | – | Seuil : 1 000 abonnés + 4 000 h ou 10 M de vues Shorts sur 90 jours. Revenus faibles en « Made for Kids ». |
| Fichiers à imprimer (coloriages, routines, cahiers) | ✅✅ | ✅✅ | ✅✅ | Etsy, Gumroad, Payhip. **C'est la meilleure source au début.** |
| Livres (Amazon KDP) | ✅✅ | ✅✅ | ✅ | Livres d'histoires avec tes personnages, cahiers d'activités |
| Produits physiques (peluches, posters, calendriers Ramadan) | ✅ | ✅✅ | ✅ | Plus tard, quand la marque est connue |
| Appli ou abonnement premium sans pub | – | ✅✅ | – | Les parents musulmans paient pour un contenu sûr |
| Partenariats (marques de parents, éditeurs islamiques) | ✅ | ✅ | ✅✅ | Par Instagram/TikTok (cible parents/adultes) |
| TikTok Creator Rewards | – | – | ✅ | Vidéos de plus d'une minute ; pas pour les comptes destinés aux enfants |
| Dons, soutien (Ko-fi, Patreon) | – | ✅ | ✅ | Bien accepté pour le contenu religieux |

👉 **Stratégie :** YouTube attire l'audience, Instagram et TikTok parlent **aux parents**, et l'argent vient des **produits**.

⚠️ Les règles des plateformes (seuils, durées minimales, règles IA) changent souvent. L'agent Veille doit les **revérifier chaque mois**.

---

## 6. Ordre de lancement conseillé

1. **Mois 1** : Projet 3 (fiches Coran adultes). C'est le plus rapide et le moins cher, et ça construit ta communauté et ta crédibilité.
2. **Mois 2** : Projet 2 (Coran enfants). C'est la niche la moins saturée, avec un public fidèle qui paie. Il profite de la communauté du projet 3.
3. **Mois 3 et suivants** : Projet 1 (dessins animés). C'est le marché le plus concurrentiel. On le lance quand le circuit de production est rodé.

*(Tu peux changer cet ordre : c'est une des questions du questionnaire.)*

---

## 7. Prochaine étape

Réponds au [questionnaire complet](./questionnaire-complet.md). Tu peux répondre petit à petit, par bloc, même en vocal. Avec tes réponses, je finalise :
- les dossiers de marque (personnages, ton, couleurs) ;
- les prompts des agents personnalisés ;
- les 30 premières idées de vidéos par projet ;
- le calendrier de publication du premier mois.
