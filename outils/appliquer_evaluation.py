# -*- coding: utf-8 -*-
"""Applique (ou simule) les decisions sur les signaux `propose` evalues.

Entree : le dernier `recherche/evaluation_signaux_proposes_<date>.csv`
(une ligne par signal propose, avec la recommandation de Claude :
« confirmer (fort) », « confirmer (faible) », « rejeter », ou « sans
occurrence »).

Deux modes :

  SIMULATION (par defaut, ne modifie RIEN) — pour que Vincent decide sur
  des nombres, pas sur une liste de noms : pour chaque option (« les 6 » =
  les forts seuls, « les 23 » = forts + faibles), on rejoue la detection
  sur toute la base avec le dictionnaire actuel PLUS les signaux de
  l'option, et on compte ce qui arriverait dans A_JUGER : les paires
  retenues par R3, nouvelles par rapport a aujourd'hui, jamais jugees.
  Les paires nouvelles deja jugees donnent une estimation de precision.
  Rapport : recherche/simulation_activation_<date>.md (+ CSV des paires).

  APPLICATION (`--appliquer 6` ou `--appliquer 23`, plus `--rejeter`) —
  a lancer UNIQUEMENT apres la decision de Vincent (critere 11) : passe
  les signaux choisis en `confirme` (force selon la recommandation), et
  avec --rejeter les 46 « rejeter » en `rejete`. La ligne du dictionnaire
  garde une trace (colonne commentaire). Puis relancer
  `outils/rescanner_base.py` et `outils/generer_a_juger.py`.

Usage :
  python outils/appliquer_evaluation.py                 # simulation
  python outils/appliquer_evaluation.py --appliquer 23 --rejeter
"""

import argparse
import csv
import datetime as dt
import sqlite3
import sys
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

import openpyxl

sys.path.insert(0, str(Path(__file__).resolve().parent))
from detecter import analyser, canaux_vitrines_depuis, charger_signaux, \
    compiler_signal, normaliser_positionnel  # noqa: E402

RACINE = Path(__file__).resolve().parent.parent
CHEMIN_DICO = RACINE / "DICTIONNAIRE.xlsx"
CHEMIN_BASE = RACINE / "donnees" / "veille.sqlite"
CHEMIN_RECOLTES = RACINE / "donnees" / "jugements_recoltes.csv"
DOSSIER_RECHERCHE = RACINE / "recherche"

OPTIONS = {
    "6": ("confirmer (fort)",),
    "23": ("confirmer (fort)", "confirmer (faible)"),
}
FORCE_PAR_RECOMMANDATION = {
    "confirmer (fort)": "fort",
    "confirmer (faible)": "faible",
}


def normaliser(texte):
    t = unicodedata.normalize("NFD", str(texte or ""))
    t = "".join(c for c in t if unicodedata.category(c) not in ("Mn", "Cf"))
    return " ".join(t.lower().split())


def derniere_evaluation():
    fichiers = sorted(DOSSIER_RECHERCHE.glob("evaluation_signaux_proposes_*.csv"))
    if not fichiers:
        sys.exit("aucune evaluation dans recherche/")
    return fichiers[-1]


def lire_evaluation(chemin):
    with open(chemin, encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def verdicts_humains():
    """(video_id, entite normalisee) -> verdict, toutes sources humaines."""
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


def videos_hors_vitrines(base, vitrines):
    """Toutes les videos de la base sauf celles publiees par une vitrine."""
    lignes = base.execute(
        "SELECT v.video_id, v.titre, v.description, c.nom, c.abonnes, "
        "v.url, v.publiee FROM videos v "
        "JOIN comptes c ON c.compte_id = v.compte_id").fetchall()
    return [l for l in lignes
            if normaliser_positionnel(l[3] or "").lstrip("@") not in vitrines]


def paires_r3(videos, signaux):
    """{(video_id, entite normalisee): detection} retenues par la regle R3."""
    paires = {}
    for video_id, titre, description, nom, abonnes, url, publiee in videos:
        texte = f"{titre or ''}\n{description or ''}"
        for d in analyser(texte, signaux):
            if d["force"] == "fort" or d["indices_commerciaux"]:
                d.update({"video_id": video_id, "chaine": nom or "",
                          "abonnes": abonnes or 0, "url": url,
                          "publiee": publiee, "titre": titre or ""})
                paires[(video_id, normaliser(d["entite"]))] = d
    return paires


def simuler(evaluation):
    signaux_actifs, _ = charger_signaux()
    vitrines = canaux_vitrines_depuis(signaux_actifs)
    base = sqlite3.connect(CHEMIN_BASE)
    videos = videos_hors_vitrines(base, vitrines)
    base.close()
    verdicts = verdicts_humains()

    reference = paires_r3(videos, signaux_actifs)
    aujourd_hui = dt.date.today().isoformat()
    resultats = {}
    lignes_csv = []
    for option, recommandations in OPTIONS.items():
        extra = [compiler_signal(e["signal"], "signal propose", e["entite"],
                                 FORCE_PAR_RECOMMANDATION[e["recommandation"]])
                 for e in evaluation if e["recommandation"] in recommandations]
        # On retire les doublons du dictionnaire (meme texte, meme entite).
        vus, extra_uniques = set(), []
        for s in extra:
            cle = (normaliser(s["texte"]), normaliser(s["entite"]))
            if cle not in vus:
                vus.add(cle)
                extra_uniques.append(s)
        toutes = paires_r3(videos, signaux_actifs + extra_uniques)
        nouvelles = {k: v for k, v in toutes.items() if k not in reference}
        jugees = {k: verdicts[k] for k in nouvelles if k in verdicts}
        a_juger = {k: v for k, v in nouvelles.items() if k not in verdicts}
        resultats[option] = {
            "signaux": extra_uniques,
            "nouvelles": nouvelles,
            "jugees": Counter(jugees.values()),
            "a_juger": a_juger,
            "par_entite": Counter(v["entite"] for v in a_juger.values()),
            "par_signal": Counter(s for v in a_juger.values()
                                  for s in v["signaux"].split(" | ")),
        }
        for (video_id, _), d in sorted(a_juger.items(),
                                       key=lambda kv: -int(kv[1]["abonnes"] or 0)):
            lignes_csv.append({
                "option": option, "video_id": video_id,
                "chaine": d["chaine"], "abonnes": d["abonnes"],
                "publiee": d["publiee"], "entite": d["entite"],
                "signaux": d["signaux"], "force": d["force"],
                "indices_commerciaux": d["indices_commerciaux"],
                "titre": d["titre"], "url": d["url"], "extrait": d["extrait"],
            })

    chemin_csv = DOSSIER_RECHERCHE / f"simulation_activation_{aujourd_hui}.csv"
    with open(chemin_csv, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=list(lignes_csv[0].keys()) if lignes_csv
                           else ["option"])
        w.writeheader()
        w.writerows(lignes_csv)

    chemin_md = DOSSIER_RECHERCHE / f"simulation_activation_{aujourd_hui}.md"
    with open(chemin_md, "w", encoding="utf-8") as f:
        f.write(f"# Simulation : que donnerait l'activation des signaux "
                f"evalues ? — {aujourd_hui}\n\n")
        f.write("Produit par `outils/appliquer_evaluation.py` (mode "
                "simulation : RIEN n'est modifie). Detection rejouee sur "
                f"les {len(videos)} videos de la base hors vitrines, avec le "
                f"dictionnaire actuel ({len(signaux_actifs)} signaux "
                "actifs) plus les signaux de chaque option. Regle R3 "
                "(signal fort, ou faible + indice commercial a moins de "
                "500 caracteres).\n\n")
        f.write(f"Paires R3 aujourd'hui (reference) : {len(reference)}.\n\n")
        f.write("| Option | Signaux actives | Paires R3 nouvelles | "
                "deja jugees | **a juger (arriveraient dans A_JUGER)** |\n")
        f.write("|---|---:|---:|---:|---:|\n")
        for option, r in resultats.items():
            f.write(f"| les {option} | {len(r['signaux'])} | "
                    f"{len(r['nouvelles'])} | {sum(r['jugees'].values())} | "
                    f"**{len(r['a_juger'])}** |\n")
        for option, r in resultats.items():
            f.write(f"\n## Option « les {option} »\n\n")
            f.write("Signaux : " + ", ".join(
                f"{s['texte']} ({s['entite']}, {s['force']})"
                for s in r["signaux"]) + "\n\n")
            if r["jugees"]:
                f.write("Paires nouvelles deja jugees par Vincent (estimation "
                        "de precision sur ces signaux) :\n\n")
                for verdict, n in r["jugees"].most_common():
                    f.write(f"- {verdict} : {n}\n")
                f.write("\n")
            f.write("A juger, par entite :\n\n")
            for entite, n in r["par_entite"].most_common():
                f.write(f"- {entite} : {n}\n")
            f.write("\nA juger, par signal declencheur :\n\n")
            for signal, n in r["par_signal"].most_common():
                f.write(f"- {signal} : {n}\n")
            f.write("\n| Chaine | Abonnes | Entite | Signaux | Indices | "
                    "Titre |\n|---|---:|---|---|---|---|\n")
            for d in sorted(r["a_juger"].values(),
                            key=lambda d: -int(d["abonnes"] or 0))[:60]:
                f.write(f"| {d['chaine']} | {d['abonnes']} | {d['entite']} | "
                        f"{d['signaux']} | {d['indices_commerciaux']} | "
                        f"{d['titre'][:60]} |\n")
            if len(r["a_juger"]) > 60:
                f.write(f"\n(… {len(r['a_juger']) - 60} autres lignes dans "
                        f"le CSV)\n")
        f.write(f"\nDetail ligne par ligne : `{chemin_csv.name}`.\n")

    for option, r in resultats.items():
        print(f"les {option} : {len(r['signaux'])} signaux -> "
              f"{len(r['nouvelles'])} paires R3 nouvelles, "
              f"{len(r['a_juger'])} a juger, jugees : {dict(r['jugees'])}")
    print(f"Ecrit : {chemin_md}")


def appliquer(evaluation, option, rejeter):
    recommandations = OPTIONS[option]
    decisions = {}
    for e in evaluation:
        cle = (normaliser(e["signal"]), normaliser(e["entite"]))
        if e["recommandation"] in recommandations:
            decisions[cle] = ("confirme",
                              FORCE_PAR_RECOMMANDATION[e["recommandation"]])
        elif rejeter and e["recommandation"] == "rejeter":
            decisions[cle] = ("rejete", None)

    wb = openpyxl.load_workbook(CHEMIN_DICO)
    ws = wb["Signaux"]
    entetes = [str(c.value or "").strip() for c in ws[1]]
    col = {nom: i + 1 for i, nom in enumerate(entetes)}
    aujourd_hui = dt.date.today().isoformat()
    mention = (f"decision de Vincent du {aujourd_hui} sur l'evaluation du "
               f"2026-09-06 (option « les {option} »)")
    changements = Counter()
    lignes_changees = []
    for rang in range(2, ws.max_row + 1):
        texte = ws.cell(rang, col["texte"]).value
        if not texte:
            continue
        if str(ws.cell(rang, col["statut"]).value or "").strip() != "propose":
            continue
        cle = (normaliser(texte), normaliser(ws.cell(rang, col["entite"]).value))
        if cle not in decisions:
            continue
        statut, force = decisions[cle]
        ws.cell(rang, col["statut"]).value = statut
        if force:
            ws.cell(rang, col["force"]).value = force
        ancien = str(ws.cell(rang, col["commentaire"]).value or "").strip()
        ws.cell(rang, col["commentaire"]).value = \
            (ancien + " ; " if ancien else "") + mention
        changements[statut] += 1
        lignes_changees.append((texte, ws.cell(rang, col["entite"]).value,
                                statut, force or ""))
    wb.save(CHEMIN_DICO)

    chemin_md = DOSSIER_RECHERCHE / f"activation_signaux_{aujourd_hui}.md"
    with open(chemin_md, "w", encoding="utf-8") as f:
        f.write(f"# Activation des signaux evalues — {aujourd_hui}\n\n")
        f.write(f"Produit par `outils/appliquer_evaluation.py --appliquer "
                f"{option}{' --rejeter' if rejeter else ''}`. {mention}.\n\n")
        f.write("| | |\n|---|---:|\n")
        f.write(f"| Signaux passes en `confirme` | {changements['confirme']} |\n")
        f.write(f"| Signaux passes en `rejete` | {changements['rejete']} |\n\n")
        f.write("| Signal | Entite | Statut | Force |\n|---|---|---|---|\n")
        for l in lignes_changees:
            f.write("| " + " | ".join(str(x) for x in l) + " |\n")
        f.write("\nA faire ensuite : `python outils/rescanner_base.py` puis "
                "`python outils/generer_a_juger.py`.\n")
    print(f"confirme : {changements['confirme']}, rejete : "
          f"{changements['rejete']}")
    print(f"Ecrit : {chemin_md}")
    print("Ensuite : python outils/rescanner_base.py && "
          "python outils/generer_a_juger.py")


def principal():
    parseur = argparse.ArgumentParser()
    parseur.add_argument("--appliquer", choices=list(OPTIONS),
                         help="applique l'option choisie par Vincent au "
                              "dictionnaire (sinon : simulation)")
    parseur.add_argument("--rejeter", action="store_true",
                         help="avec --appliquer : passe aussi les signaux "
                              "« rejeter » en rejete")
    args = parseur.parse_args()

    chemin = derniere_evaluation()
    evaluation = lire_evaluation(chemin)
    print(f"Evaluation lue : {chemin.name} ({len(evaluation)} signaux)")
    if args.appliquer:
        appliquer(evaluation, args.appliquer, args.rejeter)
    else:
        simuler(evaluation)


if __name__ == "__main__":
    principal()
