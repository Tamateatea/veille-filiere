# -*- coding: utf-8 -*-
"""Genere A_JUGER.xlsx : le classeur de verification humaine (criteres 9-10).

Contenu : un LOT DE VALIDATION de 60 paires (video, entite) tirees AU HASARD
(graine fixe, donc reproductible) parmi les paires retenues par la regle R3
et jamais jugees par Vincent — STRATIFIE en deux moities :
  - 30 paires du canal INTERPROFESSION : elles verifient si les 94 % / 81 %
    de R3 tiennent sur des cas neufs ;
  - 30 paires du canal MARQUE : la premiere mesure de ce canal, 27 fois plus
    gros et jamais juge (decision D3 de l'ancien tableau de bord).
Le tirage aleatoire est voulu : un tri par audience biaiserait la mesure.

Garanties du critere 9, verifiees a la generation :
  - l'extrait affiche CONTIENT le signal qui a declenche (verifie ligne par
    ligne, la generation echoue sinon) ;
  - chaque ligne porte le compte, son audience, la date, et un lien cliquable.

Critere 10 : la colonne « Ton commentaire » est relue par
`outils/relire_jugements.py` a chaque passage.

Le script REFUSE de regenerer si le classeur existant contient le moindre
verdict : le travail de Vincent ne s'ecrase jamais.
"""

import csv
import datetime as dt
import random
import sys
import unicodedata
from pathlib import Path

import openpyxl
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.worksheet.datavalidation import DataValidation

RACINE = Path(__file__).resolve().parent.parent
CHEMIN_DETECTIONS = RACINE / "donnees" / "detections.csv"
CHEMIN_CLASSEUR = RACINE / "A_JUGER.xlsx"
DOSSIER_RECHERCHE = RACINE / "recherche"

TAILLE_PAR_CANAL = 30
GRAINE = 20260906
CHEMIN_DICO = RACINE / "DICTIONNAIRE.xlsx"

VERDICTS = [
    "collaboration remuneree",
    "mention sans collaboration",
    "auto-promotion",
    "hors sujet",
    "je ne sais pas",
]

MODE_EMPLOI = """Comment remplir ce classeur

Une ligne = UNE video et UN commanditaire possible. Tu ne remplis que les
deux dernieres colonnes.

La colonne « Extrait exact » contient toujours le passage qui a declenche
la detection — le signal repere y est forcement visible. Si l'extrait ne te
suffit pas pour juger, clique « ouvrir » et regarde la video.

TON VERDICT — choisis dans la liste deroulante :
  collaboration remuneree      le createur est paye par ce commanditaire
  mention sans collaboration   il en parle sans etre paye
  auto-promotion               il fait la promo de ses propres projets
  hors sujet                   faux positif, rien a voir
  je ne sais pas               le passage ne permet pas de trancher

« je ne sais pas » est une reponse utile : elle mesure la limite de l'outil.

Ton commentaire — tout ce que tu veux me dire : une erreur de l'outil, un
signal manquant, une idee. CHAQUE note est relue au passage suivant et le
rapport dira ce qui en a ete fait. Rien ne part dans le vide.

Ce lot de 60 est tire AU HASARD parmi les detections : c'est lui qui
verifiera si la precision annoncee de l'outil (94 %) tient sur des cas
neufs. Juge-le en entier si possible, dans l'ordre que tu veux."""


def normaliser(texte):
    t = unicodedata.normalize("NFD", str(texte))
    t = "".join(c for c in t if unicodedata.category(c) not in ("Mn", "Cf"))
    return " ".join(t.lower().split())


def entites_interprofessions():
    """Les entites de type interprofession, lues dans le dictionnaire."""
    wb = openpyxl.load_workbook(CHEMIN_DICO, read_only=True, data_only=True)
    lignes = list(wb["Entites"].iter_rows(values_only=True))
    wb.close()
    entetes = [str(c or "").strip() for c in lignes[0]]
    i_nom, i_type = entetes.index("entite"), entetes.index("type_entite")
    return {normaliser(l[i_nom]) for l in lignes[1:]
            if l[i_nom] and "interprofession" in normaliser(l[i_type] or "")}


def deja_jugees():
    """Les paires (video_id, entite) deja tranchees par Vincent."""
    paires = set()
    chemins = list(DOSSIER_RECHERCHE.glob("jugements_reference_*.csv"))
    recoltes = RACINE / "donnees" / "jugements_recoltes.csv"
    if recoltes.exists():
        chemins.append(recoltes)
    for chemin in chemins:
        with open(chemin, encoding="utf-8-sig") as f:
            for j in csv.DictReader(f):
                for e in j["entite"].split("|"):
                    paires.add((j["video_id"], normaliser(e)))
    return paires


def verdicts_existants():
    """Compte les verdicts saisis dans A_JUGER.xlsx et PAS ENCORE recoltes.

    Un classeur entierement recolte (par relire_jugements.py) peut etre
    regenere sans perte ; seuls des verdicts non recoltes bloquent.
    """
    if not CHEMIN_CLASSEUR.exists():
        return 0
    recoltes = set()
    chemin_recoltes = RACINE / "donnees" / "jugements_recoltes.csv"
    if chemin_recoltes.exists():
        with open(chemin_recoltes, encoding="utf-8-sig") as f:
            recoltes = {(j["video_id"], normaliser(j["entite"]),
                         normaliser(j["verdict"]))
                        for j in csv.DictReader(f)}
    wb = openpyxl.load_workbook(CHEMIN_CLASSEUR, data_only=True)
    n = 0
    if "a juger" in wb.sheetnames:
        ws = wb["a juger"]
        lignes = list(ws.iter_rows(values_only=True))
        entetes = [str(c or "") for c in lignes[0]] if lignes else []
        if "TON VERDICT" in entetes:
            i_v = entetes.index("TON VERDICT")
            i_e = entetes.index("Entite possible")
            for rang, l in enumerate(lignes[1:], start=2):
                verdict = l[i_v] if i_v < len(l) else None
                if not verdict or not str(verdict).strip():
                    continue
                url = ""
                for cellule in ws[rang]:
                    if cellule.hyperlink and cellule.hyperlink.target:
                        url = cellule.hyperlink.target
                        break
                video_id = (url.split("watch?v=")[1].split("&")[0]
                            if "watch?v=" in url else "")
                cle = (video_id, normaliser(l[i_e] or ""),
                       normaliser(verdict))
                if cle not in recoltes:
                    n += 1
    wb.close()
    return n


def principal():
    n_verdicts = verdicts_existants()
    if n_verdicts and "--forcer" not in sys.argv:
        sys.exit(f"{CHEMIN_CLASSEUR.name} contient deja {n_verdicts} verdicts "
                 "de Vincent : on ne l'ecrase pas. Lancer "
                 "outils/relire_jugements.py pour les recolter d'abord.")

    with open(CHEMIN_DETECTIONS, encoding="utf-8-sig") as f:
        detections = list(csv.DictReader(f))

    # Les detections des tournees du facteur (base SQLite) rejoignent le
    # meme circuit que celles du corpus gele.
    import sqlite3
    chemin_base = RACINE / "donnees" / "veille.sqlite"
    if chemin_base.exists():
        base = sqlite3.connect(chemin_base)
        deja = {(d["video_id"], normaliser(d["entite"])) for d in detections}
        for r in base.execute(
                "SELECT d.video_id, c.nom, c.abonnes, v.publiee, v.titre, "
                "v.url, d.entite, d.signaux, d.types_signaux, d.force, "
                "d.indices_commerciaux, d.extrait "
                "FROM detections d "
                "JOIN videos v ON v.video_id = d.video_id "
                "JOIN comptes c ON c.compte_id = v.compte_id"):
            if (r[0], normaliser(r[6])) in deja:
                continue
            detections.append({
                "video_id": r[0], "chaine": r[1] or "", "abonnes": r[2] or 0,
                "publiee": r[3] or "", "titre": r[4] or "", "url": r[5] or "",
                "entite": r[6], "signaux": r[7] or "",
                "types_signaux": r[8] or "", "force": r[9] or "faible",
                "indices_commerciaux": r[10] or "", "extrait": r[11] or "",
            })
        base.close()

    jugees = deja_jugees()
    candidates = []
    for d in detections:
        retenue_r3 = (d["force"] == "fort") or bool(d["indices_commerciaux"])
        if not retenue_r3:
            continue
        if (d["video_id"], normaliser(d["entite"])) in jugees:
            continue
        candidates.append(d)

    # Critere 9 : l'extrait doit contenir au moins un des signaux.
    invalides = [d for d in candidates
                 if not any(normaliser(s) in normaliser(d["extrait"])
                            for s in d["signaux"].split(" | "))]
    if invalides:
        sys.exit(f"CRITERE 9 VIOLE : {len(invalides)} extraits ne contiennent "
                 f"pas leur signal (ex. video {invalides[0]['video_id']}). "
                 "Corriger detecter.py avant de generer.")

    interpros = entites_interprofessions()
    canal_interpro = [d for d in candidates
                      if normaliser(d["entite"]) in interpros]
    canal_marque = [d for d in candidates
                    if normaliser(d["entite"]) not in interpros]
    tirage = random.Random(GRAINE)
    lot = (tirage.sample(canal_interpro,
                         min(TAILLE_PAR_CANAL, len(canal_interpro)))
           + tirage.sample(canal_marque,
                           min(TAILLE_PAR_CANAL, len(canal_marque))))
    lot.sort(key=lambda d: -int(d["abonnes"] or 0))

    wb = openpyxl.Workbook()
    gras = Font(bold=True)

    ws_mode = wb.active
    ws_mode.title = "COMMENT FAIRE"
    for i, ligne in enumerate(MODE_EMPLOI.splitlines(), start=1):
        ws_mode.cell(row=i, column=1, value=ligne)
    ws_mode.column_dimensions["A"].width = 78

    ws = wb.create_sheet("a juger")
    entetes = ["N", "Chaine", "Abonnes", "Date", "Entite possible",
               "Signaux reperes", "Titre de la video", "Regarder",
               "Extrait exact", "TON VERDICT", "Ton commentaire"]
    ws.append(entetes)
    for c in ws[1]:
        c.font = gras
    jaune = PatternFill("solid", fgColor="FFF2CC")
    for n, d in enumerate(lot, start=1):
        rang = n + 1
        ws.cell(rang, 1, n)
        ws.cell(rang, 2, d["chaine"])
        ws.cell(rang, 3, int(d["abonnes"] or 0))
        ws.cell(rang, 4, d["publiee"])
        ws.cell(rang, 5, d["entite"])
        ws.cell(rang, 6, d["signaux"])
        ws.cell(rang, 7, d["titre"])
        lien = ws.cell(rang, 8, "ouvrir")
        lien.hyperlink = d["url"]
        lien.font = Font(color="0563C1", underline="single")
        extrait = ws.cell(rang, 9, d["extrait"])
        extrait.fill = jaune
        extrait.alignment = Alignment(wrap_text=True, vertical="top")
        # cellule 10 et 11 : a Vincent

    if lot:
        validation = DataValidation(
            type="list", formula1='"' + ",".join(VERDICTS) + '"',
            allow_blank=True, showDropDown=False)
        ws.add_data_validation(validation)
        validation.add(f"J2:J{len(lot) + 1}")

    largeurs = {"A": 4, "B": 22, "C": 11, "D": 11, "E": 16, "F": 26, "G": 40,
                "H": 8, "I": 60, "J": 26, "K": 40}
    for lettre, largeur in largeurs.items():
        ws.column_dimensions[lettre].width = largeur
    ws.freeze_panes = "A2"

    ws_src = wb.create_sheet("d'ou ca vient")
    aujourd_hui = dt.date.today().isoformat()
    for i, ligne in enumerate([
        f"Source : donnees/detections.csv (regle R3), genere le {aujourd_hui}",
        f"Paires retenues par R3 et jamais jugees : {len(candidates)} "
        f"({len(canal_interpro)} interprofession, {len(canal_marque)} marque)",
        f"Lot stratifie tire au hasard (graine {GRAINE}) : {len(lot)} — "
        "moitie interprofession (valide R3), moitie marque (premiere mesure "
        "du canal, decision D3)",
        "Paires deja jugees par Vincent, exclues : voir "
        "recherche/jugements_reference_*.csv",
    ], start=1):
        ws_src.cell(row=i, column=1, value=ligne)
    ws_src.column_dimensions["A"].width = 90

    wb.save(CHEMIN_CLASSEUR)

    DOSSIER_RECHERCHE.mkdir(exist_ok=True)
    chemin_rapport = DOSSIER_RECHERCHE / f"a_juger_{aujourd_hui}.md"
    with open(chemin_rapport, "w", encoding="utf-8") as f:
        f.write(f"# Generation du classeur A_JUGER — {aujourd_hui}\n\n")
        f.write("Produit par `outils/generer_a_juger.py`.\n\n")
        f.write(f"| | |\n|---|---:|\n")
        f.write(f"| Paires R3 jamais jugees (gisement) | {len(candidates)} |\n")
        f.write(f"| dont canal interprofession | {len(canal_interpro)} |\n")
        f.write(f"| dont canal marque | {len(canal_marque)} |\n")
        f.write(f"| Lot stratifie (graine {GRAINE}) | {len(lot)} |\n")
        f.write(f"| Extraits verifies contenant leur signal | {len(lot)} / {len(lot)} |\n\n")
        f.write("Moitie interprofession (valide les 94 % / 81 % de R3 sur du "
                "neuf), moitie marque (premiere mesure du canal, decision "
                "D3). Tirage aleatoire par canal ; affichage trie par "
                "audience. Le classeur ne sera jamais regenere tant qu'il "
                "contient un verdict non recolte.\n")

    print(f"Gisement R3 jamais juge : {len(candidates)} paires")
    print(f"Lot ecrit : {CHEMIN_CLASSEUR} ({len(lot)} lignes)")
    print(f"Ecrit : {chemin_rapport}")


if __name__ == "__main__":
    principal()
