# Etat — veille-filiere

Mis a jour le **7 septembre 2026 au soir**.

## REPRENDRE ICI

**Decision prise le 07/09 a 22h : Vincent a dit « go ».** 22 signaux
confirmes, 45 rejetes (MESURE, `recherche/activation_signaux_2026-09-07.md`),
re-balayage complet fait (`recherche/rescan_2026-09-07_2200.md`, 220
detections), et **`A_JUGER.xlsx` contient 13 lignes pre-triees** par Claude
(colonnes L-N : verdict propose, certitude, raison) — 4 evidentes, 7
probables, 2 a regarder (`recherche/a_juger_2026-09-07.md`).

**En attente : les verdicts de Vincent sur ces 13 lignes.** Des qu'il les a
saisis : `python outils/relire_jugements.py` (recolte + reponse a ses
notes), puis `python outils/construire_dossiers.py` (les tables de sortie).

La simulation qui a fonde la decision reste consultable :
`recherche/simulation_activation_2026-09-07.md`.

**Deuxieme confirmation attendue, preparee et simulee** (MESURE,
`recherche/integration_comptes_marques_2026-09-07_simulation.md`) :
les 30 chaines officielles de marques trouvees avec certitude (28 pas
encore en base). Effet : chaque chaine entre en surveillance comme
VITRINE de sa marque (ce qu'elle publie part en decouverte, jamais en
detection), et son @pseudo entre au dictionnaire en « compte de marque »
confirme fort — le canal marque par @compte, celui qui a pris Nico
d'Estais x @nestleenfrance. Les noms en texte libre restent hors
detection (D-marques). Commande, apres accord :

    python outils/integrer_comptes_marques.py --appliquer
    python outils/rescanner_base.py

Point a trancher dans la foulee : les 16 chaines « a verifier » restent
dehors tant qu'un humain n'a pas confirme l'officialite
(`--inclure-a-verifier` existe mais est deconseille).

**Fait le 07/09 sans decision necessaire :**

1. La tournee nocturne du 07/09 a 3h a tourne seule : 2 899 comptes,
   322 videos nouvelles, 0 detection (`recherche/facteur_2026-09-07_0323.md`).
2. Le facteur **baptise les comptes** depuis leur flux RSS : 1 884
   comptes herites de l'ancienne moisson n'avaient qu'un identifiant
   (critere 9 : une ligne soumise porte un compte, pas un `UC…`). La
   tournee complete relancee le 07/09 au soir les nomme au passage ;
   aucun de ces comptes sans nom n'avait de detection R3 (verifie en base).
3. Les **flux en echec sont nommes** dans le rapport, avec un compteur
   d'echecs consecutifs ; a 3, le rapport PROPOSE le retrait (rien n'est
   retire seul). Les 4 echecs de chaque tournee sont 4 chaines disparues
   (HTTP 404) : LaPanny et trois comptes sans nom.
4. Le routage vitrine peut se faire **par identifiant de compte**
   (colonne `entite_vitrine`), plus seulement par nom d'affichage — dans
   le facteur et le re-balayage.
5. `detecter.compiler_signal` : la regle de correspondance d'un signal
   est exposee une fois, pour que les simulations testent un signal
   `propose` exactement comme la detection le ferait.

**Protocole etabli et valide par Vincent** : l'outil detecte -> Claude
pre-trie chaque ligne avec raison -> Vincent tranche (les evidences en
bloc, les douteux un par un). Ses notes sont recoltees et repondues
(critere 10).

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

## Le lot de validation est juge — et il recadre tout

48 verdicts (5 directs de Vincent, 43 pre-tries par Claude et valides en
bloc par lui le 06/09). MESURE, `recherche/validation_lot1_2026-09-06.md` :

| Canal | Precision de R3 sur du neuf | Rappel |
|---|---:|---:|
| interprofession | **42 %** (5/12) | 100 % |
| **marque (noms en texte libre)** | **0 %** (0/27) | — |

Le 94 % du banc historique ne generalise pas au residu jamais juge : les
bons candidats interprofession avaient deja ete absorbes par les 391
jugements, le reste est enrichi en bruit. Et le canal marque par nom nu
(« Societe », « Marie », « President ») est du bruit pur sur ce lot.

Corrections mesurees du 06/09 : indices commerciaux a moins de 500
caracteres du signal ; CHAUD !, #Viande, #Elevage, Made in Viande,
Naturellement Flexitariens et #EnjoyItsFromEurope descendus en faible.
Banc historique apres corrections : R3 a 94 % / 79 %.

Le pre-tri par Claude est valide comme mecanisme : 43 lignes triees, zero
desaccord de Vincent. Le protocole devient : l'outil detecte -> Claude
pre-trie avec raison -> Vincent tranche sur les cas non evidents.

## Le facteur nocturne existe et tourne (06/09 au soir)

- **Base SQLite** `donnees/veille.sqlite` : 2 897 comptes, 27 353 videos
  migrees + toutes les nouvelles (MESURE, `recherche/base_sqlite_2026-09-06.md`).
  Regle nouvelle : le facteur garde TOUT ce qu'il lit, signal ou pas — un
  signal decouvert plus tard restera cherchable retroactivement (demande de
  Vincent du 06/09).
- **`outils/facteur.py`** : veille incrementale par flux RSS publics (zero
  quota, zero cle), idempotente (relancer ne refait rien), une transaction
  par compte (une panne ne corrompt rien). Detection partagee via
  `detecter.analyser` — une seule fonction pour tout le projet.
- **Tache planifiee Windows « Veille filiere - facteur »**, chaque nuit a
  3h00. Essai valide sur 5 comptes (61 videos, 0 echec,
  `recherche/facteur_2026-09-06_1708.md`) ; premiere tournee complete
  lancee le 06/09 au soir.

## La boucle YouTube est complete (06/09 au soir)

Tout ce qui suit est fait et commite :

- **`MODELE_DE_SORTIE.md`** : le schema public defini AVANT l'outil
  (conseil de la soeur de Vincent et de son ami — penser depuis la sortie).
- **Tables de sortie construites** depuis les 84 verdicts humains :
  16 createurs, 16 comptes, 84 collaborations (64 CNIEL, 17 INTERBEV,
  2 INAPORC, 1 ANVOL). `donnees/sortie/`, RIEN N'EST PUBLIE.
  MESURE : `recherche/dossiers_2026-09-06.md`.
- **`rescanner_base.py`** : tout changement du dictionnaire est desormais
  retroactif sur toute la base (53 208 videos en quelques secondes).
- **A_JUGER branche sur la base** : corpus + tournees nocturnes, meme
  circuit, pre-tri de Claude.
- **CHAUD ! retire de la detection** (0 vrai, 3+ faux juges).
- **Etat stationnaire : 1 paire a juger** — Nico d'Estais x Nestle France,
  pre-triee « collaboration remuneree » (« Merci a nos partenaires…
  @nestleenfrance »). Premiere prise du canal marque par @compte.

## Prochaine etape — YOUTUBE D'ABORD (amendement au contrat)

7. **Le second rideau** : transcriptions des comptes deja suspects.
8. **Canal marque par @comptes et hashtags officiels** : enrichir le
   dictionnaire avec les comptes officiels des 52 marques (collecte
   possible par Vincent, ou par les pages publiques).
9. Confirmer un a un les 47 signaux `propose` utiles.

REPORTE apres YouTube : TikTok (critere 6), Instagram (jeton Meta).

## Decisions appliquees le 06/09 au soir

- **D-marques APPLIQUEE** (ratification globale de Vincent, « je te fais
  confiance, continuons ») : les 52 noms de marque en texte libre sont
  sortis de la detection (statut propose, reversible cellule par cellule).
  Effet : 3 736 -> **126 paires** sur le corpus gele (-97 % de bruit),
  banc interprofession inchange a 94 % / 79 %.
- **Routage vitrine maintenu** (jamais objecte).
- **PROPOSITIONS integrees** : 6 chaines YouTube ajoutees a la surveillance
  (Morgan VS, Guillaume Sanchez, Jamy, Hakim Jemili, Laura Martinez, La
  Brigade), 9 deja suivies, 39 a resoudre (Instagram/TikTok, en attente de
  ces plateformes) ; 47 signaux au dictionnaire en `propose`.
  MESURE : `recherche/integration_propositions_2026-09-06.md`.

## Interventions attendues de Vincent

1. Plus tard : le jeton Meta quand il decidera d'ouvrir Instagram.
