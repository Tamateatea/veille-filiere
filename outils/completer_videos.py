# -*- coding: utf-8 -*-
"""Complete une video depuis sa page publique YouTube : description entiere
et case « Inclut une communication commerciale ».

Pourquoi (07/09/2026, verdicts de Vincent) :
  - 13 644 videos de l'ancienne moisson ont une description TRONQUEE a
    900 caracteres. Les mentions « collaboration commerciale » placees en
    fin de description y sont invisibles (cas Encuisineaugustine x Le
    Gaulois : la mention etait a 800 caracteres, hors extrait).
  - La case cochee par le createur (« Inclut une communication
    commerciale ») est une information que l'humain qui juge veut voir
    (demande de Vincent). Elle n'est pas dans le flux RSS ni dans l'API :
    seule la page publique la porte (marqueur `paidContentOverlayRenderer`,
    deja utilise et mesure dans l'ancien projet : 91 % de precision).

Zero quota, zero authentification : une requete HTTP par video, une
seconde de pause. Idempotent : une video completee porte
`description_complete_le` et n'est pas relue (sauf --refaire).

Perimetres :
  --candidats (defaut)  les videos qui ont une detection, plus celles deja
                        jugees par Vincent (pour pouvoir MESURER la case)
  --tronquees           + toutes les descriptions de 900 caracteres
  --limite N            s'arreter apres N pages (essai)

Rapport horodate dans recherche/.
"""

import argparse
import csv
import datetime as dt
import json
import re
import sqlite3
import time
import urllib.error
import urllib.request
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
CHEMIN_BASE = RACINE / "donnees" / "veille.sqlite"
DOSSIER_RECHERCHE = RACINE / "recherche"
CHEMIN_RECOLTES = RACINE / "donnees" / "jugements_recoltes.csv"

MARQUEUR_DECLARATION = "paidContentOverlayRenderer"
MOTIF_DESCRIPTION = re.compile(r'"shortDescription":"((?:[^"\\]|\\.)*)"')
PAUSE = 1.0
DELAI_HTTP = 20


def lire_page(video_id):
    """Rend (description complete, case cochee) depuis la page publique."""
    requete = urllib.request.Request(
        f"https://www.youtube.com/watch?v={video_id}",
        headers={"User-Agent": "Mozilla/5.0 (veille-filiere/1.0)",
                 "Accept-Language": "fr-FR,fr;q=0.9"})
    with urllib.request.urlopen(requete, timeout=DELAI_HTTP) as reponse:
        page = reponse.read().decode("utf-8", errors="replace")
    m = MOTIF_DESCRIPTION.search(page)
    description = json.loads('"' + m.group(1) + '"') if m else None
    declaration = 1 if MARQUEUR_DECLARATION in page else 0
    return description, declaration


def preparer_colonnes(base):
    colonnes = [c[1] for c in base.execute("PRAGMA table_info(videos)")]
    with base:
        if "description_complete_le" not in colonnes:
            base.execute("ALTER TABLE videos ADD COLUMN "
                         "description_complete_le TEXT")
        if "declaration_commerciale" not in colonnes:
            base.execute("ALTER TABLE videos ADD COLUMN "
                         "declaration_commerciale INTEGER")


def videos_jugees():
    ids = set()
    for chemin in list(DOSSIER_RECHERCHE.glob("jugements_reference_*.csv")) \
            + [CHEMIN_RECOLTES]:
        if chemin.exists():
            with open(chemin, encoding="utf-8-sig") as f:
                ids |= {j["video_id"] for j in csv.DictReader(f) if j["video_id"]}
    return ids


def principal():
    parseur = argparse.ArgumentParser()
    parseur.add_argument("--tronquees", action="store_true")
    parseur.add_argument("--refaire", action="store_true",
                         help="relit aussi les videos deja completees")
    parseur.add_argument("--limite", type=int, default=None)
    args = parseur.parse_args()

    base = sqlite3.connect(CHEMIN_BASE)
    preparer_colonnes(base)
    filtre = "" if args.refaire else "AND v.description_complete_le IS NULL"
    cibles = [r[0] for r in base.execute(
        "SELECT DISTINCT v.video_id FROM videos v "
        "JOIN detections d ON d.video_id = v.video_id "
        f"WHERE 1 {filtre}")]
    connues = set(cibles)
    for vid in videos_jugees():
        if vid not in connues:
            r = base.execute(
                "SELECT 1 FROM videos WHERE video_id = ? "
                f"{filtre.replace('v.', '')}", (vid,)).fetchone()
            if r:
                cibles.append(vid)
                connues.add(vid)
    if args.tronquees:
        for (vid,) in base.execute(
                "SELECT video_id FROM videos v WHERE length(description) = 900 "
                f"{filtre}"):
            if vid not in connues:
                cibles.append(vid)
                connues.add(vid)
    if args.limite:
        cibles = cibles[:args.limite]

    maintenant = dt.datetime.now().isoformat(timespec="seconds")
    lues = echecs = allongees = declarees = 0
    for vid in cibles:
        try:
            description, declaration = lire_page(vid)
        except (urllib.error.URLError, TimeoutError, OSError, ValueError):
            echecs += 1
            time.sleep(PAUSE)
            continue
        lues += 1
        with base:
            actuelle = base.execute(
                "SELECT description FROM videos WHERE video_id = ?",
                (vid,)).fetchone()[0] or ""
            if description is not None and len(description) > len(actuelle):
                base.execute("UPDATE videos SET description = ? "
                             "WHERE video_id = ?", (description, vid))
                allongees += 1
            base.execute(
                "UPDATE videos SET description_complete_le = ?, "
                "declaration_commerciale = ? WHERE video_id = ?",
                (maintenant, declaration, vid))
        declarees += declaration
        time.sleep(PAUSE)
    base.close()

    horodatage = dt.datetime.now().strftime("%Y-%m-%d_%H%M")
    chemin = DOSSIER_RECHERCHE / f"completion_videos_{horodatage}.md"
    with open(chemin, "w", encoding="utf-8") as f:
        f.write(f"# Completion des videos depuis les pages publiques — "
                f"{maintenant}\n\n")
        f.write("Produit par `outils/completer_videos.py` "
                f"({'candidats + jugees + tronquees' if args.tronquees else 'candidats + jugees'}).\n\n")
        f.write("| | |\n|---|---:|\n")
        f.write(f"| Videos ciblees | {len(cibles)} |\n")
        f.write(f"| Pages lues | {lues} |\n")
        f.write(f"| Echecs | {echecs} |\n")
        f.write(f"| Descriptions allongees | {allongees} |\n")
        f.write(f"| Case « communication commerciale » cochee | {declarees} |\n\n")
        f.write("Apres une completion : `python outils/rescanner_base.py` "
                "(les descriptions allongees peuvent reveler des signaux).\n")
    print(f"Ciblees : {len(cibles)} | lues : {lues} | echecs : {echecs} | "
          f"allongees : {allongees} | case cochee : {declarees}")
    print(f"Ecrit : {chemin}")


if __name__ == "__main__":
    principal()
