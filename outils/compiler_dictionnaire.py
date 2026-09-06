# -*- coding: utf-8 -*-
"""Compile le dictionnaire initial depuis les deux sources d'acquis.

Sources, en lecture seule :
  - acquis/cartographie/cartographie_filiere.xlsx, feuille `Alias`
    (65 signaux types et statues, heritage de l'ancien projet) ;
  - acquis/cartographie/Preliminary dataset.xlsx, feuille
    `Cartographie des lobbies` (la structure entite -> groupe -> marque et
    les hashtags observes, etablie a la main par Vincent le 31/08/2026).

Sortie : `DICTIONNAIRE.xlsx` a la racine du projet, deux feuilles :
  - `Entites` : une ligne par commanditaire possible ;
  - `Signaux` : une ligne par chaine de caracteres detectable.

REGLE (critere 5 du contrat) : une fois cree, ce classeur est le MAITRE.
Vincent l'edite directement ; les outils le lisent. Ce script REFUSE donc
d'ecraser un dictionnaire existant : il ne sert qu'a l'amorcage.

Chaque execution ecrit son rapport dans `recherche/`, horodate.
"""

import datetime as dt
import sys
import unicodedata
from pathlib import Path

import openpyxl
from openpyxl.styles import Font

RACINE = Path(__file__).resolve().parent.parent
CHEMIN_ALIAS = RACINE / "acquis" / "cartographie" / "cartographie_filiere.xlsx"
CHEMIN_VINCENT = RACINE / "acquis" / "cartographie" / "Preliminary dataset.xlsx"
CHEMIN_DICO = RACINE / "DICTIONNAIRE.xlsx"
DOSSIER_RECHERCHE = RACINE / "recherche"

COLONNES_ENTITES = ["entite", "nom_complet", "type_entite", "rattachement",
                    "produit", "statut", "source"]
COLONNES_SIGNAUX = ["texte", "type_signal", "entite", "plateforme", "statut",
                    "source", "ajoute_le", "commentaire"]


def normaliser(texte):
    """Cle de deduplication : minuscules, sans accents, sans invisible."""
    t = unicodedata.normalize("NFD", str(texte))
    t = "".join(c for c in t if unicodedata.category(c) not in ("Mn", "Cf"))
    return " ".join(t.lower().split())


def lire_feuille(chemin, nom_feuille):
    wb = openpyxl.load_workbook(chemin, read_only=True, data_only=True)
    lignes = list(wb[nom_feuille].iter_rows(values_only=True))
    wb.close()
    return lignes


def depuis_table_alias():
    """La feuille Alias heritee : deja typee, deja statuee."""
    lignes = lire_feuille(CHEMIN_ALIAS, "Alias")
    entetes = [normaliser(c or "") for c in lignes[0]]
    i_alias = entetes.index("alias_observe")
    i_type = entetes.index("type_alias")
    i_entite = entetes.index("entite_reelle")
    i_statut = entetes.index("statut")
    i_pourquoi = entetes.index("pourquoi_ca_compte")

    signaux = []
    for l in lignes[1:]:
        if not l[i_alias]:
            continue
        commentaire = str(l[i_pourquoi] or "").strip()
        statut_source = str(l[i_statut] or "").strip().upper()
        hors_perimetre = "HORS PERIMETRE" in commentaire.upper()
        if hors_perimetre:
            statut = "temoin"          # groupe temoin cerealier, garde a part
        elif statut_source == "CONFIRME":
            statut = "confirme"
        else:
            statut = "propose"         # A VERIFIER et tout le reste
        signaux.append({
            "texte": str(l[i_alias]).strip(),
            "type_signal": str(l[i_type] or "").strip(),
            "entite": str(l[i_entite] or "").strip(),
            "plateforme": "",
            "statut": statut,
            "source": "cartographie_filiere.xlsx / Alias",
            "commentaire": commentaire[:200],
        })
    return signaux


def depuis_cartographie_vincent():
    """Le classeur manuel de Vincent : entites, comptes et hashtags."""
    lignes = lire_feuille(CHEMIN_VINCENT, "Cartographie des lobbies")
    # La ligne 1 est un cartouche « Derniere MaJ » ; l'entete est ligne 2.
    entetes = [normaliser(c or "") for c in lignes[1]]

    def col(fragment):
        for i, e in enumerate(entetes):
            if fragment in e:
                return i
        raise ValueError(f"colonne '{fragment}' introuvable : {entetes}")

    i_nom = col("lobby")
    i_complet = col("nom complet")
    i_type = col("type d'entite")
    i_groupe = col("groupe")
    i_produit = col("produit")
    i_compte = col("alias ou nom du compte")
    i_hashtag = col("hashtag")
    i_reseau = col("reseau")

    source = "Preliminary dataset.xlsx (Vincent, 31/08/2026)"
    entites, signaux = {}, []
    for l in lignes[2:]:
        nom = str(l[i_nom] or "").strip()
        if not nom:
            continue
        if nom not in entites:
            entites[nom] = {
                "entite": nom,
                "nom_complet": str(l[i_complet] or "").strip(),
                "type_entite": str(l[i_type] or "").strip(),
                "rattachement": str(l[i_groupe] or "").strip()
                                 .replace("NA", ""),
                "produit": str(l[i_produit] or "").strip(),
                "statut": "confirme",
                "source": source,
            }
        plateforme = str(l[i_reseau] or "").strip()
        compte = str(l[i_compte] or "").strip()
        if compte:
            signaux.append({
                "texte": compte, "type_signal": "compte vitrine",
                "entite": nom, "plateforme": plateforme,
                "statut": "confirme", "source": source, "commentaire": "",
            })
        for jeton in str(l[i_hashtag] or "").split():
            jeton = "".join(c for c in jeton
                            if unicodedata.category(c) != "Cf").strip()
            if jeton.startswith("#") and len(jeton) > 1:
                signaux.append({
                    "texte": jeton, "type_signal": "hashtag",
                    "entite": nom, "plateforme": plateforme,
                    "statut": "confirme", "source": source, "commentaire": "",
                })
        # Le nom d'une marque est lui-meme une chaine detectable.
        if str(l[i_type] or "").strip().lower() == "marque":
            signaux.append({
                "texte": nom, "type_signal": "nom de marque",
                "entite": nom, "plateforme": "",
                "statut": "confirme", "source": source, "commentaire": "",
            })
    return list(entites.values()), signaux


def principal():
    if CHEMIN_DICO.exists() and "--forcer" not in sys.argv:
        sys.exit(f"{CHEMIN_DICO.name} existe deja : c'est le classeur maitre, "
                 "il n'est pas regenere. (--forcer pour l'ecraser sciemment.)")

    signaux_herites = depuis_table_alias()
    entites, signaux_vincent = depuis_cartographie_vincent()

    # Deduplication par (texte normalise, entite normalisee).
    # La version de Vincent (plus recente) l'emporte, mais on garde la
    # plateforme et le commentaire les plus renseignes.
    fusion = {}
    doublons = 0
    for s in signaux_herites + signaux_vincent:
        cle = (normaliser(s["texte"]), normaliser(s["entite"]))
        if cle in fusion:
            doublons += 1
            existant = fusion[cle]
            existant["plateforme"] = existant["plateforme"] or s["plateforme"]
            existant["commentaire"] = existant["commentaire"] or s["commentaire"]
            existant["source"] += " + " + s["source"]
        else:
            fusion[cle] = dict(s)
    signaux = sorted(fusion.values(),
                     key=lambda s: (s["entite"], s["type_signal"], s["texte"]))

    aujourd_hui = dt.date.today().isoformat()
    wb = openpyxl.Workbook()

    feuille_e = wb.active
    feuille_e.title = "Entites"
    feuille_e.append(COLONNES_ENTITES)
    for e in sorted(entites, key=lambda e: (e["type_entite"], e["entite"])):
        feuille_e.append([e[c] for c in COLONNES_ENTITES])

    feuille_s = wb.create_sheet("Signaux")
    feuille_s.append(COLONNES_SIGNAUX)
    for s in signaux:
        s["ajoute_le"] = aujourd_hui
        feuille_s.append([s[c] for c in COLONNES_SIGNAUX])

    for feuille, largeur in ((feuille_e, 30), (feuille_s, 34)):
        for cellule in feuille[1]:
            cellule.font = Font(bold=True)
        for colonne in feuille.columns:
            lettre = colonne[0].column_letter
            feuille.column_dimensions[lettre].width = min(
                largeur, max(12, max(len(str(c.value or "")) for c in colonne) + 2))
        feuille.freeze_panes = "A2"

    wb.save(CHEMIN_DICO)

    par_statut = {}
    for s in signaux:
        par_statut[s["statut"]] = par_statut.get(s["statut"], 0) + 1

    DOSSIER_RECHERCHE.mkdir(exist_ok=True)
    chemin_rapport = DOSSIER_RECHERCHE / f"dictionnaire_{aujourd_hui}.md"
    with open(chemin_rapport, "w", encoding="utf-8") as f:
        f.write(f"# Amorcage du dictionnaire — {aujourd_hui}\n\n")
        f.write("Produit par `outils/compiler_dictionnaire.py` depuis les deux\n")
        f.write("sources d'`acquis/cartographie/`. Fichier cree : "
                "`DICTIONNAIRE.xlsx` (le maitre, edite ensuite a la main).\n\n")
        f.write(f"| | |\n|---|---:|\n")
        f.write(f"| Entites | {len(entites)} |\n")
        f.write(f"| Signaux herites (feuille Alias) | {len(signaux_herites)} |\n")
        f.write(f"| Signaux de la cartographie de Vincent | {len(signaux_vincent)} |\n")
        f.write(f"| Doublons fusionnes | {doublons} |\n")
        f.write(f"| **Signaux au total** | **{len(signaux)}** |\n")
        for statut, n in sorted(par_statut.items()):
            f.write(f"| dont statut `{statut}` | {n} |\n")
        f.write("\nSeuls les signaux `confirme` entrent en detection "
                "(critere 11 du contrat). Les `propose` attendent Vincent, "
                "les `temoin` servent de groupe de controle cerealier.\n")

    print(f"Entites : {len(entites)}  |  Signaux : {len(signaux)} "
          f"({doublons} doublons fusionnes)")
    print(f"Ecrit : {CHEMIN_DICO}")
    print(f"Ecrit : {chemin_rapport}")


if __name__ == "__main__":
    principal()
