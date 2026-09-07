# -*- coding: utf-8 -*-
"""Mesure la case YouTube « Inclut une communication commerciale » comme
indice de collaboration, contre les verdicts humains (regle des trois
nombres : precision, rappel, fichier).

Question posee le 07/09/2026 : faut-il que la case cochee compte comme un
indice commercial dans la regle R3 (signal faible + indice -> retenu) ?
Avant de changer la regle, on mesure sur les paires jugees dont la video a
ete completee par `completer_videos.py` (la case n'est connue que pour
elles).

Trois regles comparees, sur les memes paires :
  R3          signal fort, ou faible + indice textuel (la regle actuelle)
  R3 + case   R3, ou faible + case cochee
  case seule  la case cochee, quel que soit le signal

Rapport horodate dans recherche/.
"""

import csv
import datetime as dt
import sqlite3
import sys
import unicodedata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from detecter import analyser, canaux_vitrines_depuis, charger_signaux, \
    normaliser_positionnel  # noqa: E402

RACINE = Path(__file__).resolve().parent.parent
CHEMIN_BASE = RACINE / "donnees" / "veille.sqlite"
CHEMIN_RECOLTES = RACINE / "donnees" / "jugements_recoltes.csv"
DOSSIER_RECHERCHE = RACINE / "recherche"

POSITIFS = {"collaboration remuneree"}
INDECIS = {"je ne sais pas"}


def normaliser(texte):
    t = unicodedata.normalize("NFD", str(texte or ""))
    t = "".join(c for c in t if unicodedata.category(c) not in ("Mn", "Cf"))
    return " ".join(t.lower().split())


def verdicts_humains():
    verdicts = {}
    chemins = sorted(DOSSIER_RECHERCHE.glob("jugements_reference_*.csv"))
    if CHEMIN_RECOLTES.exists():
        chemins.append(CHEMIN_RECOLTES)
    for chemin in chemins:
        with open(chemin, encoding="utf-8-sig") as f:
            for j in csv.DictReader(f):
                for e in (j.get("entite") or "").split("|"):
                    if e.strip():
                        verdicts[(j["video_id"], normaliser(e))] = \
                            normaliser(j.get("verdict"))
    return verdicts


def mesure(retenues, verites):
    vp = sum(1 for k in verites if verites[k] and k in retenues)
    fp = sum(1 for k in verites if not verites[k] and k in retenues)
    fn = sum(1 for k in verites if verites[k] and k not in retenues)
    precision = vp / (vp + fp) if vp + fp else 0
    rappel = vp / (vp + fn) if vp + fn else 0
    return vp, fp, fn, precision, rappel


def principal():
    signaux, _ = charger_signaux()
    vitrines = canaux_vitrines_depuis(signaux)
    verdicts = verdicts_humains()
    base = sqlite3.connect(CHEMIN_BASE)
    colonnes = [c[1] for c in base.execute("PRAGMA table_info(comptes)")]
    col_vitrine = ("c.entite_vitrine" if "entite_vitrine" in colonnes
                   else "NULL")
    # Les videos publiees par une vitrine (la chaine du lobby lui-meme) ne
    # sont jamais soumises a l'humain : on les ecarte de la mesure comme le
    # rescanner les ecarte de la detection. Sans ca, les 41 videos de la
    # chaine « Produits Laitiers » jugees hors sujet comptaient en faux.
    videos = {}
    n_vitrines = 0
    for r in base.execute(
            "SELECT v.video_id, v.titre, v.description, "
            f"v.declaration_commerciale, c.nom, {col_vitrine} "
            "FROM videos v JOIN comptes c ON c.compte_id = v.compte_id "
            "WHERE v.description_complete_le IS NOT NULL"):
        if r[5] or normaliser_positionnel(r[4] or "").lstrip("@") in vitrines:
            n_vitrines += 1
            continue
        videos[r[0]] = r[:4]
    base.close()

    # Les paires jugees dont la video est completee et le verdict tranche.
    verites = {}
    for (vid, entite), verdict in verdicts.items():
        if vid in videos and verdict not in INDECIS:
            verites[(vid, entite)] = verdict in POSITIFS
    exclues = sum(1 for (vid, _), v in verdicts.items()
                  if vid in videos and v in INDECIS)

    r3, r3_case, case_seule = set(), set(), set()
    for (vid, entite) in verites:
        _, titre, description, declaration = videos[vid]
        texte = f"{titre or ''}\n{description or ''}"
        for d in analyser(texte, signaux):
            if normaliser(d["entite"]) != entite:
                continue
            cle = (vid, entite)
            fort = d["force"] == "fort"
            indice = bool(d["indices_commerciaux"])
            if fort or indice:
                r3.add(cle)
            if fort or indice or declaration == 1:
                r3_case.add(cle)
            if declaration == 1:
                case_seule.add(cle)

    resultats = {"R3 (actuelle)": mesure(r3, verites),
                 "R3 + case cochee": mesure(r3_case, verites),
                 "case cochee seule": mesure(case_seule, verites)}
    n_cochees = sum(1 for vid in {k[0] for k in verites}
                    if videos[vid][3] == 1)

    aujourd_hui = dt.date.today().isoformat()
    chemin = DOSSIER_RECHERCHE / f"mesure_declaration_{aujourd_hui}.md"
    with open(chemin, "w", encoding="utf-8") as f:
        f.write(f"# La case « communication commerciale » comme indice — "
                f"{aujourd_hui}\n\n")
        f.write("Produit par `outils/mesurer_declaration.py`. Paires jugees "
                "par Vincent dont la video a ete completee depuis sa page "
                f"publique : **{len(verites)}** (+{exclues} « je ne sais "
                f"pas » exclues, {n_vitrines} videos de vitrines ecartees "
                "comme dans la detection) ; videos avec la case cochee "
                f"parmi elles : {n_cochees}.\n\n")
        f.write("| Regle | VP | FP | FN | Precision | Rappel |\n")
        f.write("|---|---:|---:|---:|---:|---:|\n")
        for nom, (vp, fp, fn, p, r) in resultats.items():
            f.write(f"| {nom} | {vp} | {fp} | {fn} | {p:.0%} | {r:.0%} |\n")
        f.write("\nLecture : la case ne dit pas POUR QUI le contenu est "
                "commercial. Elle ne vaut comme indice que combinee a un "
                "signal (une entite nommee).\n")
    for nom, (vp, fp, fn, p, r) in resultats.items():
        print(f"{nom:20s} VP {vp:3d} FP {fp:3d} FN {fn:3d}  "
              f"precision {p:.0%}  rappel {r:.0%}")
    print(f"Ecrit : {chemin}")


if __name__ == "__main__":
    principal()
