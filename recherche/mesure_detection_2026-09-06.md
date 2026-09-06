# Mesure du detecteur — 2026-09-06

Reference : `jugements_reference_2026-09-06.csv` (248 paires mesurables, 20 « je ne sais pas » exclues). Detections : `donnees/detections.csv`.


123 paires jugees portent sur des videos publiees par un canal vitrine : elles sont hors du flux createur (routees vers la decouverte) et donc hors mesure — verdicts : 6 vraies, 116 fausses, 1 indecises. Les vraies restent des collaborations reelles : leur createur doit ressortir par le flux decouverte, pas par celui-ci.


## R1 signal seul

| | |
|---|---:|
| Retenues par la regle | 98 |
| dont vraies (VP) | 66 |
| dont fausses (FP) | 32 |
| Vraies manquees (FN) | 7 |
| Fausses ecartees (VN) | 143 |
| **Precision** | **67 %** |
| **Rappel** | **90 %** |

## R2 signal + indice commercial

| | |
|---|---:|
| Retenues par la regle | 62 |
| dont vraies (VP) | 58 |
| dont fausses (FP) | 4 |
| Vraies manquees (FN) | 15 |
| Fausses ecartees (VN) | 171 |
| **Precision** | **94 %** |
| **Rappel** | **79 %** |

## R3 signal fort, ou faible + indice

| | |
|---|---:|
| Retenues par la regle | 63 |
| dont vraies (VP) | 59 |
| dont fausses (FP) | 4 |
| Vraies manquees (FN) | 14 |
| Fausses ecartees (VN) | 171 |
| **Precision** | **94 %** |
| **Rappel** | **81 %** |

## Rappel par entite (R1)

| Entite | Vraies jugees | Retrouvees |
|---|---:|---:|
| CNIEL | 63 | 58 |
| INTERBEV | 7 | 7 |
| INAPORC | 2 | 0 |
| ANVOL | 1 | 1 |

## Limites de cette mesure — a lire avant de citer les chiffres

1. **Le rappel est relatif aux candidats juges**, pas a YouTube entier : le
   jeu de reference a ete constitue a partir des detections des anciennes
   regles. Une collaboration qu'aucune regle n'a jamais vue n'y figure pas.
2. **La mesure ne couvre que le canal interprofession** (CNIEL, CIFOG,
   INTERBEV, CLIPP, INAPORC, ANVOL). Les detections de marques (« Societe »,
   « Marie », « President »…) ne sont PAS mesurees ici : aucun verdict
   n'existe encore sur ce canal. Ne rien conclure sur elles.
3. **R3 est calibree sur ce meme jeu** : le declassement des quatre signaux
   pollueurs et le routage des canaux vitrines ont ete decides en regardant
   les erreurs de ce corpus. Ses chiffres sont donc optimistes. Ils ne
   seront etablis qu'apres verification sur un lot NEUF de jugements —
   c'est le prochain lot de ~50 cas prevu par le critere 6 du contrat.

