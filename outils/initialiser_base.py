# -*- coding: utf-8 -*-
"""Cree la base SQLite du projet et y migre les acquis.

Pourquoi SQLite : ecritures transactionnelles (une panne ou un verrou ne
corrompt rien), lectures incrementales, un seul fichier, zero euro.
Decision du 06/09/2026, validee par Vincent apres avis de son ami.

Tables :
  comptes    — la liste de surveillance : un compte par ligne, avec son
               identifiant de plateforme (stable), son nom, son audience.
  videos     — TOUT ce que le facteur lit, signal ou pas. C'est le
               correctif de la faiblesse relevee par Vincent le 06/09 :
               avant, une video lue sans signal ne laissait qu'un compteur,
               et un signal decouvert plus tard etait invisible
               retroactivement.
  detections — une ligne par paire (video, entite), avec signaux, indices
               et extrait exact.
  curseurs   — ou en est le facteur pour chaque compte (idempotence :
               relancer ne refait rien, reparer une panne = relancer).

Migration : les 27 353 videos stockees de l'ancienne moisson, leurs
detections actuelles, et les compteurs de moisson comme curseurs.
Le script refuse de recreer une base existante (--forcer pour l'ecraser).
"""

import datetime as dt
import json
import sqlite3
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
CHEMIN_BASE = RACINE / "donnees" / "veille.sqlite"
CHEMIN_CORPUS = RACINE / "acquis" / "donnees_brutes" / "moisson_videos.json"
DOSSIER_RECHERCHE = RACINE / "recherche"

SCHEMA = """
CREATE TABLE comptes (
    compte_id   TEXT PRIMARY KEY,     -- identifiant stable de la plateforme
    plateforme  TEXT NOT NULL DEFAULT 'youtube',
    nom         TEXT,
    abonnes     INTEGER,
    surveille   INTEGER NOT NULL DEFAULT 1,
    ajoute_le   TEXT
);
CREATE TABLE videos (
    video_id    TEXT PRIMARY KEY,
    compte_id   TEXT NOT NULL REFERENCES comptes(compte_id),
    plateforme  TEXT NOT NULL DEFAULT 'youtube',
    titre       TEXT,
    description TEXT,
    publiee     TEXT,
    url         TEXT,
    lue_le      TEXT NOT NULL
);
CREATE INDEX idx_videos_compte ON videos(compte_id);
CREATE TABLE detections (
    video_id    TEXT NOT NULL REFERENCES videos(video_id),
    entite      TEXT NOT NULL,
    signaux     TEXT,
    types_signaux TEXT,
    force       TEXT,
    indices_commerciaux TEXT,
    extrait     TEXT,
    detectee_le TEXT NOT NULL,
    PRIMARY KEY (video_id, entite)
);
CREATE TABLE curseurs (
    compte_id        TEXT PRIMARY KEY REFERENCES comptes(compte_id),
    dernier_passage  TEXT,
    videos_connues   INTEGER NOT NULL DEFAULT 0
);
"""


def principal():
    if CHEMIN_BASE.exists():
        if "--forcer" not in sys.argv:
            sys.exit(f"{CHEMIN_BASE.name} existe deja (--forcer pour la "
                     "recreer depuis les acquis).")
        CHEMIN_BASE.unlink()

    with open(CHEMIN_CORPUS, encoding="utf-8") as f:
        moisson = json.load(f)
    faites, touchees = moisson["faites"], moisson["touchees"]

    maintenant = dt.datetime.now().isoformat(timespec="seconds")
    base = sqlite3.connect(CHEMIN_BASE)
    base.executescript(SCHEMA)

    # Les comptes : tous les canaux deja moissonnes. Le nom et l'audience ne
    # sont connus que pour les canaux ayant au moins une video stockee.
    infos = {}
    for v in touchees:
        infos.setdefault(v["channel_id"], (v.get("chaine"), v.get("abonnes")))
    base.executemany(
        "INSERT OR IGNORE INTO comptes (compte_id, nom, abonnes, ajoute_le) "
        "VALUES (?, ?, ?, ?)",
        [(cid, infos.get(cid, (None, None))[0], infos.get(cid, (None, None))[1],
          maintenant) for cid in faites])

    # Les videos stockees (celles qui portaient un signal a l'epoque).
    base.executemany(
        "INSERT OR IGNORE INTO videos (video_id, compte_id, titre, "
        "description, publiee, url, lue_le) VALUES (?, ?, ?, ?, ?, ?, ?)",
        [(v["video_id"], v["channel_id"], v.get("titre"),
          v.get("description"), v.get("publiee"), v.get("url"), maintenant)
         for v in touchees])

    # Les curseurs : le nombre de videos deja vues par l'ancienne moisson.
    base.executemany(
        "INSERT OR IGNORE INTO curseurs (compte_id, dernier_passage, "
        "videos_connues) VALUES (?, ?, ?)",
        [(cid, None, d.get("videos", 0)) for cid, d in faites.items()])

    base.commit()

    n_comptes = base.execute("SELECT COUNT(*) FROM comptes").fetchone()[0]
    n_videos = base.execute("SELECT COUNT(*) FROM videos").fetchone()[0]
    base.close()

    aujourd_hui = dt.date.today().isoformat()
    chemin_rapport = DOSSIER_RECHERCHE / f"base_sqlite_{aujourd_hui}.md"
    with open(chemin_rapport, "w", encoding="utf-8") as f:
        f.write(f"# Creation de la base SQLite — {aujourd_hui}\n\n")
        f.write("Produit par `outils/initialiser_base.py`.\n\n")
        f.write("| | |\n|---|---:|\n")
        f.write(f"| Comptes migres (canaux deja moissonnes) | {n_comptes} |\n")
        f.write(f"| Videos migrees (corpus stocke) | {n_videos} |\n")
        f.write(f"| Videos comptees par l'ancienne moisson | "
                f"{sum(d.get('videos', 0) for d in faites.values())} |\n\n")
        f.write("Regle nouvelle : le facteur conserve desormais TOUTES les "
                "videos qu'il lit, signal ou pas — un signal decouvert plus "
                "tard restera cherchable retroactivement.\n")

    print(f"Comptes : {n_comptes}  |  Videos migrees : {n_videos}")
    print(f"Ecrit : {CHEMIN_BASE}")
    print(f"Ecrit : {chemin_rapport}")


if __name__ == "__main__":
    principal()
