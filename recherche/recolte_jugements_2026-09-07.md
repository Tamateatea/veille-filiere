# Recolte des jugements — 2026-09-07

Produit par `outils/relire_jugements.py` depuis `A_JUGER.xlsx`.

**Verdicts recoltes : 13** (lignes nouvelles ou modifiees : 13)

- collaboration remuneree : 7
- je ne sais pas : 6

## Notes de Vincent (7) — critere 10

**Juste Zoé / CNIEL** (x6N7UloAJ6I) — verdict : je ne sais pas
> est-ce que tu peux vérifier? J'ai l'impression que ça point vers un site qui est une ONG de protection des animaux, mais pas impossible que ce soit un lien cahcé (peu probable)

REPONSE : Verifie (07/09, page publique du site) : nosamispourlavie.org est un SANCTUAIRE ANIMALIER a Marrakech (chiens et equides abandonnes), pas la campagne du CNIEL. Vincent a raison. Le mot-cle « Nos amis pour la vie » a ici trouve un homonyme ; la mention « Collaboration commerciale » de la description concerne Manucurist. Proposition : hors sujet pour le CNIEL. Le mot-cle reste utile (10 vraies collaborations jugees), mais son homonyme est note.

**JohanPapz / Herta** (5pwLIrm_GBA) — verdict : collaboration remuneree
> est-ce qu'on peut dire que herta est vraiment un marque qu'on veut cibler? Je ne sais pas

REPONSE : Herta est une marque de charcuterie (groupe Nestle / Casa Tarradellas), donc dans le perimetre viande du contrat. Verifie en plus : la description complete se termine par « Video sponsorisee par Herta » — la collaboration est declaree par le createur lui-meme. La question « veut-on la cibler ? » est une decision de perimetre qui revient a Vincent ; l'outil la garde tant qu'il ne l'exclut pas.

**Doigby / Babybel** (RPtRXiOgR68) — verdict : je ne sais pas
> c'est soit un collaboration, soit le youtubeur qui fait de la pub pour babybel et kiri par bonté de cœur (peu probable mais difficile à dire)

REPONSE : Verifie (07/09, page publique YouTube) : la video porte la case « Inclut une communication commerciale » cochee par le createur. La description entiere est construite autour de Babybel et renvoie vers ribambel.com, un programme du groupe Bel (Babybel, Kiri). Reserve : la case ne dit pas POUR QUI ; Asus est aussi partenaire de la chaine. Faisceau fort : proposition collaboration remuneree.

**Doigby / Babybel** (s86RvXtXCKU) — verdict : je ne sais pas
> ça augmente la probabilité que ce soit un collaboration rémunérée

REPONSE : Verifie : meme case « Inclut une communication commerciale » cochee, et la carte Fortnite « Babybel Reloaded » est une creation pour la marque. Deux videos a un an d'ecart, meme montage : proposition collaboration remuneree pour les deux.

**Mllex Chloé / Danette** (Fk8v1sJwm2c) — verdict : je ne sais pas
> danette apparaît dans le titre mais pas dans la description, qui n'indique que Uber (description tronquée)

REPONSE : Verifie : la description en base etait tronquee a 900 caracteres (ancienne moisson : 13 644 videos sur 54 212 sont dans ce cas, MESURE ce jour ; les nouvelles lectures par flux RSS sont completes). La description complete (1 314 caracteres) ne cite pas Danette : « Danette a la vanille » est une couleur de cheveux. La case « communication commerciale » est cochee, mais pour les codes Uber et Polagram. Proposition : hors sujet.

**Encuisineaugustine / Le Gaulois** (9XviQwGHG0U) — verdict : je ne sais pas
> je ne sais pas mais plutôt cool qu'elle fasse de la pub pour un pané végétal

REPONSE : Verifie : la description complete se termine par « *collaboration commerciale », mention absente de l'extrait parce que la description en base est tronquee a 900 caracteres. Avec « grace a Le Gaulois » et un produit nomme, c'est une collaboration declaree. Proposition : collaboration remuneree. (Le pane est vegetal, mais Le Gaulois est une marque de volaille du groupe LDC : la note de Vincent est entendue, c'est une decision de perimetre.)

**Angelica Pâtisserie / Actimel** (5eJ95x17wg4) — verdict : je ne sais pas
> je ne sais pas. Elle fait un trompe l'œil de gateau qui ressemble un bouteille d'actimel mais il n'y a rien en descirption

REPONSE : Verifie : aucune description, case commerciale non cochee, pas de transcription en base. Rien ne permet de trancher : « je ne sais pas » est la bonne reponse, la ligne reste en attente.


Cumul : `donnees/jugements_recoltes.csv` (62 paires).

## Lecon du passage

- Un quart de la base (13 644 videos) a une description tronquee a 900 caracteres, heritee de l'ancienne moisson. Les mentions « collaboration commerciale » placees en fin de description y sont invisibles. A proposer : recompleter ces descriptions depuis les pages publiques (zero quota, une nuit).
- La case YouTube « Inclut une communication commerciale » est lisible sur la page publique : un signal de plus a integrer au facteur (mesure a 91 % de precision dans l'ancien projet).
