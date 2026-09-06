# Detection sur le corpus gele — 2026-09-06

Produit par `outils/detecter.py`. Corpus : les 27353 videos candidates conservees dans `moisson_videos.json` (cle `touchees`). Dictionnaire : 67 signaux `confirme`, 2 temoins.

**Paires (video, entite) detectees : 126**
**dont avec au moins un indice commercial : 73**
**Videos publiees par un canal vitrine, routees vers la decouverte : 149** (`donnees/contenus_vitrines.csv`)

## Par entite

| Entite | Paires |
|---|---:|
| CNIEL | 89 |
| INTERBEV | 34 |
| ANVOL | 2 |
| Nestle France | 1 |

## Par signal (tous)

| Signal | Videos touchees |
|---|---:|
| Produits Laitiers | 78 |
| CHAUD ! | 10 |
| Aimez la viande | 9 |
| #Viande | 9 |
| Aimez la viande, mangez-en mieux | 8 |
| #EnjoyItsFromEurope | 6 |
| Made in Viande | 6 |
| Naturellement Flexitariens | 5 |
| En Mode Actif | 2 |
| Le Mois de la Volaille Francaise | 1 |
| Volailles Festives | 1 |
| @nestleenfrance | 1 |
| @lesproduitslaitiers | 1 |

## Groupe temoin (cerealier, ne detecte pas)

Aucune occurrence.

Detail ligne par ligne : `donnees/detections.csv`.
