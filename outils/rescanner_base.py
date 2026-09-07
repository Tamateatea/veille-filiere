# -*- coding: utf-8 -*-
"""Re-balaye TOUTES les videos de la base avec le dictionnaire actuel.

A lancer apres tout changement du dictionnaire (signal ajoute, confirme,
declasse, retire). C'est la piece qui rend les changements RETROACTIFS :
le facteur n'analyse que le nouveau, ce script re-analyse tout le stock.

La table `detections` est reconstruite entierement ; les verdicts humains
(fichiers recherche/ et donnees/jugements_recoltes.csv) ne sont jamais
touches. Rapport horodate dans recherche/.
"""

import datetime as dt
import sqlite3
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from detecter import analyser, canaux_vitrines_depuis, charger_signaux, \
    normaliser_positionnel  # noqa: E402

RACINE = Path(__file__).resolve().parent.parent
CHEMIN_BASE = RACINE / "donnees" / "veille.sqlite"
DOSSIER_RECHERCHE = RACINE / "recherche"


def principal():
    signaux, _ = charger_signaux()
    vitrines = canaux_vitrines_depuis(signaux)
    base = sqlite3.connect(CHEMIN_BASE)
    maintenant = dt.datetime.now().isoformat(timespec="seconds")

    colonnes_comptes = [c[1] for c in base.execute("PRAGMA table_info(comptes)")]
    col_vitrine = ("c.entite_vitrine" if "entite_vitrine" in colonnes_comptes
                   else "NULL")
    videos = base.execute(
        f"SELECT v.video_id, v.titre, v.description, c.nom, {col_vitrine} "
        "FROM videos v JOIN comptes c ON c.compte_id = v.compte_id").fetchall()

    lignes = []
    par_entite = Counter()
    n_vitrines = 0
    for video_id, titre, description, nom_compte, entite_vitrine in videos:
        # Vitrine par identifiant (chaine officielle de marque) ou par nom.
        if entite_vitrine or (
                normaliser_positionnel(nom_compte or "").lstrip("@") in vitrines):
            n_vitrines += 1
            continue
        texte = f"{titre or ''}\n{description or ''}"
        for d in analyser(texte, signaux):
            par_entite[d["entite"]] += 1
            lignes.append((video_id, d["entite"], d["signaux"],
                           d["types_signaux"], d["force"],
                           d["indices_commerciaux"], d["extrait"],
                           maintenant))

    with base:
        # Ne reconstruit que les detections issues des descriptions : les
        # detections orales (source='transcription') appartiennent a
        # second_rideau.py, qui est lui-meme rejouable.
        colonnes = [c[1] for c in base.execute("PRAGMA table_info(detections)")]
        if "source" in colonnes:
            base.execute("DELETE FROM detections WHERE source = 'description'")
        else:
            base.execute("DELETE FROM detections")
        base.executemany(
            "INSERT OR IGNORE INTO detections (video_id, entite, signaux, "
            "types_signaux, force, indices_commerciaux, extrait, "
            "detectee_le) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", lignes)
    base.close()

    horodatage = dt.datetime.now().strftime("%Y-%m-%d_%H%M")
    chemin_rapport = DOSSIER_RECHERCHE / f"rescan_{horodatage}.md"
    with open(chemin_rapport, "w", encoding="utf-8") as f:
        f.write(f"# Re-balayage complet de la base — {maintenant}\n\n")
        f.write("Produit par `outils/rescanner_base.py` avec le "
                f"dictionnaire actuel ({len(signaux)} signaux actifs).\n\n")
        f.write("| | |\n|---|---:|\n")
        f.write(f"| Videos re-analysees | {len(videos) - n_vitrines} |\n")
        f.write(f"| Videos de vitrines ecartees | {n_vitrines} |\n")
        f.write(f"| Detections reconstruites | {len(lignes)} |\n\n")
        for entite, n in par_entite.most_common():
            f.write(f"- {entite} : {n}\n")

    print(f"Videos re-analysees : {len(videos) - n_vitrines} "
          f"(+{n_vitrines} vitrines ecartees)")
    print(f"Detections reconstruites : {len(lignes)}")
    print(f"Ecrit : {chemin_rapport}")


if __name__ == "__main__":
    principal()
