# -*- coding: utf-8 -*-
"""Re-derive le jeu de reference depuis les classeurs de jugement.

Premier outil du projet veille-filiere. Il ne fait confiance a aucun
chiffre ecrit ailleurs : il ouvre chaque classeur de `acquis/jugements/`,
cherche les feuilles portant une colonne VERDICT, et compte ce qui s'y
trouve reellement.

Sorties, horodatees, dans `recherche/` :
  - jugements_reference_<date>.csv : une ligne par jugement rendu
  - jugements_reference_<date>.md  : la synthese, fichier par fichier

Aucune ecriture ailleurs. Les classeurs sont ouverts en lecture seule.
"""

import csv
import datetime as dt
import unicodedata
from pathlib import Path

import openpyxl

RACINE = Path(__file__).resolve().parent.parent
DOSSIER_JUGEMENTS = RACINE / "acquis" / "jugements"
DOSSIER_RECHERCHE = RACINE / "recherche"


def sans_accents(texte):
    return "".join(
        c for c in unicodedata.normalize("NFD", str(texte))
        if unicodedata.category(c) != "Mn"
    ).lower().strip()


def trouver_colonne(entetes, *mots):
    """Rend l'index de la premiere colonne dont l'entete contient un des mots."""
    for i, entete in enumerate(entetes):
        if entete is None:
            continue
        e = sans_accents(entete)
        if any(mot in e for mot in mots):
            return i
    return None


def lire_classeur(chemin):
    """Rend la liste des jugements du classeur, feuille par feuille."""
    lignes = []
    # Pas de mode read_only : il ne donne pas acces aux hyperliens, or la
    # colonne « Regarder » cache l'URL de la video derriere le mot « ouvrir ».
    wb = openpyxl.load_workbook(chemin, data_only=True)
    for feuille in wb.worksheets:
        # L'entete n'est pas toujours en ligne 1 : certains classeurs
        # commencent par un mode d'emploi. On cherche la premiere ligne
        # contenant une colonne VERDICT.
        toutes_lignes = list(feuille.iter_rows(values_only=True))
        entetes, iterateur = None, []
        for i, candidate in enumerate(toutes_lignes[:50]):
            # Une vraie ligne d'en-tete porte plusieurs colonnes nommees ;
            # une ligne de mode d'emploi qui cite le mot « verdict » n'en a
            # qu'une. On exige au moins quatre cellules remplies.
            if (trouver_colonne(candidate, "verdict") is not None
                    and sum(1 for c in candidate if c is not None
                            and str(c).strip()) >= 4):
                entetes, iterateur = candidate, toutes_lignes[i + 1:]
                premiere_ligne = i + 2
                break
        if entetes is None:
            continue  # pas une feuille de jugement
        col_verdict = trouver_colonne(entetes, "verdict")
        col = {
            "chaine": trouver_colonne(entetes, "chaine", "compte", "createur", "nom"),
            "abonnes": trouver_colonne(entetes, "abonnes"),
            "date": trouver_colonne(entetes, "date"),
            "entite": trouver_colonne(entetes, "entite", "annonceur", "commanditaire"),
            "titre": trouver_colonne(entetes, "titre", "texte"),
            "commentaire": trouver_colonne(entetes, "commentaire"),
        }
        total = 0
        for rang, ligne in enumerate(iterateur, start=premiere_ligne):
            total += 1
            verdict = ligne[col_verdict] if col_verdict < len(ligne) else None
            if verdict is None or str(verdict).strip() == "":
                verdict = None

            def valeur(nom):
                i = col[nom]
                if i is None or i >= len(ligne) or ligne[i] is None:
                    return ""
                v = ligne[i]
                if isinstance(v, dt.datetime):
                    return v.date().isoformat()
                return str(v).strip()

            url = ""
            for cellule in feuille[rang]:
                if cellule.hyperlink and cellule.hyperlink.target:
                    url = cellule.hyperlink.target
                    break
            video_id = ""
            if "watch?v=" in url:
                video_id = url.split("watch?v=")[1].split("&")[0]

            lignes.append({
                "fichier": chemin.name,
                "feuille": feuille.title,
                "rang": rang,
                "video_id": video_id,
                "url": url,
                "chaine": valeur("chaine"),
                "abonnes": valeur("abonnes"),
                "date": valeur("date"),
                "entite": valeur("entite"),
                "titre": valeur("titre"),
                "verdict": str(verdict).strip() if verdict is not None else "",
                "commentaire": valeur("commentaire"),
            })
    wb.close()
    return lignes


def principal():
    horodatage = dt.date.today().isoformat()
    DOSSIER_RECHERCHE.mkdir(exist_ok=True)

    toutes = []
    for chemin in sorted(DOSSIER_JUGEMENTS.glob("*.xlsx")):
        toutes.extend(lire_classeur(chemin))

    jugees = [l for l in toutes if l["verdict"]]

    chemin_csv = DOSSIER_RECHERCHE / f"jugements_reference_{horodatage}.csv"
    with open(chemin_csv, "w", newline="", encoding="utf-8-sig") as f:
        champs = ["fichier", "feuille", "rang", "video_id", "url", "chaine",
                  "abonnes", "date", "entite", "titre", "verdict",
                  "commentaire"]
        ecrivain = csv.DictWriter(f, fieldnames=champs)
        ecrivain.writeheader()
        ecrivain.writerows(jugees)

    # Synthese par fichier puis par verdict.
    par_fichier = {}
    for l in toutes:
        cle = f"{l['fichier']} / {l['feuille']}"
        d = par_fichier.setdefault(cle, {"total": 0, "jugees": 0, "verdicts": {}})
        d["total"] += 1
        if l["verdict"]:
            d["jugees"] += 1
            v = sans_accents(l["verdict"])
            d["verdicts"][v] = d["verdicts"].get(v, 0) + 1

    commentaires = sum(1 for l in jugees if l["commentaire"])

    chemin_md = DOSSIER_RECHERCHE / f"jugements_reference_{horodatage}.md"
    with open(chemin_md, "w", encoding="utf-8") as f:
        f.write(f"# Jeu de reference re-derive — {horodatage}\n\n")
        f.write("Produit par `outils/jugements_reference.py`, qui ouvre chaque\n")
        f.write("classeur de `acquis/jugements/` et compte les verdicts reellement\n")
        f.write("presents. Aucun chiffre repris d'un document.\n\n")
        f.write(f"**Total des lignes soumises a jugement : {len(toutes)}**\n")
        f.write(f"**Total des verdicts rendus : {len(jugees)}**\n")
        f.write(f"**Verdicts accompagnes d'un commentaire : {commentaires}**\n")
        avec_id = sum(1 for l in jugees if l["video_id"])
        f.write(f"**Verdicts relies a un identifiant video : {avec_id}**\n\n")
        f.write("| Fichier / feuille | Lignes | Jugees | Detail des verdicts |\n")
        f.write("|---|---:|---:|---|\n")
        for cle, d in sorted(par_fichier.items()):
            detail = ", ".join(
                f"{v} : {n}" for v, n in sorted(d["verdicts"].items(),
                                               key=lambda x: -x[1])
            ) or "—"
            f.write(f"| {cle} | {d['total']} | {d['jugees']} | {detail} |\n")
        f.write("\nLe detail ligne par ligne est dans "
                f"`{chemin_csv.name}`.\n")

    print(f"Lignes soumises : {len(toutes)}")
    print(f"Verdicts rendus : {len(jugees)}")
    print(f"Ecrit : {chemin_csv}")
    print(f"Ecrit : {chemin_md}")


if __name__ == "__main__":
    principal()
