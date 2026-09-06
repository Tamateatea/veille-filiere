# -*- coding: utf-8 -*-
"""Mesure la regle R3 ACTUELLE sur le lot de validation (jugements recoltes).

Difference avec `mesurer_detection.py` : ici l'etalon est le lot NEUF de
`donnees/jugements_recoltes.csv` (le classeur A_JUGER), pas les 391 verdicts
historiques. C'est la mesure exigee par la limite n°3 du rapport de mesure :
R3 avait ete calibree sur l'ancien jeu, ses chiffres devaient etre confirmes
sur du neuf.

Le lot avait ete tire sur les detections d'AVANT les corrections du jour
(proximite des indices, declassement de CHAUD !). La mesure dit donc aussi
combien de paires du lot la regle actuelle ne retient plus — l'effet reel
des corrections.

Provenance des verdicts, a garder en tete en lisant les chiffres :
5 rendus directement par Vincent, 43 pre-tries par Claude puis valides en
bloc par Vincent. Et deux cas du lot (SQUEEZIE/Marie, Greg Guillotin/CNIEL)
ont inspire les corrections mesurees ici : petite fuite, chiffres a lire
comme indicatifs a +/- quelques points.
"""

import csv
import datetime as dt
import unicodedata
from pathlib import Path

import openpyxl

RACINE = Path(__file__).resolve().parent.parent
CHEMIN_RECOLTE = RACINE / "donnees" / "jugements_recoltes.csv"
CHEMIN_DETECTIONS = RACINE / "donnees" / "detections.csv"
CHEMIN_DICO = RACINE / "DICTIONNAIRE.xlsx"
DOSSIER_RECHERCHE = RACINE / "recherche"

VRAIS = {"collaboration remuneree"}
FAUX = {"hors sujet", "mention sans collaboration", "auto-promotion"}


def normaliser(texte):
    t = unicodedata.normalize("NFD", str(texte))
    t = "".join(c for c in t if unicodedata.category(c) not in ("Mn", "Cf"))
    return " ".join(t.lower().split())


def interprofessions():
    wb = openpyxl.load_workbook(CHEMIN_DICO, read_only=True, data_only=True)
    lignes = list(wb["Entites"].iter_rows(values_only=True))
    wb.close()
    entetes = [str(c or "").strip() for c in lignes[0]]
    i_nom, i_type = entetes.index("entite"), entetes.index("type_entite")
    return {normaliser(l[i_nom]) for l in lignes[1:]
            if l[i_nom] and "interprofession" in normaliser(l[i_type] or "")}


def principal():
    with open(CHEMIN_RECOLTE, encoding="utf-8-sig") as f:
        lot = list(csv.DictReader(f))
    with open(CHEMIN_DETECTIONS, encoding="utf-8-sig") as f:
        detections = {(d["video_id"], normaliser(d["entite"])): d
                      for d in csv.DictReader(f)}
    interpros = interprofessions()

    stats = {"interprofession": {"vp": 0, "fp": 0, "fn": 0, "vn": 0},
             "marque": {"vp": 0, "fp": 0, "fn": 0, "vn": 0}}
    exclus = 0
    for j in lot:
        verdict = normaliser(j["verdict"])
        if verdict in {normaliser(v) for v in VRAIS}:
            vrai = True
        elif verdict in {normaliser(v) for v in FAUX}:
            vrai = False
        else:
            exclus += 1
            continue
        canal = ("interprofession" if normaliser(j["entite"]) in interpros
                 else "marque")
        d = detections.get((j["video_id"], normaliser(j["entite"])))
        retenue = d is not None and (d["force"] == "fort"
                                     or bool(d["indices_commerciaux"]))
        s = stats[canal]
        if retenue and vrai:
            s["vp"] += 1
        elif retenue and not vrai:
            s["fp"] += 1
        elif not retenue and vrai:
            s["fn"] += 1
        else:
            s["vn"] += 1

    aujourd_hui = dt.date.today().isoformat()
    chemin = DOSSIER_RECHERCHE / f"validation_lot1_{aujourd_hui}.md"

    def taux(n, d):
        return f"{100 * n / d:.0f} %" if d else "—"

    with open(chemin, "w", encoding="utf-8") as f:
        f.write(f"# Validation de R3 sur le lot neuf — {aujourd_hui}\n\n")
        f.write(f"Etalon : `jugements_recoltes.csv`, {len(lot)} verdicts "
                f"({exclus} « je ne sais pas » exclus). Regle : R3 ACTUELLE "
                "(apres proximite des indices et declassement de CHAUD !).\n\n")
        f.write("Provenance : 5 verdicts directs de Vincent, 43 pre-tries "
                "par Claude et valides en bloc par lui. Deux cas du lot ont "
                "inspire les corrections mesurees ici (fuite legere).\n\n")
        f.write("| Canal | Retenues | VP | FP | FN | VN | Precision | Rappel |\n")
        f.write("|---|---:|---:|---:|---:|---:|---:|---:|\n")
        for canal, s in stats.items():
            ret = s["vp"] + s["fp"]
            f.write(f"| {canal} | {ret} | {s['vp']} | {s['fp']} | {s['fn']} "
                    f"| {s['vn']} | {taux(s['vp'], ret)} "
                    f"| {taux(s['vp'], s['vp'] + s['fn'])} |\n")
        total_retire = sum(s["vn"] for s in stats.values())
        f.write(f"\nPaires du lot que la regle actuelle ne retient plus "
                f"(effet des corrections du jour + cas sans indice proche) : "
                f"{total_retire} ecartees a raison ou a tort — voir FN.\n")

    print(f"Ecrit : {chemin}")
    for canal, s in stats.items():
        ret = s["vp"] + s["fp"]
        print(f"{canal} : precision {taux(s['vp'], ret)} "
              f"({s['vp']}/{ret}), rappel {taux(s['vp'], s['vp'] + s['fn'])}")


if __name__ == "__main__":
    principal()
