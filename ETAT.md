# Etat — veille-filiere

Mis a jour le **6 septembre 2026**.

## Ou on en est

Le projet vient d'etre fonde. `CONTRAT.md` est valide par Vincent
(6 septembre). Les acquis de l'ancien projet sont copies dans `acquis/`.

**Premiere mesure faite** — le jeu de reference, re-derive des classeurs et
non repris du journal (MESURE, `recherche/jugements_reference_2026-09-06.md`) :

| | |
|---|---:|
| Verdicts rendus par Vincent sur des videos YouTube | **391** |
| dont collaboration remuneree | 79 |
| dont hors sujet | 285 |
| dont « je ne sais pas » | 21 |
| dont mention sans collaboration | 6 |
| Annonces Meta soumises, jamais jugees | 90 |

Note : l'ancien projet parlait d'un jeu de reference de 175 videos. La
re-derivation en trouve **391** — Vincent a juge les classeurs 3 et 4 que la
documentation croyait en attente. C'est exactement pourquoi on re-derive.

## Le dictionnaire et le detecteur existent et sont mesures

**Dictionnaire** (`DICTIONNAIRE.xlsx`, le classeur maitre, editable par
Vincent) : 78 entites, 126 signaux — 119 confirmes, 55 forts / 71 faibles
(MESURE, `recherche/dictionnaire_2026-09-06.md`).

**Detecteur** (`outils/detecter.py` puis `outils/mesurer_detection.py`) :
trois regles mesurees contre les verdicts de Vincent, canal interprofession
(MESURE, `recherche/mesure_detection_2026-09-06.md`) :

| Regle | Precision | Rappel |
|---|---:|---:|
| R1 signal seul | 67 % | 90 % |
| R2 signal + indice commercial | 94 % | 79 % |
| **R3 signal fort, ou faible + indice** | **94 %** | **81 %** |

Deux decisions de conception, prises en analysant les desaccords :

1. **Les videos publiees par un canal vitrine sortent du flux createur**
   (123 paires jugees, dont 116 fausses — un tiers du bruit de l'ancien jeu
   venait de la). Elles partent dans `donnees/contenus_vitrines.csv`, le
   flux decouverte. A faire ratifier par Vincent.
2. **Quatre signaux declasses en faible sur mesure** : #Viande, #Elevage,
   Made in Viande, Naturellement Flexitariens.

**R3 depasse les seuils du contrat (80/80) MAIS est calibree sur le meme
jeu** : chiffres optimistes, a confirmer sur un lot neuf de jugements
(critere 6). Ne pas declarer les criteres 2 et 3 atteints avant ca.

## Prochaine etape

3. **Le classeur de verification** lisible (criteres 9, 10) — genere depuis
   `donnees/detections.csv`, en commencant par les paires R3 non encore
   jugees.
4. **Le facteur** : la veille incrementale nocturne (critere 1).
5. **TikTok** : rattacher les partenariats labellises aux commanditaires via
   hashtags (critere 6) — produira le lot de ~50 cas pour Vincent.

## Interventions attendues de Vincent

1. **Ratifier le routage vitrine** (decision 1 ci-dessus).
2. Plus tard : un lot de ~50 cas a juger (critere 6, et validation de R3
   sur du neuf), et le jeton Meta quand il decidera.
