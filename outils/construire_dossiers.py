# -*- coding: utf-8 -*-
"""Construit les tables de sortie (MODELE_DE_SORTIE.md) depuis les verdicts.

Regle d'or : une ligne de `collaborations` n'existe que si un humain a
rendu le verdict « collaboration remuneree » sur ce contenu. L'outil ne
fait qu'assembler autour de ce verdict les elements factuels : le compte,
l'audience, les signaux observes, l'extrait.

Entrees :
  - recherche/jugements_reference_*.csv  (les verdicts historiques)
  - donnees/jugements_recoltes.csv       (les verdicts des nouveaux lots)
  - donnees/veille.sqlite                (videos, comptes)
  - donnees/detections.csv               (signaux et extraits)
  - DICTIONNAIRE.xlsx feuille Entites    (les commanditaires)

Sorties : donnees/sortie/{commanditaires,createurs,comptes,
collaborations}.csv — **RIEN N'EST PUBLIE** : c'est la forme cible,
produite pour etre relue. Rapport dans recherche/.
"""

import csv
import datetime as dt
import re
import sqlite3
import unicodedata
from pathlib import Path

import openpyxl

RACINE = Path(__file__).resolve().parent.parent
DOSSIER_SORTIE = RACINE / "donnees" / "sortie"
DOSSIER_RECHERCHE = RACINE / "recherche"
CHEMIN_BASE = RACINE / "donnees" / "veille.sqlite"
CHEMIN_RECOLTES = RACINE / "donnees" / "jugements_recoltes.csv"
CHEMIN_DETECTIONS = RACINE / "donnees" / "detections.csv"
CHEMIN_DICO = RACINE / "DICTIONNAIRE.xlsx"

VERDICT_VRAI = "collaboration remuneree"


def normaliser(texte):
    t = unicodedata.normalize("NFD", str(texte))
    t = "".join(c for c in t if unicodedata.category(c) not in ("Mn", "Cf"))
    return " ".join(t.lower().split())


def slug(texte):
    n = normaliser(texte)
    n = re.sub(r"[^a-z0-9]+", "-", n).strip("-")
    return n or "inconnu"


def charger_verdicts():
    """Tous les verdicts « collaboration remuneree », dedupliques."""
    lignes = {}
    for chemin in sorted(DOSSIER_RECHERCHE.glob("jugements_reference_*.csv")):
        with open(chemin, encoding="utf-8-sig") as f:
            for j in csv.DictReader(f):
                if normaliser(j["verdict"]) == VERDICT_VRAI:
                    lignes[(j["video_id"], normaliser(j["entite"]))] = j
    if CHEMIN_RECOLTES.exists():
        with open(CHEMIN_RECOLTES, encoding="utf-8-sig") as f:
            for j in csv.DictReader(f):
                if normaliser(j["verdict"]) == VERDICT_VRAI:
                    lignes[(j["video_id"], normaliser(j["entite"]))] = j
    return list(lignes.values())


def principal():
    aujourd_hui = dt.date.today().isoformat()
    DOSSIER_SORTIE.mkdir(parents=True, exist_ok=True)

    # Les commanditaires, depuis le dictionnaire.
    wb = openpyxl.load_workbook(CHEMIN_DICO, read_only=True, data_only=True)
    lignes_e = list(wb["Entites"].iter_rows(values_only=True))
    wb.close()
    entetes_e = [str(c or "").strip() for c in lignes_e[0]]
    commanditaires = {}
    for l in lignes_e[1:]:
        d = dict(zip(entetes_e, l))
        if d.get("entite"):
            commanditaires[normaliser(d["entite"])] = {
                "commanditaire_id": slug(d["entite"]),
                "nom": str(d["entite"]).strip(),
                "type": str(d.get("type_entite") or "").strip(),
                "rattachement": str(d.get("rattachement") or "").strip(),
                "produits": str(d.get("produit") or "").strip(),
            }

    verdicts = charger_verdicts()
    base = sqlite3.connect(CHEMIN_BASE)
    detections = {}
    with open(CHEMIN_DETECTIONS, encoding="utf-8-sig") as f:
        for d in csv.DictReader(f):
            detections[(d["video_id"], normaliser(d["entite"]))] = d

    createurs, comptes, collaborations = {}, {}, []
    commanditaires_utilises = {}
    sans_compte = 0
    for n, j in enumerate(sorted(verdicts, key=lambda x: x.get("chaine", "")),
                          start=1):
        video_id = j["video_id"]
        ligne_video = base.execute(
            "SELECT compte_id, publiee FROM videos WHERE video_id = ?",
            (video_id,)).fetchone()
        compte_plateforme = ligne_video[0] if ligne_video else ""
        if not compte_plateforme:
            sans_compte += 1
        nom_createur = (j.get("chaine") or "").strip() or "?"
        createur_id = slug(nom_createur)
        createurs.setdefault(createur_id, {
            "createur_id": createur_id,
            "nom_public": nom_createur,
            "categorie": "a categoriser",
        })
        compte_id = f"youtube:{compte_plateforme}" if compte_plateforme else ""
        if compte_id:
            comptes.setdefault(compte_id, {
                "compte_id": compte_id,
                "createur_id": createur_id,
                "plateforme": "youtube",
                "identifiant_public": nom_createur,
                "audience": j.get("abonnes", ""),
                "audience_relevee_le": aujourd_hui,
            })

        for entite_brute in j["entite"].split("|"):
            cle_entite = normaliser(entite_brute)
            comm = commanditaires.get(cle_entite)
            if comm:
                commanditaires_utilises[cle_entite] = comm
            det = detections.get((video_id, cle_entite))
            signaux = (det["signaux"] + " ; indices : "
                       + (det["indices_commerciaux"] or "aucun")) if det \
                else "mention jugee sur piece par un humain (hors detecteur)"
            collaborations.append({
                "collaboration_id": f"c-{n:06d}",
                "createur_id": createur_id,
                "compte_id": compte_id,
                "commanditaire_id": comm["commanditaire_id"] if comm
                                     else slug(entite_brute),
                "contenu_url": j.get("url", ""),
                "contenu_titre": j.get("titre", ""),
                "publie_le": j.get("date", ""),
                "signaux_observes": signaux,
                "extrait": (det or {}).get("extrait", ""),
                "degre": "collaboration remuneree (verdict humain)",
                "constate_le": j.get("recolte_le", "") or "2026-08",
                "note_interne_NE_PAS_PUBLIER": (j.get("commentaire") or "")[:120],
            })
    base.close()

    tables = {
        "commanditaires": list(commanditaires_utilises.values()),
        "createurs": list(createurs.values()),
        "comptes": list(comptes.values()),
        "collaborations": collaborations,
    }
    for nom, lignes in tables.items():
        chemin = DOSSIER_SORTIE / f"{nom}.csv"
        with open(chemin, "w", newline="", encoding="utf-8-sig") as f:
            if lignes:
                w = csv.DictWriter(f, fieldnames=list(lignes[0].keys()))
                w.writeheader()
                w.writerows(lignes)

    par_commanditaire = {}
    for c in collaborations:
        par_commanditaire[c["commanditaire_id"]] = \
            par_commanditaire.get(c["commanditaire_id"], 0) + 1

    chemin_rapport = DOSSIER_RECHERCHE / f"dossiers_{aujourd_hui}.md"
    with open(chemin_rapport, "w", encoding="utf-8") as f:
        f.write(f"# Tables de sortie construites — {aujourd_hui}\n\n")
        f.write("Produit par `outils/construire_dossiers.py` selon "
                "`MODELE_DE_SORTIE.md`. **RIEN N'EST PUBLIE** : forme "
                "cible, a relire.\n\n")
        f.write("| Table | Lignes |\n|---|---:|\n")
        for nom, lignes in tables.items():
            f.write(f"| {nom} | {len(lignes)} |\n")
        f.write(f"| collaborations sans compte retrouve | {sans_compte} |\n\n")
        f.write("## Collaborations par commanditaire\n\n")
        for cid, nb in sorted(par_commanditaire.items(), key=lambda x: -x[1]):
            f.write(f"- {cid} : {nb}\n")
        f.write("\nAvant toute publication : verification finale, courrier "
                "prealable aux createurs, decision « qui publie ».\n")

    print(f"createurs : {len(createurs)}  |  comptes : {len(comptes)}  |  "
          f"collaborations : {len(collaborations)}")
    print(f"Ecrit : {DOSSIER_SORTIE}")
    print(f"Ecrit : {chemin_rapport}")


if __name__ == "__main__":
    principal()
