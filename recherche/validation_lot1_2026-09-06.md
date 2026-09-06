# Validation de R3 sur le lot neuf — 2026-09-06

Etalon : `jugements_recoltes.csv`, 48 verdicts (1 « je ne sais pas » exclus). Regle : R3 ACTUELLE (apres proximite des indices et declassement de CHAUD !).

Provenance : 5 verdicts directs de Vincent, 43 pre-tries par Claude et valides en bloc par lui. Deux cas du lot ont inspire les corrections mesurees ici (fuite legere).

| Canal | Retenues | VP | FP | FN | VN | Precision | Rappel |
|---|---:|---:|---:|---:|---:|---:|---:|
| interprofession | 12 | 5 | 7 | 0 | 5 | 42 % | 100 % |
| marque | 27 | 0 | 27 | 0 | 3 | 0 % | — |

Paires du lot que la regle actuelle ne retient plus (effet des corrections du jour + cas sans indice proche) : 8 ecartees a raison ou a tort — voir FN.
