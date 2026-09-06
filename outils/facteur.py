# -*- coding: utf-8 -*-
"""Le facteur : la veille incrementale quotidienne (critere 1 du contrat).

Pour chaque compte surveille de la base, il demande a YouTube « quoi de
neuf ? » via le FLUX RSS public de la chaine — gratuit, sans cle, sans
authentification, ~15 dernieres videos avec titre et description. Puis :

  1. il enregistre TOUTE video nouvelle dans `videos` (signal ou pas —
     regle du 06/09 : tout ce qui est lu est garde) ;
  2. il passe la detection (`detecter.analyser`, la fonction partagee) sur
     les nouvelles et range les resultats dans `detections` ;
  3. il avance le curseur du compte — apres ecriture reussie seulement.

Idempotence : une video deja connue est ignoree (INSERT OR IGNORE), donc
relancer le facteur ne refait rien, et reparer une panne = relancer.
Chaque compte est valide dans sa propre transaction : une coupure en pleine
tournee ne corrompt rien et ne perd que le compte en cours.

Usage :
  python outils/facteur.py --limite 5     # tournee d'essai sur 5 comptes
  python outils/facteur.py                # tournee complete

Chaque tournee ecrit son rapport horodate dans `recherche/`.
"""

import argparse
import datetime as dt
import sqlite3
import sys
import time
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from detecter import analyser, canaux_vitrines_depuis, charger_signaux, \
    normaliser_positionnel  # noqa: E402

RACINE = Path(__file__).resolve().parent.parent
CHEMIN_BASE = RACINE / "donnees" / "veille.sqlite"
DOSSIER_RECHERCHE = RACINE / "recherche"

URL_FLUX = "https://www.youtube.com/feeds/videos.xml?channel_id={}"
ESPACES = {
    "a": "http://www.w3.org/2005/Atom",
    "yt": "http://www.youtube.com/xml/schemas/2015",
    "media": "http://search.yahoo.com/mrss/",
}
PAUSE_ENTRE_FLUX = 0.3  # secondes — politesse
DELAI_HTTP = 15


def lire_flux(compte_id):
    """Rend la liste des videos du flux RSS public de la chaine."""
    requete = urllib.request.Request(
        URL_FLUX.format(compte_id),
        headers={"User-Agent": "veille-filiere/1.0 (registre associatif; "
                               "contact via depot github Tamateatea)"})
    with urllib.request.urlopen(requete, timeout=DELAI_HTTP) as reponse:
        arbre = ET.fromstring(reponse.read())
    videos = []
    for entree in arbre.findall("a:entry", ESPACES):
        def texte(chemin):
            n = entree.find(chemin, ESPACES)
            return n.text if n is not None and n.text else ""
        videos.append({
            "video_id": texte("yt:videoId"),
            "titre": texte("a:title"),
            "publiee": texte("a:published")[:10],
            "description": texte("media:group/media:description"),
        })
    return videos


def principal():
    parseur = argparse.ArgumentParser()
    parseur.add_argument("--limite", type=int, default=None,
                         help="ne visiter que N comptes (tournee d'essai)")
    args = parseur.parse_args()

    signaux, _ = charger_signaux()
    vitrines = canaux_vitrines_depuis(signaux)
    base = sqlite3.connect(CHEMIN_BASE)
    maintenant = dt.datetime.now().isoformat(timespec="seconds")

    # Les comptes jamais visites d'abord, puis les plus anciens passages :
    # une tournee interrompue reprend naturellement ou elle s'est arretee.
    comptes = base.execute(
        "SELECT c.compte_id, c.nom FROM comptes c "
        "LEFT JOIN curseurs k ON k.compte_id = c.compte_id "
        "WHERE c.surveille = 1 "
        "ORDER BY k.dernier_passage IS NOT NULL, k.dernier_passage").fetchall()
    if args.limite:
        comptes = comptes[:args.limite]

    visites = echecs = nouvelles = detectees = 0
    detections_du_jour = []
    for compte_id, nom in comptes:
        try:
            flux = lire_flux(compte_id)
        except (urllib.error.URLError, ET.ParseError, TimeoutError, OSError):
            echecs += 1
            continue
        visites += 1
        est_vitrine = (normaliser_positionnel(nom or "").lstrip("@")
                       in vitrines)
        try:
            with base:  # une transaction par compte
                for v in flux:
                    if not v["video_id"]:
                        continue
                    insere = base.execute(
                        "INSERT OR IGNORE INTO videos (video_id, compte_id, "
                        "titre, description, publiee, url, lue_le) "
                        "VALUES (?, ?, ?, ?, ?, ?, ?)",
                        (v["video_id"], compte_id, v["titre"],
                         v["description"], v["publiee"],
                         f"https://www.youtube.com/watch?v={v['video_id']}",
                         maintenant)).rowcount
                    if not insere:
                        continue  # deja connue : idempotence
                    nouvelles += 1
                    if est_vitrine:
                        continue  # contenu du lobby : flux decouverte
                    texte = f"{v['titre']}\n{v['description']}"
                    for d in analyser(texte, signaux):
                        d.pop("signaux_touches", None)
                        base.execute(
                            "INSERT OR IGNORE INTO detections (video_id, "
                            "entite, signaux, types_signaux, force, "
                            "indices_commerciaux, extrait, detectee_le) "
                            "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                            (v["video_id"], d["entite"], d["signaux"],
                             d["types_signaux"], d["force"],
                             d["indices_commerciaux"], d["extrait"],
                             maintenant))
                        detectees += 1
                        detections_du_jour.append(
                            (nom or compte_id, d["entite"], d["force"],
                             d["signaux"], v["titre"][:60]))
                base.execute(
                    "INSERT INTO curseurs (compte_id, dernier_passage) "
                    "VALUES (?, ?) ON CONFLICT(compte_id) "
                    "DO UPDATE SET dernier_passage = excluded.dernier_passage",
                    (compte_id, maintenant))
        except sqlite3.Error:
            echecs += 1
            continue
        time.sleep(PAUSE_ENTRE_FLUX)
    base.close()

    horodatage = dt.datetime.now().strftime("%Y-%m-%d_%H%M")
    chemin_rapport = DOSSIER_RECHERCHE / f"facteur_{horodatage}.md"
    with open(chemin_rapport, "w", encoding="utf-8") as f:
        f.write(f"# Tournee du facteur — {maintenant}\n\n")
        f.write("Produit par `outils/facteur.py` (flux RSS publics, zero "
                "quota API).\n\n")
        f.write("| | |\n|---|---:|\n")
        f.write(f"| Comptes visites | {visites} |\n")
        f.write(f"| Flux en echec | {echecs} |\n")
        f.write(f"| Videos nouvelles enregistrees | {nouvelles} |\n")
        f.write(f"| Detections nouvelles | {detectees} |\n\n")
        if detections_du_jour:
            f.write("| Compte | Entite | Force | Signaux | Titre |\n")
            f.write("|---|---|---|---|---|\n")
            for ligne in detections_du_jour:
                f.write("| " + " | ".join(str(x) for x in ligne) + " |\n")
        else:
            f.write("Aucune detection nouvelle cette tournee.\n")

    print(f"Comptes visites : {visites} (echecs : {echecs})")
    print(f"Videos nouvelles : {nouvelles}  |  Detections : {detectees}")
    print(f"Ecrit : {chemin_rapport}")


if __name__ == "__main__":
    principal()
