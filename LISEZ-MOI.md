# veille-filiere

Outil de veille des collaborations commerciales remunerees entre createurs de
contenu et les filieres viande, lait et oeufs. Fonde le 6 septembre 2026, en
reprise propre du projet `InfluencersxMeat&MilkLobbyTracker` (conserve comme
archive, plus jamais modifie).

**Le document maitre est `CONTRAT.md`** : il definit ce que « l'outil marche »
veut dire, en onze criteres verifiables par Vincent sans lire de code. Rien ne
se declare fini autrement qu'en citant ces criteres.

## La carte des dossiers

| Dossier | Contenu | Regle |
|---|---|---|
| `acquis/` | ce qui a ete conserve de l'ancien projet, copie le 06/09/2026 | **lecture seule** |
| `acquis/donnees_brutes/` | les corpus moissonnes (332 119 videos YouTube, 149 711 contenus TikTok, annonces Meta, transcriptions) | trois jours de quota API, on ne les repaie pas |
| `acquis/jugements/` | les classeurs juges par Vincent — le seul etalon de verite du projet | intouchable |
| `acquis/cartographie/` | la table d'alias et la cartographie manuelle de Vincent (`Preliminary dataset.xlsx`) | source du dictionnaire |
| `outils/` | les scripts, un par tache, noms en francais | chaque script qui mesure ecrit dans `recherche/` |
| `recherche/` | toutes les mesures, horodatees, ligne par ligne | une mesure non ecrite n'existe pas |
| `donnees/` | l'etat de l'outil (registre de ce qui a ete vu, dictionnaire compile) | reconstructible |

## Les trois regles reprises de l'ancien projet

1. **Etiqueter chaque affirmation** : MESURE (nommer le fichier), RAPPORTE
   (citer la source), SUPPOSE (rien derriere). Jamais un chiffre sans le
   fichier qui le produit.
2. **L'ancien journal est une carte, pas une preuve.** Tout savoir herite se
   re-verifie sur les fichiers bruts au moment de s'en servir.
3. **On ne soumet a un humain que des entites propres** — un compte, un nom,
   une plateforme — jamais un fragment de texte brut.
