# -*- coding: utf-8 -*-
"""Le second rideau : la detection dans ce qui est DIT, pas ecrit.

Certaines collaborations ne laissent aucune trace en description : le
createur remercie son commanditaire a l'oral. Les transcriptions
automatiques attrapent ca — mais elles coutent cher a produire, donc le
second rideau ne s'applique qu'aux videos deja transcrites (1 331 heritees
de l'ancien projet) et, plus tard, aux comptes deja suspects.

Ce que fait ce script :
  1. ajoute si besoin la colonne `source` a la table detections
     ('description' par defaut, 'transcription' pour l'oral) ;
  2. passe le dictionnaire actuel (via detecter.analyser, la fonction
     partagee) sur chaque transcription ;
  3. MESURE la valeur du signal oral contre les verdicts humains
     existants, sur les paires ou une transcription existe ;
  4. range les detections orales en base (rejouable : il efface et
     reconstruit uniquement source='transcription') — elles rejoignent le
     circuit A_JUGER comme les autres.

Rapport horodate dans recherche/.
"""

import csv
import datetime as dt
import json
import sqlite3
import sys
import unicodedata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from detecter import analyser, charger_signaux  # noqa: E402

RACINE = Path(__file__).resolve().parent.parent
CHEMIN_BASE = RACINE / "donnees" / "veille.sqlite"
DOSSIER_ACQUIS = RACINE / "acquis" / "donnees_brutes"
DOSSIER_RECHERCHE = RACINE / "recherche"

FICHIERS_TRANSCRIPTIONS = ["transcriptions.json",
                           "transcriptions_second_rideau.json",
                           "transcriptions_temoins.json"]

VRAIS = {"collaboration remuneree"}
FAUX = {"hors sujet", "mention sans collaboration", "auto-promotion"}


def normaliser(texte):
    t = unicodedata.normalize("NFD", str(texte))
    t = "".join(c for c in t if unicodedata.category(c) not in ("Mn", "Cf"))
    return " ".join(t.lower().split())


def charger_transcriptions():
    transcriptions = {}
    for nom in FICHIERS_TRANSCRIPTIONS:
        chemin = DOSSIER_ACQUIS / nom
        if chemin.exists():
            with open(chemin, encoding="utf-8") as f:
                transcriptions.update(json.load(f))
    return transcriptions


def charger_verdicts():
    verdicts = {}
    for chemin in sorted(DOSSIER_RECHERCHE.glob("jugements_reference_*.csv")):
        with open(chemin, encoding="utf-8-sig") as f:
            for j in csv.DictReader(f):
                for e in j["entite"].split("|"):
                    verdicts[(j["video_id"], normaliser(e))] = \
                        normaliser(j["verdict"])
    recoltes = RACINE / "donnees" / "jugements_recoltes.csv"
    if recoltes.exists():
        with open(recoltes, encoding="utf-8-sig") as f:
            for j in csv.DictReader(f):
                verdicts[(j["video_id"], normaliser(j["entite"]))] = \
                    normaliser(j["verdict"])
    return verdicts


def principal():
    signaux, _ = charger_signaux()
    transcriptions = charger_transcriptions()
    verdicts = charger_verdicts()
    maintenant = dt.datetime.now().isoformat(timespec="seconds")

    base = sqlite3.connect(CHEMIN_BASE)
    colonnes = [c[1] for c in base.execute("PRAGMA table_info(detections)")]
    if "source" not in colonnes:
        base.execute("ALTER TABLE detections ADD COLUMN source TEXT "
                     "NOT NULL DEFAULT 'description'")

    detections_orales = []
    for video_id, texte in transcriptions.items():
        if not texte:
            continue
        for d in analyser(texte, signaux):
            d.pop("signaux_touches", None)
            detections_orales.append((video_id, d))

    # MESURE contre les verdicts, sur les videos transcrites et jugees.
    videos_transcrites = set(transcriptions)
    paires_jugees = {cle: v for cle, v in verdicts.items()
                     if cle[0] in videos_transcrites}
    retenues = {(vid, normaliser(d["entite"])) for vid, d in detections_orales
                if d["force"] == "fort" or d["indices_commerciaux"]}
    vp = fp = fn = vn = exclus = 0
    for cle, verdict in paires_jugees.items():
        if verdict in {normaliser(v) for v in VRAIS}:
            vrai = True
        elif verdict in {normaliser(v) for v in FAUX}:
            vrai = False
        else:
            exclus += 1
            continue
        r = cle in retenues
        vp += r and vrai
        fp += r and not vrai
        fn += (not r) and vrai
        vn += (not r) and not vrai

    # En base : rejouable, uniquement la source transcription.
    with base:
        base.execute("DELETE FROM detections WHERE source = 'transcription'")
        for video_id, d in detections_orales:
            existe_video = base.execute(
                "SELECT 1 FROM videos WHERE video_id = ?",
                (video_id,)).fetchone()
            if not existe_video:
                continue  # transcription d'une video hors base : ignoree ici
            base.execute(
                "INSERT OR IGNORE INTO detections (video_id, entite, "
                "signaux, types_signaux, force, indices_commerciaux, "
                "extrait, detectee_le, source) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'transcription')",
                (video_id, d["entite"], d["signaux"], d["types_signaux"],
                 d["force"], d["indices_commerciaux"],
                 "[ENTENDU DANS LA VIDEO] " + d["extrait"], maintenant))
        inserees = base.execute(
            "SELECT COUNT(*) FROM detections WHERE source = 'transcription'"
        ).fetchone()[0]
    base.close()

    def taux(n, d):
        return f"{100 * n / d:.0f} %" if d else "—"

    aujourd_hui = dt.date.today().isoformat()
    chemin_rapport = DOSSIER_RECHERCHE / f"second_rideau_{aujourd_hui}.md"
    with open(chemin_rapport, "w", encoding="utf-8") as f:
        f.write(f"# Second rideau : detection orale — {aujourd_hui}\n\n")
        f.write("Produit par `outils/second_rideau.py`, dictionnaire "
                f"actuel ({len(signaux)} signaux actifs).\n\n")
        f.write("| | |\n|---|---:|\n")
        f.write(f"| Transcriptions disponibles | {len(transcriptions)} |\n")
        f.write(f"| Detections orales (toutes) | {len(detections_orales)} |\n")
        f.write(f"| dont inserees en base (video connue) | {inserees} |\n\n")
        f.write("## MESURE du signal oral (regle R3 sur transcription) "
                "contre les verdicts humains\n\n")
        f.write(f"Paires jugees ET transcrites : {vp + fp + fn + vn} "
                f"(+{exclus} indecises exclues)\n\n")
        f.write("| | |\n|---|---:|\n")
        f.write(f"| VP | {vp} |\n| FP | {fp} |\n| FN | {fn} |\n| VN | {vn} |\n")
        f.write(f"| **Precision** | **{taux(vp, vp + fp)}** |\n")
        f.write(f"| **Rappel** | **{taux(vp, vp + fn)}** |\n\n")
        f.write("Lecture : le rappel oral seul est structurellement bas — "
                "le second rideau COMPLETE la description, il ne la "
                "remplace pas. Sa valeur est dans les cas que la "
                "description ne voit pas.\n")

    print(f"Transcriptions : {len(transcriptions)}  |  Detections orales : "
          f"{len(detections_orales)} (inserees : {inserees})")
    print(f"Mesure : precision {taux(vp, vp + fp)}, rappel {taux(vp, vp + fn)}")
    print(f"Ecrit : {chemin_rapport}")


if __name__ == "__main__":
    principal()
