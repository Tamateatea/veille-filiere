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
import re
import sys
import unicodedata
from pathlib import Path

import openpyxl
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.worksheet.datavalidation import DataValidation

sys.path.insert(0, str(Path(__file__).resolve().parent))
from detecter import INDICATEURS, PORTEE_INDICE, charger_signaux, \
    normaliser_positionnel  # noqa: E402

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

Deux colonnes t'aident a trancher sans ouvrir la video :
  « Case communication commerciale »  OUI = le createur a lui-meme coche
      la case YouTube « Inclut une communication commerciale » (elle ne
      dit pas pour quelle marque : Doigby l'avait cochee pour Babybel,
      Mllex Chloe pour un code Uber).
  « Mention commerciale (passage) »   le bout de description qui porte
      un mot comme « partenariat », « sponsorise », « collaboration
      commerciale », quand il est loin du signal (souvent tout en bas).
  « Dit dans la video (passage) »     ce que le createur DIT, d'apres les
      sous-titres automatiques, autour du nom du commanditaire ou d'un
      mot commercial, avec le minutage. Utile quand la description est
      vide ou douteuse. Les sous-titres automatiques font des fautes.

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


def passage_commercial(description, signaux, extrait):
    """Le passage de la description qui porte la mention commerciale.

    Demande de Vincent (07/09) : la mention « collaboration commerciale »
    d'Encuisineaugustine etait a 800 caracteres du signal, hors extrait —
    l'humain qui juge doit la voir sans ouvrir la video. On cherche
    l'indice commercial le plus proche du signal ; s'il est deja dans
    l'extrait, on ne repete rien.
    """
    if not description:
        return ""
    norme = normaliser_positionnel(description)
    positions_signal = [norme.find(normaliser_positionnel(s))
                        for s in signaux.split(" | ") if s]
    positions_signal = [p for p in positions_signal if p >= 0]
    candidats = []
    for nom, motif in INDICATEURS.items():
        for m in re.finditer(motif, norme):
            distance = (min(abs(m.start() - p) for p in positions_signal)
                        if positions_signal else PORTEE_INDICE)
            candidats.append((distance, m.start(), m.end()))
    if not candidats:
        return ""
    _, debut, fin = min(candidats)
    morceau = description[max(0, debut - 100):fin + 100].strip()
    if normaliser(morceau[:60]) and normaliser(morceau[:60]) in normaliser(extrait):
        return ""  # deja visible dans l'extrait
    prefixe = "…" if debut > 100 else ""
    suffixe = "…" if fin + 100 < len(description) else ""
    return prefixe + morceau.replace("\n", " ⏎ ") + suffixe


def passage_oral(base, video_id, entite_signaux, signaux):
    """Ce qui est DIT dans la video autour du signal ou d'un mot commercial.

    Decision de Vincent (07/09) : la transcription renforce la certitude
    quand la description est vide ou douteuse. On cherche d'abord un signal
    de l'entite dans la transcription, sinon un mot commercial ; on affiche
    le passage avec son minutage. Rend "" si pas de transcription.
    """
    tables = {r[0] for r in base.execute(
        "SELECT name FROM sqlite_master WHERE type = 'table'")}
    if "transcriptions" not in tables:
        return ""
    r = base.execute("SELECT statut, texte, segments FROM transcriptions "
                     "WHERE video_id = ?", (video_id,)).fetchone()
    if not r:
        return "(pas encore transcrite)"
    statut, texte, segments = r
    if statut != "ok" or not texte:
        return "(pas de sous-titres disponibles)"
    norme = normaliser_positionnel(texte)
    motifs = [s["regex"] for s in signaux
              if normaliser(s["entite"]) == normaliser(entite_signaux)]
    position = None
    for motif in motifs:
        m = motif.search(norme)
        if m:
            position = m.start()
            break
    etiquette = "signal entendu"
    if position is None:
        for nom, motif in INDICATEURS.items():
            m = re.search(motif, norme)
            if m:
                position = m.start()
                etiquette = "mot commercial entendu"
                break
    if position is None:
        return "(transcrite : ni signal ni mot commercial entendu)"
    morceau = texte[max(0, position - 150):position + 200].strip()
    minutage = ""
    if segments:
        import json
        cumul = 0
        for seconde, ligne in json.loads(segments):
            cumul += len(ligne) + 1
            if cumul > position:
                minutage = f"a {int(seconde) // 60}:{int(seconde) % 60:02d} — "
                break
    return f"{minutage}{etiquette} : « …{morceau}… »"


def complements_depuis_base(base, video_id):
    """(description complete, case cochee) si la base les connait."""
    colonnes = [c[1] for c in base.execute("PRAGMA table_info(videos)")]
    if "declaration_commerciale" not in colonnes:
        r = base.execute("SELECT description FROM videos WHERE video_id = ?",
                         (video_id,)).fetchone()
        return (r[0] if r else ""), None
    r = base.execute("SELECT description, declaration_commerciale FROM videos "
                     "WHERE video_id = ?", (video_id,)).fetchone()
    return (r[0] if r else ""), (r[1] if r else None)


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
               "Extrait exact", "Case « communication commerciale »",
               "Mention commerciale (passage)", "Dit dans la video (passage)",
               "TON VERDICT", "Ton commentaire"]
    ws.append(entetes)
    for c in ws[1]:
        c.font = gras
    jaune = PatternFill("solid", fgColor="FFF2CC")
    vert = PatternFill("solid", fgColor="E2EFDA")
    base = sqlite3.connect(chemin_base) if chemin_base.exists() else None
    signaux_actifs, _ = charger_signaux()
    n_cochees = n_passages = n_oraux = 0
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
        description, declaration = (complements_depuis_base(base, d["video_id"])
                                    if base else ("", None))
        libelle = {1: "OUI, cochee par le createur", 0: "non"}.get(
            declaration, "pas encore lue")
        case = ws.cell(rang, 10, libelle)
        if declaration == 1:
            case.fill = vert
            n_cochees += 1
        passage = passage_commercial(description, d["signaux"], d["extrait"])
        if passage:
            n_passages += 1
        cellule_passage = ws.cell(rang, 11, passage)
        cellule_passage.alignment = Alignment(wrap_text=True, vertical="top")
        oral = (passage_oral(base, d["video_id"], d["entite"], signaux_actifs)
                if base else "")
        if oral and not oral.startswith("("):
            n_oraux += 1
        cellule_oral = ws.cell(rang, 12, oral)
        cellule_oral.alignment = Alignment(wrap_text=True, vertical="top")
        # cellules 13 et 14 : a Vincent
    if base:
        base.close()

    if lot:
        validation = DataValidation(
            type="list", formula1='"' + ",".join(VERDICTS) + '"',
            allow_blank=True, showDropDown=False)
        ws.add_data_validation(validation)
        validation.add(f"M2:M{len(lot) + 1}")

    largeurs = {"A": 4, "B": 22, "C": 11, "D": 11, "E": 16, "F": 26, "G": 40,
                "H": 8, "I": 60, "J": 20, "K": 45, "L": 45, "M": 26, "N": 40}
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
        f.write(f"| Extraits verifies contenant leur signal | {len(lot)} / {len(lot)} |\n")
        f.write(f"| dont case « communication commerciale » cochee | {n_cochees} |\n")
        f.write(f"| dont mention commerciale hors extrait, affichee | {n_passages} |\n")
        f.write(f"| dont passage oral (transcription) affiche | {n_oraux} |\n\n")
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
