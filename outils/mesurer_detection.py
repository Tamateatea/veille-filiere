# -*- coding: utf-8 -*-
"""Mesure le detecteur contre les verdicts de Vincent (criteres 2, 3, 4).

Entrees :
  - recherche/jugements_reference_<date>.csv (le plus recent) — les verdicts ;
  - donnees/detections.csv — la sortie de `detecter.py`.

Trois regles mesurees :
  - R1 « signal seul »       : une paire (video, entite) est retenue des
    qu'un signal du dictionnaire est present ;
  - R2 « signal + indice »   : R1, plus au moins un indice commercial
    (merci a, partenariat, sponsorise, code promo…) ;
  - R3 « force du signal »   : un signal FORT suffit seul (un compte, un
    hashtag, un nom de campagne, d'operation ou de serie designent le
    commanditaire sans ambiguite) ; un signal FAIBLE (nom de marque, slogan,
    nom de chaine ecrit en texte libre) exige en plus un indice commercial.

Correspondance verdict -> etalon :
  - collaboration remuneree                    -> VRAI
  - hors sujet, mention sans collaboration     -> FAUX
  - je ne sais pas                             -> exclu de la mesure

Sorties : recherche/mesure_detection_<date>.md (les nombres) et
recherche/mesure_detection_<date>_desaccords.csv (chaque cas ou la regle
et Vincent divergent, pour inspection).
"""

import csv
import datetime as dt
import unicodedata
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
CHEMIN_DETECTIONS = RACINE / "donnees" / "detections.csv"
DOSSIER_RECHERCHE = RACINE / "recherche"

VRAIS = {"collaboration remuneree"}
FAUX = {"hors sujet", "mention sans collaboration"}
CHEMIN_VITRINES = RACINE / "donnees" / "contenus_vitrines.csv"


def normaliser(texte):
    t = unicodedata.normalize("NFD", str(texte))
    t = "".join(c for c in t if unicodedata.category(c) not in ("Mn", "Cf"))
    return " ".join(t.lower().split())


def charger_reference():
    candidats = sorted(DOSSIER_RECHERCHE.glob("jugements_reference_*.csv"))
    if not candidats:
        raise SystemExit("Aucun jugements_reference_*.csv : lancer "
                         "outils/jugements_reference.py d'abord.")
    chemin = candidats[-1]
    with open(chemin, encoding="utf-8-sig") as f:
        lignes = list(csv.DictReader(f))
    return chemin.name, lignes


def taux(numerateur, denominateur):
    if denominateur == 0:
        return "—"
    return f"{100 * numerateur / denominateur:.0f} %"


def principal():
    nom_reference, reference = charger_reference()

    with open(CHEMIN_DETECTIONS, encoding="utf-8-sig") as f:
        detections = {}
        for d in csv.DictReader(f):
            cle = (d["video_id"], normaliser(d["entite"]))
            detections[cle] = d

    videos_vitrines = set()
    if CHEMIN_VITRINES.exists():
        with open(CHEMIN_VITRINES, encoding="utf-8-sig") as f:
            videos_vitrines = {v["video_id"] for v in csv.DictReader(f)}

    resultats = []      # un dict par paire jugee et mesurable
    exclus = 0
    vitrines_jugees = {"vrai": 0, "faux": 0, "autre": 0}
    for j in reference:
        verdict = normaliser(j["verdict"])
        if j["video_id"] in videos_vitrines:
            if verdict in {normaliser(v) for v in VRAIS}:
                vitrines_jugees["vrai"] += 1
            elif verdict in {normaliser(v) for v in FAUX}:
                vitrines_jugees["faux"] += 1
            else:
                vitrines_jugees["autre"] += 1
            continue
        if verdict in {normaliser(v) for v in VRAIS}:
            vrai = True
        elif verdict in {normaliser(v) for v in FAUX}:
            vrai = False
        else:
            exclus += 1
            continue
        entites = [normaliser(e) for e in j["entite"].split("|")]
        trouvee = None
        for e in entites:
            trouvee = detections.get((j["video_id"], e))
            if trouvee:
                break
        signal_fort = trouvee is not None and trouvee["force"] == "fort"
        avec_indice = trouvee is not None and bool(trouvee["indices_commerciaux"])
        resultats.append({
            "jugement": j,
            "vrai": vrai,
            "r1": trouvee is not None,
            "r2": avec_indice,
            "r3": signal_fort or avec_indice,
            "detection": trouvee,
        })

    aujourd_hui = dt.date.today().isoformat()
    chemin_md = DOSSIER_RECHERCHE / f"mesure_detection_{aujourd_hui}.md"
    chemin_csv = DOSSIER_RECHERCHE / f"mesure_detection_{aujourd_hui}_desaccords.csv"

    lignes_md = []
    lignes_md.append(f"# Mesure du detecteur — {aujourd_hui}\n")
    lignes_md.append(f"Reference : `{nom_reference}` "
                     f"({len(resultats)} paires mesurables, "
                     f"{exclus} « je ne sais pas » exclues). "
                     "Detections : `donnees/detections.csv`.\n")
    total_vitrines = sum(vitrines_jugees.values())
    if total_vitrines:
        lignes_md.append(
            f"\n{total_vitrines} paires jugees portent sur des videos "
            "publiees par un canal vitrine : elles sont hors du flux "
            "createur (routees vers la decouverte) et donc hors mesure — "
            f"verdicts : {vitrines_jugees['vrai']} vraies, "
            f"{vitrines_jugees['faux']} fausses, "
            f"{vitrines_jugees['autre']} indecises. Les vraies restent des "
            "collaborations reelles : leur createur doit ressortir par le "
            "flux decouverte, pas par celui-ci.\n")

    desaccords = []
    for nom_regle in ("r1", "r2", "r3"):
        vp = sum(1 for r in resultats if r[nom_regle] and r["vrai"])
        fp = sum(1 for r in resultats if r[nom_regle] and not r["vrai"])
        fn = sum(1 for r in resultats if not r[nom_regle] and r["vrai"])
        vn = sum(1 for r in resultats if not r[nom_regle] and not r["vrai"])
        positifs = vp + fn
        libelle = {"r1": "R1 signal seul",
                   "r2": "R2 signal + indice commercial",
                   "r3": "R3 signal fort, ou faible + indice"}[nom_regle]
        lignes_md.append(f"\n## {libelle}\n")
        lignes_md.append("| | |\n|---|---:|")
        lignes_md.append(f"| Retenues par la regle | {vp + fp} |")
        lignes_md.append(f"| dont vraies (VP) | {vp} |")
        lignes_md.append(f"| dont fausses (FP) | {fp} |")
        lignes_md.append(f"| Vraies manquees (FN) | {fn} |")
        lignes_md.append(f"| Fausses ecartees (VN) | {vn} |")
        lignes_md.append(f"| **Precision** | **{taux(vp, vp + fp)}** |")
        lignes_md.append(f"| **Rappel** | **{taux(vp, positifs)}** |")

        for r in resultats:
            if r[nom_regle] != r["vrai"]:
                j = r["jugement"]
                desaccords.append({
                    "regle": libelle,
                    "type": "faux positif" if r[nom_regle] else "faux negatif",
                    "video_id": j["video_id"],
                    "chaine": j["chaine"],
                    "entite": j["entite"],
                    "titre": j["titre"],
                    "verdict_vincent": j["verdict"],
                    "commentaire_vincent": j["commentaire"],
                    "signaux": (r["detection"] or {}).get("signaux", ""),
                    "url": j["url"],
                })

    # Rappel par entite, regle R1 — pour voir ou le dictionnaire est aveugle.
    lignes_md.append("\n## Rappel par entite (R1)\n")
    lignes_md.append("| Entite | Vraies jugees | Retrouvees |\n|---|---:|---:|")
    par_entite = {}
    for r in resultats:
        if not r["vrai"]:
            continue
        for e in r["jugement"]["entite"].split("|"):
            e = e.strip()
            d = par_entite.setdefault(e, [0, 0])
            d[0] += 1
            if r["r1"]:
                d[1] += 1
    for e, (total, retrouvees) in sorted(par_entite.items(),
                                         key=lambda x: -x[1][0]):
        lignes_md.append(f"| {e} | {total} | {retrouvees} |")

    lignes_md.append("""
## Limites de cette mesure — a lire avant de citer les chiffres

1. **Le rappel est relatif aux candidats juges**, pas a YouTube entier : le
   jeu de reference a ete constitue a partir des detections des anciennes
   regles. Une collaboration qu'aucune regle n'a jamais vue n'y figure pas.
2. **La mesure ne couvre que le canal interprofession** (CNIEL, CIFOG,
   INTERBEV, CLIPP, INAPORC, ANVOL). Les detections de marques (« Societe »,
   « Marie », « President »…) ne sont PAS mesurees ici : aucun verdict
   n'existe encore sur ce canal. Ne rien conclure sur elles.
3. **R3 est calibree sur ce meme jeu** : le declassement des quatre signaux
   pollueurs et le routage des canaux vitrines ont ete decides en regardant
   les erreurs de ce corpus. Ses chiffres sont donc optimistes. Ils ne
   seront etablis qu'apres verification sur un lot NEUF de jugements —
   c'est le prochain lot de ~50 cas prevu par le critere 6 du contrat.
""")

    with open(chemin_md, "w", encoding="utf-8") as f:
        f.write("\n".join(lignes_md) + "\n")
    with open(chemin_csv, "w", newline="", encoding="utf-8-sig") as f:
        champs = ["regle", "type", "video_id", "chaine", "entite", "titre",
                  "verdict_vincent", "commentaire_vincent", "signaux", "url"]
        w = csv.DictWriter(f, fieldnames=champs)
        w.writeheader()
        w.writerows(desaccords)

    print(f"Paires mesurables : {len(resultats)} (+{exclus} exclues)")
    print(f"Ecrit : {chemin_md}")
    print(f"Ecrit : {chemin_csv}")


if __name__ == "__main__":
    principal()
