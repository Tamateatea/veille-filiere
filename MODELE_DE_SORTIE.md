# Modele de sortie — ce que le site publiera, champ par champ

Etabli le 7 septembre 2026, en application du conseil de la soeur de
Vincent et de son ami (06/09) : « reflechir en termes de donnees
sortantes, prevoir ce qui sera public, et adapter l'outil a ca ».
L'outil se construit desormais VERS cette forme, pas l'inverse.

**Rien de ce qui suit n'est publie aujourd'hui.** Ce fichier decrit la
cible. Toute publication reelle exige d'abord : la verification humaine
finale, le courrier prealable au createur (droit de reponse, decide le
25/08), et la decision « qui publie » (structure juridique, ouverte).

## 1. Le principe : publier des SIGNAUX, pas des verdicts

Decision de Vincent du 25/08 (archive, METHODOLOGIE 14bis.4). Une fiche
publique n'affirme pas « X est paye par Y » : elle montre le faisceau —
chaque ligne verifiable independamment par le lecteur.

## 2. Les tables plates (pas d'onglet par personne)

Quatre tables, reliees par des identifiants. Un tableur les previsualise,
une base de site les servira telles quelles. (La CNIL vise la restitution
« sous forme de profils » : des tables plates avec une fiche generee a la
demande valent mieux qu'un profil fige par personne.)

### `commanditaires` — PUBLIC
| champ | exemple | source |
|---|---|---|
| commanditaire_id | cniel | dictionnaire |
| nom | CNIEL | dictionnaire |
| type | interprofession | dictionnaire |
| rattachement | — (ou groupe industriel) | dictionnaire |
| produits | lait | dictionnaire |

### `createurs` — PUBLIC
| champ | exemple | source |
|---|---|---|
| createur_id | morgan-vs | attribue a la confirmation |
| nom_public | Morgan VS | confirme par Vincent |
| categorie | createur de contenu / chef / autre | verdict de Vincent |

### `comptes` — PUBLIC
| champ | exemple | source |
|---|---|---|
| compte_id | youtube:UCXwummU… | plateforme (stable) |
| createur_id | morgan-vs | rattachement HUMAIN, jamais automatique |
| plateforme | youtube | — |
| identifiant_public | @MorganVS | plateforme |
| audience | 1 200 000 | releve, avec date |
| audience_relevee_le | 2026-09-06 | — |

### `collaborations` — PUBLIC, une ligne par CONTENU
| champ | exemple | source |
|---|---|---|
| collaboration_id | c-000123 | attribue |
| compte_id / createur_id | … | tables ci-dessus |
| commanditaire_id | cniel | conjonction signal + verdict |
| contenu_url | https://youtube.com/watch?v=… | plateforme |
| contenu_titre | … | plateforme |
| publie_le | 2026-04-02 | plateforme |
| signaux_observes | mention en description ; remerciement ; case declaree : NON | detecteur, verifiables un a un |
| extrait | « Merci aux Produits Laitiers d'etre… » | description publique |
| degre | collaboration remuneree confirmee / faisceau fort | verdict humain |
| constate_le | 2026-09-06 | jugement |
| vues / likes (+ date de releve) | optionnel, perissable | API, releve a la demande |
| montant | vide sauf source publique | quasi jamais disponible |

## 3. Ce qui ne sera JAMAIS public

- les commentaires de travail de Vincent ;
- les candidats non confirmes, les « je ne sais pas », les propositions ;
- tout contenu de `donnees/` et `recherche/` : ce sont les coulisses ;
- les rapprochements compte -> personne non confirmes par un humain.

## 4. Ce que le site publiera sur lui-meme (transparence)

- le perimetre exact de surveillance (quels comptes, depuis quand) ;
- la methode et ses taux d'erreur mesures ;
- la date de derniere mise a jour, par source ;
- la mention du courrier prealable envoye au createur, et sa reponse
  s'il en donne une.

## 5. Consequence immediate pour l'outil

`outils/construire_dossiers.py` produit ces quatre tables a partir des
verdicts humains existants — et de rien d'autre. Si un champ manque a la
production, c'est un defaut de l'outil a corriger, pas du modele.
