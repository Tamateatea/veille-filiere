# CONTRAT — la definition de « l'outil marche »

Propose le 6 septembre 2026. **Valide par Vincent le 6 septembre 2026**, avec
deux exigences integrees le meme jour : la veille nocturne automatique
(section 1) et les criteres 9 et 10 (lisibilite humaine, notes lues).

**Amendement du 6 septembre au soir, decide par Vincent** (sur conseil de
son ami informaticien) : **YouTube d'abord, en entier ; les autres reseaux
quand YouTube marche bien.** Le critere 6 (TikTok) est reporte a la version
suivante — il reste au contrat, il n'est simplement plus dans la v1.
« YouTube marche bien » = les criteres 1 a 5 et 7 a 11 tenus sur YouTube,
boucle complete : facteur nocturne -> detection -> pre-tri de Claude ->
classeur A_JUGER -> verdicts de Vincent qui nourrissent le dictionnaire.

Ce fichier est le seul juge de la phrase « j'ai construit un outil, il marche ».
Claude n'a pas le droit de la prononcer autrement qu'en citant les criteres
ci-dessous, chacun avec son nombre et le fichier de `recherche/` qui le prouve.

---

## 1. Ce que l'outil est

Un outil lance par **une seule commande**, qui lit des contenus publics de
YouTube et TikTok (Instagram des que le jeton Meta existe) et produit **la
liste des contenus portant des signaux forts de collaboration commerciale
remuneree** avec les filieres viande, lait et oeufs.

Perimetre des commanditaires : **interprofessions ET marques**, detectees
ensemble mais **mesurees separement** — les deux canaux n'ont pas le meme
bruit. *(Choix propose, a confirmer ou barrer par Vincent.)*

Les oeufs sont inclus (decision de Vincent, 6 septembre 2026).

**Rythme :** un rattrapage initial (les corpus deja moissonnes), puis une
**veille nocturne automatique** par tache planifiee, qui ne regarde que le
contenu nouveau depuis le passage precedent — c'est ce qui la maintient sous
les quotas quotidiens des plateformes. Vincent ne lance rien a la main.

## 2. Ce que l'outil produit

Une ligne par contenu detecte : plateforme, compte (identifiant exact), date,
URL, la liste des **signaux observes** (mention d'alias, hashtag de campagne,
formule de remerciement, case de declaration…), et **l'extrait exact** qui a
declenche la detection. Plus une synthese : une ligne par compte.

Regle ferme : l'outil ne soumet a un humain que des **entites propres** — un
compte, un nom, une plateforme. Jamais un fragment de texte brut.

## 3. Les criteres de reception

Chacun est verifiable par Vincent **sans lire une ligne de code**.

| # | Critere | Comment Vincent le verifie |
|---|---|---|
| 1 | Une seule commande fait tout, et relancee, elle reprend ou elle s'etait arretee | il la lance deux fois |
| 2 | **Precision ≥ 80 %** sur le jeu de reference (les 175 videos jugees) | le rapport nomme le fichier qui le mesure |
| 3 | **Rappel ≥ 80 %** sur le meme jeu | idem |
| 4 | Les nombres sont **re-derives des fichiers bruts**, jamais recopies du journal | le rapport cite ses sources |
| 5 | Ajouter un alias ou un hashtag = **editer une ligne d'un classeur**, zero code, et la re-detection tourne sans nouvelle collecte | il ajoute un hashtag et relance |
| 6 | TikTok : les contenus a label de partenariat sont rattaches a un commanditaire quand un hashtag ou alias le permet ; precision mesuree sur **~50 cas juges par Vincent** | il juge le lot, le rapport donne le nombre |
| 7 | Chaque execution ecrit un **rapport horodate** dans `recherche/` avec ces nombres | il ouvre le dernier rapport |
| 8 | **Zero euro, zero authentification**, donnees publiques seulement | constat |
| 9 | **Lisibilite humaine** : chaque ligne soumise a Vincent porte l'extrait EXACT qui a declenche la detection (jamais un extrait tronque qui ne le contient pas), le compte, son audience, le lien cliquable ; si la preuve n'est pas dans l'extrait, la ligne le dit | il ouvre le classeur et verifie dix lignes |
| 10 | **Ses notes sont lues** : le classeur a une colonne commentaire, relue a chaque passage ; le rapport suivant liste chaque note et ce qui en a ete fait | il ecrit une note et lit le rapport suivant |
| 11 | **L'outil propose, il ne s'auto-modifie pas** : chaque passage produit une liste de propositions (nouveaux comptes, alias, hashtags) avec leur preuve, dans un onglet separe ; rien n'entre en detection sans confirmation | il verifie qu'une proposition non confirmee ne detecte rien |

## 4. Ce que l'outil n'est PAS (version 1)

- Pas le site public. Rien n'est publie.
- Pas Instagram tant que le jeton Meta n'existe pas.
- Pas des verdicts : des **signaux**, qu'un humain jugera.

## 5. Les interventions de Vincent, toutes connues d'avance

1. Valider (ou corriger) ce contrat.
2. Juger **un a deux lots d'environ 50 cas** quand une mesure l'exige.
3. Le jeton Meta, quand il decide de faire la verification d'identite.
4. Les decisions marquees *(a confirmer par Vincent)* dans ce fichier.

Tout le reste se fait sans lui.

## 6. Ce qui est conserve de l'existant — rien d'autre

- Les **corpus moissonnes** (332 119 videos YouTube, 149 711 contenus TikTok) :
  trois jours de quota, on ne les repaie pas.
- Le **jeu de reference** : les 175 videos jugees par Vincent. Intouchable.
- La **cartographie de Vincent** (`Preliminary dataset.xlsx`) : 88 lignes,
  alias et hashtags observes a la main.
- Le savoir **re-verifie au moment de s'en servir** — le journal indique ou
  chercher, il ne fait pas preuve.

Le code et la documentation actuels ne sont pas repris : l'outil se construit
propre, dans un dossier neuf, hors OneDrive et sans `&` dans le nom.
