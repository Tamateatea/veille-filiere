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

## Le classeur de verification existe : `A_JUGER.xlsx`

Genere le 06/09 (MESURE, `recherche/a_juger_2026-09-06.md`) : **48 paires**
tirees au hasard parmi les 722 retenues par R3 et jamais jugees —
**18 interprofession** (tout ce qui reste : elles valideront les 94 % / 81 %
sur du neuf) et **30 marque** (la premiere mesure du canal marque, D3).

Garanties integrees : l'extrait contient toujours son signal (verifie a la
generation, qui echoue sinon — critere 9) ; la colonne commentaire est
recoltee par `outils/relire_jugements.py`, qui liste chaque note et exige
une reponse (critere 10) ; le generateur refuse d'ecraser un classeur
contenant des verdicts non recoltes.

## Prochaine etape

4. **Le facteur** : la veille incrementale nocturne (critere 1), stockage
   SQLite a construire a cette occasion.
5. **TikTok** : rattacher les partenariats labellises aux commanditaires via
   hashtags (critere 6).

## Interventions attendues de Vincent

1. **Juger `A_JUGER.xlsx`** (48 lignes) — c'est ce qui etablira les vrais
   chiffres de R3 et la premiere mesure du canal marque.
2. **Ratifier le routage vitrine** (decision 1 ci-dessus).
3. Plus tard : le jeton Meta quand il decidera.
