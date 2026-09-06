# -*- coding: utf-8 -*-
"""Le detecteur : cherche les signaux du dictionnaire dans le corpus gele.

Entrees :
  - DICTIONNAIRE.xlsx, feuille `Signaux` — seuls les signaux `confirme`
    detectent ; les `temoin` (groupe de controle cerealier) sont comptes a
    part ; les `propose` sont ignores (critere 11 du contrat).
  - acquis/donnees_brutes/moisson_videos.json, cle `touchees` — les videos
    candidates conservees du corpus gele, avec leur description.

Sorties :
  - donnees/detections.csv — une ligne par paire (video, entite), avec les
    signaux trouves, les indices commerciaux, et l'extrait EXACT qui a
    declenche (critere 9) ;
  - recherche/detection_<date>.md — le rapport chiffre, signal par signal.

Le detecteur n'affirme rien : il compte des signaux. La mesure de sa valeur
est faite par `mesurer_detection.py` contre les verdicts de Vincent.
"""

import csv
import datetime as dt
import json
import re
import unicodedata
from collections import Counter
from pathlib import Path

import openpyxl

RACINE = Path(__file__).resolve().parent.parent
CHEMIN_DICO = RACINE / "DICTIONNAIRE.xlsx"
CHEMIN_CORPUS = RACINE / "acquis" / "donnees_brutes" / "moisson_videos.json"
CHEMIN_DETECTIONS = RACINE / "donnees" / "detections.csv"
CHEMIN_VITRINES = RACINE / "donnees" / "contenus_vitrines.csv"
DOSSIER_RECHERCHE = RACINE / "recherche"

# Une video publiee par le compte d'un lobby ou d'une marque n'est pas une
# collaboration d'un createur : c'est le lobby qui parle. Elle sort du flux
# de detection et part dans le flux DECOUVERTE (contenus_vitrines.csv), ou
# l'on cherchera des noms de createurs a proposer. Regle confirmee par les
# commentaires de Vincent (« c'est la chaine du lobby lui-meme »).
TYPES_CANAUX = {"chaine YouTube", "chaine YouTube regionale",
                "compte vitrine", "compte de marque"}

# Vocabulaire commercial : la presence d'un de ces motifs a cote d'un signal
# est l'indice que la mention est une collaboration, pas une conversation.
INDICATEURS = {
    "remerciement": r"merci\s+(a|au|aux)\b",
    "partenariat": r"\bpartenari|\bpartenaire",
    "sponsor": r"\bsponsoris",
    "collaboration": r"\bcollaboration\s+commerciale|\ben\s+collaboration\s+avec",
    "code_promo": r"\bcode\s+promo|\bcode\s+reduc",
    "communication_commerciale": r"\bcommunication\s+commerciale",
    "offert": r"\boffert(e|es|s)?\s+par\b",
}


def normaliser_positionnel(texte):
    """Version comparable du texte, de MEME LONGUEUR que l'original.

    Chaque caractere est remplace par sa base sans accent, en minuscule ;
    les caracteres invisibles deviennent des espaces. La longueur ne change
    pas, donc une position trouvee ici designe la meme position dans
    l'original — c'est ce qui permet d'extraire l'extrait exact.
    """
    sortie = []
    for c in texte:
        if unicodedata.category(c) == "Cf":
            sortie.append(" ")
            continue
        d = unicodedata.normalize("NFD", c)
        base = d[0] if d else c
        sortie.append(base.lower() if base.isascii() or base.isalpha() else base)
    return "".join(sortie)


def charger_signaux():
    """Rend (signaux actifs, signaux temoins) depuis le classeur maitre."""
    wb = openpyxl.load_workbook(CHEMIN_DICO, read_only=True, data_only=True)
    lignes = list(wb["Signaux"].iter_rows(values_only=True))
    wb.close()
    entetes = [str(c or "").strip() for c in lignes[0]]
    actifs, temoins = [], []
    for l in lignes[1:]:
        d = dict(zip(entetes, l))
        if not d.get("texte"):
            continue
        texte = str(d["texte"]).strip()
        norme = normaliser_positionnel(texte)
        if norme.startswith(("#", "@")) or "." in norme:
            # hashtag, compte ou site : la chaine exacte, non precedee d'un
            # caractere de mot, non suivie d'un caractere de mot.
            motif = r"(?<![\w#@])" + re.escape(norme) + r"(?!\w)"
        else:
            # texte libre : frontiere de mot des deux cotes.
            motif = r"(?<!\w)" + re.escape(norme) + r"(?!\w)"
        signal = {
            "texte": texte,
            "type_signal": str(d.get("type_signal") or "").strip(),
            "entite": str(d.get("entite") or "").strip(),
            "force": str(d.get("force") or "faible").strip(),
            "regex": re.compile(motif),
        }
        statut = str(d.get("statut") or "").strip()
        if statut == "confirme":
            actifs.append(signal)
        elif statut == "temoin":
            temoins.append(signal)
    return actifs, temoins


def detecter_dans(texte_original, signaux):
    """Rend {entite: [(signal, position)]} pour un texte."""
    norme = normaliser_positionnel(texte_original)
    trouves = {}
    for s in signaux:
        m = s["regex"].search(norme)
        if m:
            trouves.setdefault(s["entite"], []).append((s, m.start()))
    return trouves


def extraire(texte, position, longueur=240):
    debut = max(0, position - 80)
    extrait = texte[debut:debut + longueur].strip()
    prefixe = "…" if debut > 0 else ""
    suffixe = "…" if debut + longueur < len(texte) else ""
    return prefixe + extrait.replace("\n", " ⏎ ") + suffixe


def principal():
    signaux, temoins = charger_signaux()
    with open(CHEMIN_CORPUS, encoding="utf-8") as f:
        videos = json.load(f)["touchees"]

    # Table des canaux vitrines : nom normalise -> entite.
    canaux_vitrines = {}
    for s in signaux:
        if s["type_signal"] in TYPES_CANAUX:
            nom = normaliser_positionnel(s["texte"]).lstrip("@")
            canaux_vitrines[nom] = s["entite"]

    aujourd_hui = dt.date.today().isoformat()
    detections = []
    vitrines = []
    compte_signaux = Counter()
    compte_temoins = Counter()

    for v in videos:
        texte = f"{v.get('titre') or ''}\n{v.get('description') or ''}"
        nom_chaine = normaliser_positionnel(v.get("chaine") or "").lstrip("@")
        if nom_chaine in canaux_vitrines:
            vitrines.append({
                "video_id": v.get("video_id", ""),
                "chaine": v.get("chaine", ""),
                "entite_du_canal": canaux_vitrines[nom_chaine],
                "publiee": v.get("publiee", ""),
                "titre": v.get("titre", ""),
                "url": v.get("url", ""),
            })
            continue
        norme = normaliser_positionnel(texte)
        indices = sorted(nom for nom, motif in INDICATEURS.items()
                         if re.search(motif, norme))
        for entite, hits in detecter_dans(texte, signaux).items():
            noms = sorted({s["texte"] for s, _ in hits})
            types = sorted({s["type_signal"] for s, _ in hits if s["type_signal"]})
            force = ("fort" if any(s["force"] == "fort" for s, _ in hits)
                     else "faible")
            for s, _ in hits:
                compte_signaux[s["texte"]] += 1
            premiere = min(p for _, p in hits)
            detections.append({
                "video_id": v.get("video_id", ""),
                "chaine": v.get("chaine", ""),
                "abonnes": v.get("abonnes", ""),
                "publiee": v.get("publiee", ""),
                "titre": v.get("titre", ""),
                "url": v.get("url", ""),
                "entite": entite,
                "signaux": " | ".join(noms),
                "types_signaux": " | ".join(types),
                "force": force,
                "indices_commerciaux": " | ".join(indices),
                "extrait": extraire(texte, premiere),
            })
        for entite, hits in detecter_dans(texte, temoins).items():
            for s, _ in hits:
                compte_temoins[s["texte"]] += 1

    CHEMIN_DETECTIONS.parent.mkdir(exist_ok=True)
    with open(CHEMIN_DETECTIONS, "w", newline="", encoding="utf-8-sig") as f:
        champs = ["video_id", "chaine", "abonnes", "publiee", "titre", "url",
                  "entite", "signaux", "types_signaux", "force",
                  "indices_commerciaux", "extrait"]
        w = csv.DictWriter(f, fieldnames=champs)
        w.writeheader()
        w.writerows(detections)

    with open(CHEMIN_VITRINES, "w", newline="", encoding="utf-8-sig") as f:
        champs = ["video_id", "chaine", "entite_du_canal", "publiee", "titre",
                  "url"]
        w = csv.DictWriter(f, fieldnames=champs)
        w.writeheader()
        w.writerows(vitrines)

    par_entite = Counter(d["entite"] for d in detections)
    avec_indice = sum(1 for d in detections if d["indices_commerciaux"])

    DOSSIER_RECHERCHE.mkdir(exist_ok=True)
    chemin_rapport = DOSSIER_RECHERCHE / f"detection_{aujourd_hui}.md"
    with open(chemin_rapport, "w", encoding="utf-8") as f:
        f.write(f"# Detection sur le corpus gele — {aujourd_hui}\n\n")
        f.write("Produit par `outils/detecter.py`. Corpus : les "
                f"{len(videos)} videos candidates conservees dans "
                "`moisson_videos.json` (cle `touchees`). Dictionnaire : "
                f"{len(signaux)} signaux `confirme`, {len(temoins)} temoins.\n\n")
        f.write(f"**Paires (video, entite) detectees : {len(detections)}**\n")
        f.write(f"**dont avec au moins un indice commercial : {avec_indice}**\n")
        f.write(f"**Videos publiees par un canal vitrine, routees vers la "
                f"decouverte : {len(vitrines)}** "
                "(`donnees/contenus_vitrines.csv`)\n\n")
        f.write("## Par entite\n\n| Entite | Paires |\n|---|---:|\n")
        for entite, n in par_entite.most_common():
            f.write(f"| {entite} | {n} |\n")
        f.write("\n## Par signal (tous)\n\n| Signal | Videos touchees |\n|---|---:|\n")
        for signal, n in compte_signaux.most_common():
            f.write(f"| {signal} | {n} |\n")
        f.write("\n## Groupe temoin (cerealier, ne detecte pas)\n\n")
        if compte_temoins:
            for signal, n in compte_temoins.most_common():
                f.write(f"- {signal} : {n}\n")
        else:
            f.write("Aucune occurrence.\n")
        f.write(f"\nDetail ligne par ligne : `donnees/detections.csv`.\n")

    print(f"Videos lues : {len(videos)}")
    print(f"Paires (video, entite) : {len(detections)}")
    print(f"Ecrit : {CHEMIN_DETECTIONS}")
    print(f"Ecrit : {chemin_rapport}")


if __name__ == "__main__":
    principal()
