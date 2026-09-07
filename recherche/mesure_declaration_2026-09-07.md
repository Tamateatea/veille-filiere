# La case « communication commerciale » comme indice — 2026-09-07

Produit par `outils/mesurer_declaration.py`. Paires jugees par Vincent dont la video a ete completee depuis sa page publique : **308** (+22 « je ne sais pas » exclues, 123 videos de vitrines ecartees comme dans la detection) ; videos avec la case cochee parmi elles : 51.

| Regle | VP | FP | FN | Precision | Rappel |
|---|---:|---:|---:|---:|---:|
| R3 (actuelle) | 81 | 18 | 8 | 82% | 91% |
| R3 + case cochee | 82 | 19 | 7 | 81% | 92% |
| case cochee seule | 37 | 3 | 52 | 92% | 42% |

Lecture : la case ne dit pas POUR QUI le contenu est commercial. Elle ne vaut comme indice que combinee a un signal (une entite nommee).
