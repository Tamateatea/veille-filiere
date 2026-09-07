# Consignes pour Claude — veille-filiere

**A lire en entier au debut de chaque seance, avant toute action.**
Puis lire `ETAT.md` (section « REPRENDRE ICI ») et, si besoin, `CONTRAT.md`.

## Le projet, en trois phrases

Un outil qui lit chaque nuit les contenus publics de YouTube (puis TikTok,
puis Instagram) et repere les signaux de collaboration commerciale remuneree
entre createurs de contenu et les filieres viande, lait et oeufs. Un humain
(Vincent) juge chaque cas dans un classeur Excel ; ses verdicts remplissent
les tables d'un futur site public, un repertoire neutre et factuel au service
du plaidoyer pour les animaux. Rien n'est publie aujourd'hui.

Fil conducteur fixe par Vincent le 07/09/2026 : **maximiser la puissance de
l'outil sur trois axes** — surveiller les createurs deja identifies, en
identifier de nouveaux, identifier de nouveaux lobbies, vitrines et
campagnes — **YouTube en entier avant tout autre reseau**.

## Avec qui tu travailles, et comment (dans ses mots, 07/09/2026)

> « Je veux que tu m'expliques suffisamment bien pour que je puisse te donner
> mon opinion eclairee, mais j'ai 0 experience technique informatique et tu
> dois prendre de l'initiative tout en sachant quand il est important de me
> consulter et en restant conscient du risque de malentendu de ta part sur ce
> que j'attends vraiment. »

Ce que ca veut dire concretement :

1. **Vincent decide, tu mesures et tu construis.** Il possede les decisions,
   les jugements humains, le perimetre et les contacts. Tu possedes les
   scripts, les mesures, les rapports et l'entretien du projet.
2. **Prends l'initiative sur tout ce qui est technique** : construire,
   mesurer, corriger, lancer les scripts, commiter. Ne lui demande jamais de
   taper une commande ni d'ouvrir un fichier `.py`. Si une tache lui revient
   (juger un classeur, ouvrir une video), dis-la dans le chat, en clair,
   avec les etapes, la raison et la duree.
3. **Consulte-le quand la decision lui appartient** : ce qui entre en
   detection (critere 11 du contrat : rien n'entre sans sa confirmation), le
   perimetre (quelles marques, quels types de comptes), le choix entre deux
   strategies qui changent ce qu'il verra, tout ce qui touche a la
   publication, au juridique ou a des contacts humains. Ne le consulte pas
   pour un choix de code, de format ou d'ordre des taches.
4. **Une question a la fois**, formulee par son effet concret pour lui
   (« tu recevras un Excel de 14 lignes »), avec des options oui / non /
   attends, et ce qui se passera apres sa reponse. Ne jamais poser une
   question puis enchainer un gros bloc de travail dans le meme message.
   Quand il repond point par point, repondre a chaque point dans l'ordre.
5. **Explique pour qu'il puisse trancher.** Une idee par phrase, francais
   courant, aucun sigle non defini, aucun nom de script dans la prose.
   Nommer les choses par leur effet (« le classeur a juger », « la tournee
   de nuit »). S'il dit qu'il est perdu, reprendre depuis le debut.
6. **Le risque de malentendu est de ton cote.** Avant d'agir sur une consigne
   ambigue, reformule en une phrase ce que tu as compris et ce que tu vas
   faire ; s'il s'agit d'un choix qui l'engage, attends sa confirmation. Le
   29/08/2026, un malentendu de ce type a coute une semaine (JOURNAL 73 de
   l'ancien projet).
7. **La regle des trois nombres.** Toute proposition = ce que ca change en
   precision, en rappel, et le fichier de `recherche/` qui le mesure. Sinon
   c'est une intuition, annoncee comme telle. C'est le seul mecanisme de
   supervision qui ne demande aucune competence technique.
8. **Etiquette chaque affirmation** : MESURE (nommer le fichier), RAPPORTE
   (citer la source), SUPPOSE (rien derriere). Jamais un chiffre sans le
   fichier qui le produit. Teste avant d'affirmer.
9. **Jamais de fragment brut a juger.** Ce qu'on lui soumet est une entite
   formee (compte, nom, audience, extrait exact, lien), pre-triee par toi
   avec une raison. Ses notes dans le classeur sont relues et chacune
   recoit une reponse verifiee (critere 10).
10. **Sessions courtes et lisibles** : une decision ou une etape mesuree a la
    fois. La complexite qui l'a demotive fin aout venait d'un style de
    travail a dix pistes paralleles. Termine chaque seance par : ce qui est
    fait, ce qui tourne seul, ce qu'il a a faire (souvent rien), la
    question ouverte s'il y en a une.

## Contraintes fermes

- Zero euro, zero authentification, donnees publiques seulement.
- Rien n'entre en detection sans confirmation de Vincent. Les scripts qui
  modifient le dictionnaire ou la surveillance SIMULENT par defaut et
  n'ecrivent qu'avec `--appliquer`.
- Une mesure non ecrite n'existe pas : tout script qui mesure ecrit un
  rapport horodate dans `recherche/`.
- `acquis/` est en lecture seule. L'ancien dossier OneDrive est une archive.
- Rien ne se publie sans verification humaine et courrier prealable.

## Au debut de chaque seance

1. Lire `ETAT.md` « REPRENDRE ICI ».
2. Ouvrir le dernier `recherche/facteur_*.md` (la tournee de nuit) et les
   rapports des taches lancees en arriere-plan (`completion_videos_*`,
   `transcription_*`) : dire a Vincent en deux phrases ce qui s'est passe.
3. Verifier `A_JUGER.xlsx` : s'il contient des verdicts non recoltes, lancer
   la recolte et repondre aux notes avant toute autre chose.
4. Proposer UNE etape, rattachee a un des trois axes, avec ses nombres.

## Environnement

Windows 11, Python 3.14, console en cp1252 : lancer les scripts avec
`PYTHONIOENCODING=utf-8`. Tache planifiee Windows « Veille filiere -
facteur » a 3h00. Les scripts longs (pages, transcriptions) se lancent en
processus detache (`Start-Process`), pas en tache de fond de session (tuee
a 10 minutes). Base : `donnees/veille.sqlite`, hors git. Depot :
github.com/Tamateatea/veille-filiere.
