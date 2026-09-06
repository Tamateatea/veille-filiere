# Chaines YouTube officielles des marques et groupes — 2026-09-06

Resolution par pages publiques youtube.com/@pseudo (lien canonical
uniquement, 0,4 s de pause, aucune authentification). Detail ligne
par ligne : `recherche/comptes_marques_2026-09-06.csv`. Donnees
brutes des 298 requetes : deux JSONL de session (scratchpad).

**Tout ceci est une PROPOSITION (critere 11 du contrat)** : rien
n'a ete ecrit dans DICTIONNAIRE.xlsx ni dans la base SQLite.

## Synthese (MESURE — comptes_marques_2026-09-06.csv)

| | entites |
|---|---:|
| Marques + groupes testes | 70 |
| Chaine trouvee, certitude **sur** | 29 |
| Chaine trouvee, **a verifier** | 16 |
| **Introuvables** par pseudo | 25 |

Certitude « sur » = la description de la chaine identifie la marque,
ou le titre est marque+France et le nom est trop distinctif pour un
homonyme credible. « a verifier » = chaine resolue mais rien dans le
titre/la description ne prouve l'officialite.

## Les 5 plus grosses chaines trouvees (certitude sur)

| marque | chaine | abonnes |
|---|---|---|
| Le Gaulois | Le Gaulois (@legaulois) | 57,5 k abonnés |
| Galbani | Galbani (@galbani) | 25,6 k abonnés |
| Actimel | Actimel (@actimel) | 12,2 k abonnés |
| Danette | DanetteFrance (@danette) | 11,2 k abonnés |
| Lactel | Lactel France (@lactelfrance) | 10,1 k abonnés |

## Les introuvables

| entite | pseudos testes | pourquoi |
|---|---|---|
| Bigard | @bigard, @bigardfrance, @bigardfr, @bigardofficiel, @groupebigard, @bigardviandes | aucun candidat ne resout |
| Laita | @laita, @laitafrance, @laitafr, @laitaofficiel, @groupelaita, @laitagroupe | laita/laitafrance/groupelaita... ne resolvent pas |
| Pilgrim's | @pilgrims, @pilgrimsfrance, @pilgrimsfr, @pilgrimsofficiel | pilgrims* ne resout pas |
| Savencia | @savencia, @savenciafrance, @savenciafr, @savenciaofficiel, @savenciafromagedairy, @savenciagroupe | savencia*, savenciafromagedairy ne resolvent pas |
| Sicarev | @sicarev, @sicarevfrance, @sicarevfr, @sicarevofficiel, @groupesicarev | sicarev*, groupesicarev ne resolvent pas |
| Sodiaal | @sodiaal, @sodiaalfrance, @sodiaalfr, @sodiaalofficiel, @sodiaalunion, @groupesodiaal | sodiaal*, sodiaalunion ne resolvent pas |
| T'Rhea | @trhea | @trhea est une personne (TRHEA EBOUELE), ecarte |
| Bridel | @bridel, @bridelfrance, @bridelfr, @bridelofficiel | bridel* ne resout pas |
| Broceliande | @broceliande | @broceliande = guide touristique de la foret, homonyme ; rien d'autre |
| Elle & Vire | @ellevire, @elleetvire, @ellevirefrance | @ellevire est une personne ; elleetvire/ellevirefrance ne resolvent pas |
| Entremont | @entremont, @entremontfrance, @entremontfr, @entremontofficiel | @entremont est une personne ; rien d'autre |
| Gastronome | @gastronome, @gastronomefrance, @gastronomefr, @gastronomeofficiel | gastronome* ne resout pas |
| Gervais | @gervais, @gervaisfrance, @gervaisfr, @gervaisofficiel | gervais* ne resout pas |
| Marie | @marie, @mariefrance, @mariefr | homonymie massive sur le prenom ; @marie/@mariefr sont des personnes |
| Paysan Breton | @paysanbreton, @paysanbretonfrance, @paysanbretonfr, @paysanbretonofficiel, @paysan, @paysanfrance, @paysanfr, @paysanofficiel | @paysanbreton est une personne ; les variantes ne resolvent pas |
| Pere Dodu | @peredodu, @peredodufrance, @peredodufr, @peredoduofficiel, @pere, @perefrance, @perefr, @pereofficiel | peredodu* ne resout pas ; @pere* sont des personnes |
| Sabeval | @sabeval | @sabeval est un joueur Minecraft, ecarte |
| Saint Agur | @saintagur, @saintagurfrance, @saintagurfr, @saintagurofficiel, @saint, @saintfrance, @saintfr, @saintofficiel | saintagur* ne resout pas |
| Saint Moret | @saintmoret, @saintmoretfrance, @saintmoretfr, @saintmoretofficiel, @saint, @saintfrance, @saintfr, @saintofficiel | saintmoret* ne resout pas ; @saintmoret est une personne |
| Salakis | @salakis, @salakisfrance | @salakis est une chaine d'humour PC ('Salakis CPC'), ecarte ; salakisfrance ne resout pas |
| Soignon | @soignon, @soignonfrance, @soignonfr, @soignonofficiel | soignon* ne resout pas |
| Taillefine | @taillefine, @taillefinefrance, @taillefinefr | @taillefine = 'taille fine', particulier ; variantes ne resolvent pas |
| Tartare | @tartare, @tartarefrance, @tartarefr, @tartareofficiel | @tartare est une personne ; tartarefrance ne resout pas |
| Tendriade | @tendriade, @tendriadefrance, @tendriadefr, @tendriadeofficiel | tendriade* ne resout pas |
| Veloute | @veloute, @veloutefrance, @veloutefr, @velouteofficiel | @veloute est une personne ; variantes ne resolvent pas |

## Pieges rencontres (pour la suite)

- Le pseudo « naturel » d'une marque est souvent squatte par un
  particulier : @charal, @kiri, @ldc, @loue, @marie, @salakis,
  @sabeval, @tartare, @veloute, @vandrie sont des personnes.
- Trois chaines officielles trouvees ne sont PAS francaises :
  Galbani (italienne), Leerdammer (allemande), Yoplait (americaine).
- Le premier `channelId` du HTML est une chaine recommandee ;
  seul le `<link rel="canonical">` fait foi (piege deja verifie
  dans outils/integrer_propositions.py).
