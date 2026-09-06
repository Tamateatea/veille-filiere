# -*- coding: utf-8 -*-
"""Integre les decisions de PROPOSITIONS.xlsx dans le systeme.

Contexte : le pre-tri de Claude sur les 259 propositions a ete valide en
bloc par Vincent le 06/09 (« j'ai regarde vite fait et je te fais
confiance »). Ce script transforme ces decisions en effets concrets :

  - « suivre ce compte » (createurs et chefs) -> le compte entre dans la
    table `comptes` de la base et le facteur le visitera chaque nuit.
    Si on ne connait pas sa chaine YouTube, on tente de la resoudre par la
    page publique youtube.com/@identifiant (aucune authentification) ;
    ce qui ne se resout pas est consigne « a resoudre », rien n'est perdu.
  - « signal pour le dictionnaire » -> ajoute a DICTIONNAIRE.xlsx en statut
    `propose`, force `faible`. Ils NE DETECTENT PAS encore : le critere 11
    exige une confirmation par signal, et la famille des noms de series a
    deja produit des faux positifs mesures (CHAUD !).
  - les categories « ignorer » et « a toi de voir » ne changent rien.

La colonne TA DECISION du classeur est remplie avec la decision ratifiee,
tracee « valide en bloc par Vincent (06/09) ».

Sorties : recherche/integration_propositions_<date>.md, et
donnees/suivis_confirmes.csv (la liste, resolue ou a resoudre).
"""

import csv
import datetime as dt
import re
import sqlite3
import time
import unicodedata
import urllib.error
import urllib.request
from pathlib import Path

import openpyxl

RACINE = Path(__file__).resolve().parent.parent
CHEMIN_PROPOSITIONS = RACINE / "PROPOSITIONS.xlsx"
CHEMIN_DICO = RACINE / "DICTIONNAIRE.xlsx"
CHEMIN_BASE = RACINE / "donnees" / "veille.sqlite"
CHEMIN_SUIVIS = RACINE / "donnees" / "suivis_confirmes.csv"
DOSSIER_RECHERCHE = RACINE / "recherche"

MENTION_RATIFICATION = "valide en bloc par Vincent (06/09)"
# Le lien canonique est le SEUL marqueur fiable : le premier "channelId"
# du HTML est souvent celui d'une chaine recommandee, pas celui de la page.
MOTIF_CANONIQUE = re.compile(
    r'<link rel="canonical" href="https://www\.youtube\.com/channel/'
    r'(UC[0-9A-Za-z_-]{22})"')


def normaliser(texte):
    t = unicodedata.normalize("NFD", str(texte))
    t = "".join(c for c in t if unicodedata.category(c) not in ("Mn", "Cf"))
    return " ".join(t.lower().split())


def resoudre_chaine_youtube(pseudo):
    """Cherche l'identifiant de chaine derriere youtube.com/@pseudo."""
    if not re.fullmatch(r"[A-Za-z0-9_.\-]{3,30}", pseudo):
        return None  # pas une forme de pseudo : inutile d'essayer
    url = f"https://www.youtube.com/@{pseudo}"
    requete = urllib.request.Request(
        url, headers={"User-Agent": "Mozilla/5.0 (veille-filiere/1.0)"})
    try:
        with urllib.request.urlopen(requete, timeout=20) as reponse:
            page = reponse.read().decode("utf-8", errors="replace")
    except (urllib.error.URLError, TimeoutError, OSError):
        return None
    m = MOTIF_CANONIQUE.search(page)
    return m.group(1) if m else None


def principal():
    wb = openpyxl.load_workbook(CHEMIN_PROPOSITIONS)
    ws = wb["propositions"]
    entetes = [str(c.value or "") for c in ws[1]]
    col = {nom: entetes.index(nom) + 1 for nom in entetes if nom}

    suivre, signaux_proposes = [], []
    for rang in range(2, ws.max_row + 1):
        pretri = str(ws.cell(rang, col["PRE-TRI CLAUDE"]).value or "")
        if not pretri or pretri == "a toi de voir":
            continue
        decision_cell = ws.cell(rang, col["TA DECISION"])
        if not decision_cell.value:
            if pretri.startswith("suivre"):
                decision_cell.value = "suivre ce compte"
            elif pretri.startswith("signal"):
                decision_cell.value = "je ne sais pas"  # entre en propose
            else:
                decision_cell.value = "ignorer"
            commentaire = ws.cell(rang, col["Ton commentaire"])
            commentaire.value = MENTION_RATIFICATION
        ligne = {
            "nom": str(ws.cell(rang, col["Proposition"]).value or "").strip(),
            "identifiant": str(ws.cell(rang, col["Identifiant"]).value
                               or "").strip().lstrip("@"),
            "entites": str(ws.cell(rang, col["Lobbies concernes"]).value
                           or "").strip(),
            "categorie": pretri,
        }
        if pretri.startswith("suivre"):
            suivre.append(ligne)
        elif pretri.startswith("signal"):
            signaux_proposes.append(ligne)
    wb.save(CHEMIN_PROPOSITIONS)

    # 1. Les comptes a suivre : deja connus, resolus, ou a resoudre.
    base = sqlite3.connect(CHEMIN_BASE)
    noms_connus = {normaliser(nom): cid for cid, nom in base.execute(
        "SELECT compte_id, nom FROM comptes WHERE nom IS NOT NULL")}
    maintenant = dt.datetime.now().isoformat(timespec="seconds")
    resultats = []
    n_deja = n_resolus = n_a_resoudre = 0
    for s in suivre:
        cid = noms_connus.get(normaliser(s["nom"]))
        statut = ""
        if cid:
            n_deja += 1
            statut = f"deja surveille ({cid})"
        else:
            pseudo = s["identifiant"] or s["nom"].replace(" ", "")
            cid = resoudre_chaine_youtube(pseudo)
            time.sleep(0.4)
            if cid:
                existe = base.execute(
                    "SELECT nom FROM comptes WHERE compte_id = ?",
                    (cid,)).fetchone()
                if existe:
                    n_deja += 1
                    statut = f"deja surveille ({cid})"
                else:
                    base.execute(
                        "INSERT INTO comptes (compte_id, nom, surveille, "
                        "ajoute_le) VALUES (?, ?, 1, ?)",
                        (cid, s["nom"], maintenant))
                    n_resolus += 1
                    statut = f"AJOUTE a la surveillance ({cid})"
            else:
                n_a_resoudre += 1
                statut = "a resoudre (pas de chaine YouTube trouvee — " \
                         "probablement Instagram/TikTok)"
        resultats.append({**s, "resolution": statut})
    base.commit()
    base.close()

    with open(CHEMIN_SUIVIS, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=["nom", "identifiant", "entites",
                                          "categorie", "resolution"])
        w.writeheader()
        w.writerows(resultats)

    # 2. Les signaux proposes pour le dictionnaire (statut propose).
    wb = openpyxl.load_workbook(CHEMIN_DICO)
    feuille = wb["Signaux"]
    entetes_dico = [str(c.value or "") for c in feuille[1]]
    existants = {normaliser(feuille.cell(r, entetes_dico.index("texte") + 1)
                            .value or "")
                 for r in range(2, feuille.max_row + 1)}
    aujourd_hui = dt.date.today().isoformat()
    n_signaux = 0
    for s in signaux_proposes:
        if normaliser(s["nom"]) in existants:
            continue
        ligne = {c: "" for c in entetes_dico}
        ligne.update({
            "texte": s["nom"], "type_signal": "nom de serie ou de campagne",
            "entite": s["entites"].split(" | ")[0], "statut": "propose",
            "force": "faible", "ajoute_le": aujourd_hui,
            "source": "decouverte vitrines 06/09, " + MENTION_RATIFICATION,
            "commentaire": "ne detecte pas tant que non confirme signal "
                           "par signal (critere 11)",
        })
        feuille.append([ligne.get(c, "") for c in entetes_dico])
        n_signaux += 1
    wb.save(CHEMIN_DICO)

    chemin_rapport = (DOSSIER_RECHERCHE
                      / f"integration_propositions_{aujourd_hui}.md")
    with open(chemin_rapport, "w", encoding="utf-8") as f:
        f.write(f"# Integration des propositions — {aujourd_hui}\n\n")
        f.write("Pre-tri de Claude ratifie en bloc par Vincent (06/09).\n\n")
        f.write("| | |\n|---|---:|\n")
        f.write(f"| Comptes a suivre | {len(suivre)} |\n")
        f.write(f"| deja sous surveillance | {n_deja} |\n")
        f.write(f"| chaines YouTube resolues et AJOUTEES | {n_resolus} |\n")
        f.write(f"| a resoudre (autre plateforme) | {n_a_resoudre} |\n")
        f.write(f"| Signaux ajoutes au dictionnaire en `propose` | {n_signaux} |\n\n")
        f.write(f"Detail : `donnees/suivis_confirmes.csv`.\n")

    print(f"A suivre : {len(suivre)} (deja : {n_deja}, ajoutes : {n_resolus}, "
          f"a resoudre : {n_a_resoudre})")
    print(f"Signaux proposes ajoutes : {n_signaux}")
    print(f"Ecrit : {chemin_rapport}")


if __name__ == "__main__":
    principal()
