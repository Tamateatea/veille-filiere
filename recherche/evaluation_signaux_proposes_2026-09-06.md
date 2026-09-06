# Evaluation des signaux `propose` du dictionnaire — 2026-09-06

Produit par un script d'evaluation (scratchpad de session, fonctions `normaliser_positionnel` et `extraire` importees de `outils/detecter.py`, regex construites selon la regle exacte de `charger_signaux`). **Rien n'a ete modifie** : ni le dictionnaire, ni la base — evaluation seulement, pour que Vincent confirme ou rejette signal par signal (critere 11).

Corpus : les **53 381 videos** de `donnees/veille.sqlite` (titre + description), MESURE ce fichier. Verdicts croises : `recherche/jugements_reference_2026-09-06.csv` + `donnees/jugements_recoltes.csv` (437 videos jugees uniques).

Signaux `propose` evalues : **105** (dont 2 lignes en double au dictionnaire : `Label Rouge` et `Les produits tripiers`, INTERBEV).

## Synthese par recommandation

| Recommandation | Signaux |
|---|---:|
| confirmer (fort) | 6 |
| confirmer (faible) | 17 |
| rejeter | 46 |
| sans occurrence — sans objet pour l'instant | 36 |
| **Total** | **105** |

### Les confirmer (fort)

- **Les Produits Laitiers** (CNIEL) — 61 occ. — 15 'collaboration remuneree' jugees meme entite (Inoxtag/KAIZEN 'Merci a mes partenaires ... Les Produits Laitiers', Check 'en partenariat avec') ; les 44 hors sujet sont le bruit attendu, a filtrer par les indices commerciaux.
- **Nos amis pour la vie** (CNIEL) — 21 occ. — 10 'collaboration remuneree' jugees meme entite sur 20 ; extraits explicites 'Toujours en partenariat avec nos amis pour la vie: Les Produits Laitiers' (Check, Juste Zoe).
- **MIV 2021** (INTERBEV) — 6 occ. — 6/6 videos jugees 'collaboration remuneree' (operation Made in Viande 2021 avec Florian On Air).
- **Actimel** (Actimel) — 4 occ. — Extraits explicites 'Partenariat remunere avec Actimel' (Inoxtag, x2) + jeu-concours Studio Danielle ; aucune video jugee mais la preuve est dans l'extrait.
- **Le Porc Francais** (INAPORC) — 2 occ. — 2/2 videos jugees 'collaboration remuneree' meme entite (FlorianOnAir : 'Video sponsorisee par Le Porc Francais', 'En partenariat avec Le Porc Francais').
- **Volaille Francaise** (ANVOL) — 2 occ. — 1 'collaboration remuneree' jugee meme entite sur 2 (FlorianOnAir 'Mars, c'est le mois de la Volaille Francaise'), l'autre 'je ne sais pas'.

### Les confirmer (faible)

- **Elle & Vire** (Elle & Vire) — 22 occ. — Recette CuisineAZ 'beurre doux Elle & Vire de Conde-sur-Vire' (langage marketing = placement plausible) ; le reste est du B2B etranger.
- **Danette** (Danette) — 18 occ. — Mcfly et Carlito 'On verifie le slogan de @danette' : interaction directe avec la marque, mais format editorial multi-marques possible ; a faire juger.
- **Babybel** (Babybel) — 14 occ. — Contenus gaming Doigby centres sur la marque (map Fortnite 'Babybel Reloaded', Farming Simulator 'AVEC BABYBEL') : collaboration tres plausible ; aucun verdict.
- **La Vache qui rit** (La Vache qui rit) — 7 occ. — Video Nota Bene consacree a l'anniversaire de la marque : collaboration plausible mais non declaree dans l'extrait (SUPPOSE) ; le reste est du generique.
- **Yoplait** (Yoplait) — 5 occ. — Stream Kameto avec jeu-concours grandjeuyop.yoplait.fr : operation commerciale plausible ; les autres occurrences sont un ingredient generique.
- **Entremont** (Entremont) — 2 occ. — Recettes CuisineAZ construites sur le produit nomme ('sauce 3 Fromages Entremont') : placement plausible ; aucun verdict.
- **Galbani** (Galbani) — 2 occ. — Toscane Lucas 'Je cuisine avec le mascarpone @Galbani France' : placement createur plausible ; aucun verdict.
- **Herta** (Herta) — 2 occ. — JohanPapz 'Herta m'a mis au defi de faire des pizzas' : defi de marque typique d'un partenariat ; 2 occurrences, aucun verdict.
- **Le Gaulois** (Le Gaulois) — 2 occ. — Recette createur 'grace a Le Gaulois' (placement plausible), mais homonymes presents ('BARDIX LE GAULOIS').
- **Leporc** (INAPORC) — 2 occ. — Videos LeStream avec lien leporc.com et #cestbondanslecochon : campagne INAPORC chez des createurs ; aucun verdict sur ces videos.
- **Les produits tripiers** (INTERBEV) — 2 occ. — Recette 'C'est meilleur quand c'est bon' citant 'Les produits tripiers aussi' : echo plausible d'une campagne INTERBEV ; 1 video jugee hors sujet. Ligne en double au dictionnaire.
- **Les produits tripiers** (INTERBEV) — 2 occ. — Recette 'C'est meilleur quand c'est bon' citant 'Les produits tripiers aussi' : echo plausible d'une campagne INTERBEV ; 1 video jugee hors sujet. Ligne en double au dictionnaire.
- **Saint Agur** (Saint Agur) — 2 occ. — Recette CuisineAZ titree 'a la creme de Saint Agur' : placement plausible ; aucun verdict.
- **Charal** (Charal) — 1 occ. — Aypierre 'Le Buildboard Challenge minecraft de Charal' : operation de marque avec un createur ; occurrence unique, aucun verdict.
- **Radio Sexe** (CNIEL) — 1 occ. — 1 occurrence (le son officiel chez Kameto) ; le podcast lui-meme est RAPPORTE sponsorise par le CNIEL (StreetPress). Peu de rendement en description, mais zero bruit.
- **Socopa** (Socopa) — 1 occ. — FlorianOnAir jury de la 'Coupe de France de Burger by Socopa' : operation de marque, invitation plausible ; occurrence unique.
- **Soignon** (Soignon) — 1 occ. — Recette CuisineAZ titree sur le produit ('buche aux herbes de Provence Soignon') : meme motif de placement qu'Entremont.

## Les 20 signaux les plus frequents, avec un contexte

| Signal | Entite | Occ. | Verdicts | Recommandation | Contexte d'exemple |
|---|---|---:|---|---|---|
| Societe | Societe | 1379 | 35 jugees: hors sujet=28 \| collaboration remuneree=6 \| je ne sais pas=1 (meme … | rejeter | [Michou] …entre croûtons ! Ça faisait longtemps ! Dans cette vidéo on va jouer au jeu de société Bomb Island que mes frères ont crées ! C'est un Battle Royale avec des tr… |
| Marie | Marie | 868 | 7 jugees: hors sujet=7 (meme entite: hors sujet=5) | rejeter | [SQUEEZIE] …in Tarrou, Théo Meunier, Garance Sanders, Johan Ravaute ⏎ Photographe plateau : Marie Flament ⏎  ⏎ Chef de projet PlaniPresse : Martin Victor Pujebet ⏎ Direct… |
| President | President | 702 | 8 jugees: hors sujet=7 \| je ne sais pas=1 (meme entite: hors sujet=2) | rejeter | [VICE] …he Pagans to join their rivals, the Sutar Soldiers, where he was appointed Vice President. ⏎  ⏎ Watch this full episode of the @VICE-TV docuseries, United Gangs o… |
| Maitre Coq | Maitre Coq | 171 | 3 jugees: je ne sais pas=3 | rejeter | [Maître CoQ] …Pour cette recette, il vous faudra :  ⏎  ⏎ •  50 g de lamelles kebab surgelées Maître CoQ ⏎ •  1 galette wrap  ⏎ •  50 g de trio de poivrons surgelés ⏎ •  1… |
| Foie Gras | CIFOG | 130 | 86 jugees: hors sujet=81 \| je ne sais pas=3 \| mention sans collaboration=2 (me… | rejeter | [Valouzz] Mon premier Noël en tant que Papa 🎅🎄 ⏎ Nom du produit: Foie gras de canard entier et Fine de Bretagne ⏎  ⏎ Lien du produit: ⏎ https://conserverie-artisanale-bre… |
| Tartare | Tartare | 128 | 4 jugees: hors sujet=4 | rejeter | [NYT Cooking] …Menu \| NYT Cooking ⏎ Get Wolfgang Puck’s Oscar recipes (for free!):  ⏎ Spicy Tuna Tartare in Sesame Miso Cones: https://nyti.ms/40lUM6q ⏎ Chicken Potpie: … |
| Veloute | Veloute | 85 | 3 jugees: hors sujet=2 \| collaboration remuneree=1 | rejeter | [Juste Zoé] …es habitudes au quotidien de génération en génération. Danone Le Nature, Danone Velouté Nature et Danone Skyr Nature so |
| Boursin | Boursin | 82 | aucune video jugee | rejeter | [Kemar] Un déchet humain se confesse autour d’une pizza boursin viande hachée |
| Fleury Michon | Fleury Michon | 61 | aucune video jugee | rejeter | [Fleury Michon] FICT x FLEURY MICHON : Julien, manager service maintenance ⏎ FICT x FLEURY MICHON : Julien, manager service maintenance |
| Les Produits Laitiers | CNIEL | 61 | 62 jugees: hors sujet=45 \| collaboration remuneree=16 \| je ne sais pas=1 (meme… | confirmer (fort) | [Inoxtag] …. Mathis) ⏎ Merci à mes partenaires air up, Nike, Deezer, Fitness Park, Erborian, Les Produits Laitiers, Orange, et Therm-ic de m’avoir accompagné et soutenu d… |
| Activia | Activia | 38 | aucune video jugee | rejeter | [Activia France] Activia Kéfir : un mix unique de levures de kéfir traditionnelles et de milliards de probiotiques |
| Gervais | Gervais | 24 | aucune video jugee | rejeter | [Juste Zoé] QUI DÉCOUVRIRA NOS SECRETS ? ft. Iris Mittenaere   Chloë Gervais, Paul Duchemin et Anna RVR 🔍 ⏎ Aujourd’hui, j’ai 24 ans 🎉 Pour l’occasion, j’ai invité mes co… |
| Elle & Vire | Elle & Vire | 22 | aucune video jugee | confirmer (faible) | [CuisineAZ.com] …s de cuisson : 15 min ⏎  ⏎ Ingrédients pour le crumble : ⏎ - 80g de beurre doux Elle & Vire de Condé-sur-Vire froid ⏎ - 80g de farine ⏎ - 80g de sucre ⏎ … |
| Nos amis pour la vie | CNIEL | 21 | 20 jugees: collaboration remuneree=10 \| hors sujet=10 (meme entite: collaborati… | confirmer (fort) | [Juste Zoé] …lection?utm_source=Influence_Youtube&utm_medium=cpc&utm_campaign=JusteZo_G ⏎  ⏎ Nos amis pour la vie : https://www.nosamispourlavie.org ⏎  ⏎ Mes réseaux :  ⏎… |
| Label Rouge | INTERBEV | 20 | 1 jugees: hors sujet=1 | rejeter | [FlorianOnAir] …tel de luxe, à Paris dans le 16ème. ⏎ Au menu : arancini au safran et au saumon Label Rouge, tartare de dorade royale, sole étuvée , ... ⏎  ⏎ Le resto : B… |
| Label Rouge | INTERBEV | 20 | 1 jugees: hors sujet=1 | rejeter | [FlorianOnAir] …tel de luxe, à Paris dans le 16ème. ⏎ Au menu : arancini au safran et au saumon Label Rouge, tartare de dorade royale, sole étuvée , ... ⏎  ⏎ Le resto : B… |
| Danette | Danette | 18 | aucune video jugee | confirmer (faible) | [Mcfly et Carlito] On vérifie le slogan de @danette |
| CHAUD ! | CNIEL | 17 | 11 jugees: hors sujet=9 \| je ne sais pas=2 (meme entite: hors sujet=9 \| je ne … | rejeter | [Produits Laitiers] CHAUD! - Épisode 4 (avec Jeffrey Cagnes) ⏎ Dans ce 4ᵉ épisode de la série CHAUD !, la brigade fait étape à Saint-Étienne pour suivre le parcours du la… |
| Loue | Loue | 16 | 1 jugees: hors sujet=1 | rejeter | [Michou] …ns cette video on s’est fait un Cache Cache IRL Grandeur Nature, j’ai carrément loué un Village entier dans le theme du Far West ! Donc avec Raska, Nicotine, Do… |
| Babybel | Babybel | 14 | aucune video jugee | confirmer (faible) | [Doigby] 🚜 ON SOUTIENT LES AGRICULTEURS AVEC BABYBEL ! (Farming Simulator) ⏎ 💙 → Je sors mon chapeau de paille pour devenir agriculteur sur Farming Simulator ! On va prod… |

Detail complet, signal par signal (105 lignes) : `recherche/evaluation_signaux_proposes_2026-09-06.csv` (colonnes : signal, entite, statut_actuel, occurrences, verdicts_croises, recommandation, justification, exemples).

Notes de lecture :

- « occurrences » = nombre de videos dont titre+description matchent le signal (frontieres de mot, insensible aux accents et a la casse — la regle exacte de `detecter.py`).
- « meme entite » dans les verdicts = la video a ete jugee pour l'entite du signal ; les autres verdicts portent sur la meme video mais une autre entite.
- Beaucoup de signaux de series (CIFOG, INTERBEV, CNIEL) ne vivent que sur les chaines vitrines des lobbies, deja routees hors detection : les confirmer n'apporterait rien, d'ou « rejeter » malgre des occurrences reelles.
