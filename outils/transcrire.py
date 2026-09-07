# -*- coding: utf-8 -*-
"""Transcrit ce qui est DIT dans les videos candidates (sous-titres
automatiques YouTube, via yt-dlp — pages publiques, zero quota, zero cle).

Decision de Vincent du 07/09/2026 : la transcription sert partout ou elle
renforce la certitude — pas seulement quand la description est vide
(Angelica x Actimel), aussi quand les signaux sont douteux (Doigby x
Babybel). Cout mesure : ~7 secondes par video. On ne transcrit donc que ce
qui va passer devant un humain : les videos portant une detection, plus,
pour la mesure, celles que Vincent a deja jugees.

Table `transcriptions` (video_id, langue, texte, segments, source, statut,
lue_le) : une ligne par video tentee, statut `ok` / `aucune` (pas de
sous-titres) / `echec`. Les 1 298 transcriptions heritees de l'ancien
projet (acquis/donnees_brutes/transcriptions*.json) y sont migrees a la
premiere execution, source `acquis`.

Usage :
  python outils/transcrire.py                # les candidates
  python outils/transcrire.py --jugees       # + les videos jugees
  python outils/transcrire.py --limite 10    # essai
"""

import argparse
import csv
import datetime as dt
import json
import re
import sqlite3
import subprocess
import sys
import tempfile
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from detecter import canaux_vitrines_depuis, charger_signaux, \
    normaliser_positionnel  # noqa: E402

RACINE = Path(__file__).resolve().parent.parent
CHEMIN_BASE = RACINE / "donnees" / "veille.sqlite"
DOSSIER_ACQUIS = RACINE / "acquis" / "donnees_brutes"
DOSSIER_RECHERCHE = RACINE / "recherche"
CHEMIN_RECOLTES = RACINE / "donnees" / "jugements_recoltes.csv"
FICHIERS_ACQUIS = ["transcriptions.json", "transcriptions_second_rideau.json",
                   "transcriptions_temoins.json"]
DELAI = 180
PAUSE = 4.0            # secondes entre deux videos (politesse, evite le 429)
PAUSE_APRES_429 = 90.0  # attente avant de reessayer quand YouTube freine


def preparer_table(base):
    with base:
        base.execute(
            "CREATE TABLE IF NOT EXISTS transcriptions ("
            "video_id TEXT PRIMARY KEY REFERENCES videos(video_id), "
            "langue TEXT, texte TEXT, segments TEXT, source TEXT, "
            "statut TEXT NOT NULL, lue_le TEXT NOT NULL)")


def migrer_acquis(base):
    """Les transcriptions de l'ancien projet entrent une fois, source acquis."""
    deja = {r[0] for r in base.execute("SELECT video_id FROM transcriptions")}
    connues = {r[0] for r in base.execute("SELECT video_id FROM videos")}
    n = 0
    maintenant = dt.datetime.now().isoformat(timespec="seconds")
    with base:
        for nom in FICHIERS_ACQUIS:
            chemin = DOSSIER_ACQUIS / nom
            if not chemin.exists():
                continue
            with open(chemin, encoding="utf-8") as f:
                for vid, texte in json.load(f).items():
                    if vid in deja or vid not in connues or not texte:
                        continue
                    base.execute(
                        "INSERT INTO transcriptions (video_id, langue, texte, "
                        "segments, source, statut, lue_le) "
                        "VALUES (?, 'fr', ?, NULL, ?, 'ok', ?)",
                        (vid, texte if isinstance(texte, str) else str(texte),
                         f"acquis/{nom}", maintenant))
                    deja.add(vid)
                    n += 1
    return n


def sous_titres(video_id):
    """Rend (langue, [(seconde, ligne)]) ou (None, []) sans sous-titres."""
    with tempfile.TemporaryDirectory() as d:
        r = subprocess.run(
            [sys.executable, "-m", "yt_dlp", "--skip-download",
             "--write-auto-subs", "--sub-langs", "fr.*", "--sub-format",
             "vtt", "--no-warnings", "-o", str(Path(d) / "s"),
             f"https://www.youtube.com/watch?v={video_id}"],
            capture_output=True, text=True, timeout=DELAI)
        if r.returncode != 0:
            raise RuntimeError(r.stderr.strip()[-200:])
        fichiers = [f for f in sorted(Path(d).glob("*.vtt"))
                    if "-orig" not in f.name]
        if not fichiers:
            return None, []
        langue = fichiers[0].name.split(".")[-2]
        texte = fichiers[0].read_text(encoding="utf-8", errors="replace")

    def secondes(t):
        h, m, s = t.split(":")
        return int(h) * 3600 + int(m) * 60 + float(s)

    lignes, vu = [], None
    for debut, corps in re.findall(
            r"(\d\d:\d\d:\d\d\.\d\d\d) --> \d\d:\d\d:\d\d\.\d\d\d[^\n]*\n"
            r"(.*?)(?=\n\n|\Z)", texte, re.S):
        for l in re.sub(r"<[^>]+>", "", corps).strip().splitlines():
            l = l.strip()
            if l and l != vu:
                lignes.append((round(secondes(debut)), l))
                vu = l
    return langue, lignes


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
    parseur.add_argument("--jugees", action="store_true")
    parseur.add_argument("--limite", type=int, default=None)
    args = parseur.parse_args()

    base = sqlite3.connect(CHEMIN_BASE)
    preparer_table(base)
    migrees = migrer_acquis(base)

    signaux, _ = charger_signaux()
    vitrines = canaux_vitrines_depuis(signaux)
    colonnes = [c[1] for c in base.execute("PRAGMA table_info(comptes)")]
    col_vitrine = "c.entite_vitrine" if "entite_vitrine" in colonnes else "NULL"
    # Les echecs (souvent un 429 passager) sont retentes a chaque passage.
    deja = {r[0] for r in base.execute(
        "SELECT video_id FROM transcriptions WHERE statut <> 'echec'")}
    cibles = []
    for vid, nom, ev in base.execute(
            f"SELECT DISTINCT v.video_id, c.nom, {col_vitrine} FROM videos v "
            "JOIN detections d ON d.video_id = v.video_id "
            "JOIN comptes c ON c.compte_id = v.compte_id"):
        if vid in deja or ev or \
                normaliser_positionnel(nom or "").lstrip("@") in vitrines:
            continue
        cibles.append(vid)
    if args.jugees:
        connues = {r[0] for r in base.execute("SELECT video_id FROM videos")}
        for vid in sorted(videos_jugees()):
            if vid in connues and vid not in deja and vid not in cibles:
                cibles.append(vid)
    if args.limite:
        cibles = cibles[:args.limite]

    ok = aucune = echecs = 0
    for vid in cibles:
        maintenant = dt.datetime.now().isoformat(timespec="seconds")
        try:
            langue, lignes = sous_titres(vid)
        except (RuntimeError, subprocess.TimeoutExpired, OSError) as erreur:
            if "429" in str(erreur):
                # YouTube freine : on attend, puis on reessaie une fois.
                # (Mesure du 07/09 : sans pause, 11 echecs 429 sur 20.)
                time.sleep(PAUSE_APRES_429)
                try:
                    langue, lignes = sous_titres(vid)
                    statut = "ok" if lignes else "aucune"
                    ok += bool(lignes)
                    aucune += not lignes
                except (RuntimeError, subprocess.TimeoutExpired, OSError):
                    statut, langue, lignes = "echec", None, []
                    echecs += 1
            else:
                statut, langue, lignes = "echec", None, []
                echecs += 1
        else:
            statut = "ok" if lignes else "aucune"
            ok += bool(lignes)
            aucune += not lignes
        time.sleep(PAUSE)
        with base:
            base.execute(
                "INSERT OR REPLACE INTO transcriptions (video_id, langue, "
                "texte, segments, source, statut, lue_le) "
                "VALUES (?, ?, ?, ?, 'yt-dlp sous-titres automatiques', ?, ?)",
                (vid, langue, " ".join(l for _, l in lignes) or None,
                 json.dumps(lignes, ensure_ascii=False) if lignes else None,
                 statut, maintenant))
    total = base.execute("SELECT count(*) FROM transcriptions "
                         "WHERE statut = 'ok'").fetchone()[0]
    base.close()

    horodatage = dt.datetime.now().strftime("%Y-%m-%d_%H%M")
    chemin = DOSSIER_RECHERCHE / f"transcription_{horodatage}.md"
    with open(chemin, "w", encoding="utf-8") as f:
        f.write(f"# Transcription des candidates — {horodatage}\n\n")
        f.write("Produit par `outils/transcrire.py` (sous-titres "
                "automatiques YouTube via yt-dlp, pages publiques, zero "
                "quota).\n\n| | |\n|---|---:|\n")
        f.write(f"| Transcriptions heritees migrees | {migrees} |\n")
        f.write(f"| Videos ciblees | {len(cibles)} |\n")
        f.write(f"| Transcrites | {ok} |\n")
        f.write(f"| Sans sous-titres | {aucune} |\n")
        f.write(f"| Echecs | {echecs} |\n")
        f.write(f"| **Transcriptions en base au total** | **{total}** |\n")
    print(f"migrees : {migrees} | ciblees : {len(cibles)} | ok : {ok} | "
          f"sans : {aucune} | echecs : {echecs} | total en base : {total}")
    print(f"Ecrit : {chemin}")


if __name__ == "__main__":
    principal()
