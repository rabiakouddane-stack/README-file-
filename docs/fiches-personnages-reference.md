# Fiches de référence des personnages, et plan de production du pilote

> **Pourquoi c'est l'étape la plus importante :** si Alya n'a pas exactement le même visage, les mêmes cheveux et les mêmes habits dans chaque scène, la série paraît « fausse ». On crée donc **une fois pour toutes** une image de référence par personnage. Ensuite, **on donne toujours cette image à l'outil**, en plus du texte.

---

## Étape 1 : créer les images de référence (gratuit)

**Outil conseillé : Google Gemini (génération et modification d'images).** Il garde très bien la ressemblance quand on lui redonne une image. Leonardo ou Bing Image Creator peuvent servir de solution de secours.

Pour chaque personnage :
1. Colle le prompt « planche personnage » ci-dessous.
2. Génère **3 versions**, puis **choisis ta préférée** ✅.
3. Enregistre-la avec un nom clair (`REF_ALYA.png`, `REF_AMIR_nouveau-ne.png`, etc.) dans un dossier « Références ».
4. Génère ensuite la planche des **expressions** en redonnant l'image choisie : « Same character as the reference image, … ».

### Style commun (à ajouter à la fin de chaque prompt)
```
original stylized 3D animated character, soft rounded shapes, warm soft studio lighting, plain cream background, cinematic quality, character design sheet, no text, no logo
```

### Alya (2 ans)
**Planche personnage :**
```
Character turnaround sheet of ALYA, a 2-year-old toddler girl: round face, big warm brown eyes, very curly voluminous dark-brown hair in two small puffs with mustard-yellow hair ties, rosy cheeks, light tan skin, sage-green linen overalls over a cream t-shirt, barefoot. Front view, three-quarter view, side view and back view, full body, standing, same character in every view. [STYLE]
```
**Planche expressions** (avec l'image de référence) :
```
Same character as the reference image. Expression sheet with 6 head close-ups: happy smile, amazed with open mouth, shy looking down, worried, proud "voilà" smile, whispering with finger on lips. [STYLE]
```

### Amir (nouveau-né)
```
Character sheet of AMIR, a tiny newborn baby boy: sleepy round face, wisps of dark hair, chubby cheeks, tiny hands, wrapped in a cream knitted blanket. Views: sleeping in arms, eyes open looking up, close-up of tiny hand. Same baby in every view. [STYLE]
```

### Maman
```
Character turnaround sheet of MOM: woman in her early 30s, gentle smile, warm brown eyes, light tan skin, long straight black hair worn loose, cozy terracotta knitted sweater, blue jeans, white sneakers. Front, three-quarter, side views, full body. Same character in every view. [STYLE]
```
*(Version enceinte, pour les plans 1 à 4 : ajouter « visibly pregnant, round belly ». À générer à partir de l'image de référence.)*

### Papa
```
Character turnaround sheet of DAD: man in his early 30s, short dark hair, neat short beard, kind eyes, light-grey sweater, dark trousers. Front, three-quarter, side views, full body. [STYLE]
```

### Mamie (côté papa)
```
Character turnaround sheet of MAMIE: warm elderly grandmother, round kind face, gentle wrinkled smile, cream hijab, beige long cardigan over a long dress. Front, three-quarter, side views, full body. [STYLE]
```

### Papi (côté papa)
```
Character turnaround sheet of PAPI: gentle elderly grandfather, short white beard, round glasses, grey knitted beanie, brown knitted vest over a white shirt. Front, three-quarter, side views, full body. [STYLE]
```

### Ma (côté maman)
```
Character turnaround sheet of MA: young-looking 58-year-old grandmother with a youthful smooth face, sparkling dark eyes, warm smile, sage-green hijab, light cream button-up shirt, terracotta pleated trousers, flat loafers. Front, three-quarter, side views, full body. [STYLE]
```

### Bassi (côté maman)
```
Character turnaround sheet of BASSI: 64-year-old grandfather, black hair with a few grey strands at the temples, thick black moustache, warm laugh lines, navy-blue t-shirt, blue jeans, sneakers, no hat. Front, three-quarter, side views, full body. [STYLE]
```

### Tata
```
Character turnaround sheet of AUNT: young woman, 30 years old, fair light skin, joyful expression, very long straight dark-brown hair worn loose, mustard-yellow t-shirt, blue jeans, white sneakers. Front, three-quarter, side views, full body. [STYLE]
```

### Yanis (le cousin, 2 ans et demi)
```
Character turnaround sheet of YANIS: a 2-and-a-half-year-old toddler boy, fair light skin, completely straight smooth dark-brown hair (same color as Amir) ending just above his shoulders, worn loose, chubby rosy cheeks, big cheerful smile, red hoodie, soft jeans, small sneakers. Front, three-quarter, side views, full body. [STYLE]
```

### Tonton (frère de maman, papa de Yanis)
```
Character turnaround sheet of UNCLE: very tall young man, 30 years old, very short black hair (neat short crop), short trimmed beard, big friendly smile, olive-green t-shirt, blue jeans, sneakers. Front, three-quarter, side views, full body. [STYLE]
```

### Les décors (une seule fois)
```
Bright Montessori living room, child-eye-level view: low wooden shelf with a few wooden toys, round beige wool rug, cream sofa, large window with soft morning light, green plants, light wood floor, sage green and cream palette. Original stylized 3D animation, cinematic, no people, no text.
```
```
Warm front entrance of a family home seen from a toddler's height, wooden door, coat hooks, soft daylight. Original stylized 3D animation, no people, no text.
```

**À la fin de l'étape 1, tu as environ 14 images de référence.** Elles serviront pour **toute la série**.

---

## Étape 2 : créer les images des 18 scènes

Pour chaque scène de `episode-pilote-naissance.md` :
1. Dans Gemini, **ajoute les images de référence** des personnages présents dans la scène (et du décor).
2. Colle le prompt de la scène, en commençant par : `Using the reference images for the characters and the room, …`
3. Fais 2 ou 3 essais, puis garde la meilleure image → `S1E1_plan01.png`, etc.

## Étape 3 : animer (Kling, en image vers vidéo)
1. Importe l'image de la scène.
2. Colle le **prompt vidéo** (mouvement lent, 5 à 8 s).
3. Pour économiser les crédits, commence par les **plans fixes** (1, 3, 6, 11, 14).

## Étape 4 : voix (ElevenLabs)
- **Narratrice** : voix féminine douce, vitesse lente. Toujours la même voix.
- **Alya** : voix de petite fille (ou voix douce rendue plus aiguë), avec de très courtes répliques.
- **Maman, Mamie, Papi, Bassi** : une voix fixe chacun.
- **Amir** : vrais sons de bébé (bibliothèque CC0 : souffle, gazouillis).
- L'agent Voix prépare un fichier avec chaque réplique, la voix choisie et les pauses.

## Étape 5 : montage (CapCut)
L'agent Montage fournit la feuille de montage : ordre, durées, fondus, voix, sons, **aucune musique**, sous-titres, version 16:9 et Short 9:16.

## Étape 6 : ta validation finale, puis la publication ✅

---

## Ton planning pour ce pilote (1 h par jour)

| Jour | Ce que tu fais |
|---|---|
| J1 | Images de référence : Alya, Amir, Maman, Papa (choisir les meilleures) |
| J2 | Images de référence : Mamie, Papi, Ma, Bassi, Tata, Tonton, Yanis, décors |
| J3 | Images des scènes 1 à 9 |
| J4 | Images des scènes 10 à 18 |
| J5 | Animation des scènes 1 à 9 (Kling) |
| J6 | Animation des scènes 10 à 18 |
| J7 | Voix (ElevenLabs) + montage CapCut à partir de la feuille de montage |
| J8 | ✅ Validation finale, puis publication de l'épisode et du Short |

👉 **Pour ce premier épisode, compte environ 8 jours.** Les suivants iront **2 fois plus vite**, car les personnages et les décors seront déjà prêts.
