"""
Collecte d'offres de stage / d'emploi via l'API REST de Jooble (gratuite, clé requise).

1) Crée ta clé : https://jooble.org/api/about  (inscription gratuite)
2) Dans le fichier .env (à la racine du projet), ajoute :
       JOOBLE_API_KEY=ta_cle_ici
   (optionnel) JOOBLE_BASE_URL=https://jooble.org/api   <- à changer seulement si Jooble
   te donne une adresse spécifique à un pays pour ta clé.
3) Depuis le dossier src/ :
       python collect_offres.py              # 1 page par requête
       python collect_offres.py --pages 2    # 2 pages par requête
       python collect_offres.py --tout       # garde aussi les offres hors Marrakech

Écrit : data/raw/offres_jooble.csv           (offres normalisées)
Cache : data/raw/offres_jooble_cache.json     (réponses brutes ; relancer le script ne
        redépense PAS de requêtes déjà faites, sauf avec --rafraichir)

Remarques :
 - L'API renvoie des extraits (snippets), pas les annonces complètes : le lien mène à l'annonce.
 - Certaines sources indiquent un nombre limité de requêtes par clé gratuite : le script
   utilise peu de requêtes et met tout en cache.
 - Le "type" (Stage / Alternance / Emploi) est déduit du TITRE de l'annonce uniquement.
"""
import argparse
import hashlib
import json
import os
import re
import time
from datetime import date

import pandas as pd
import requests
from dotenv import load_dotenv

DOSSIER = os.path.dirname(os.path.abspath(__file__))
RACINE = os.path.join(DOSSIER, "..")
load_dotenv(os.path.join(RACINE, ".env"))

CLE = os.getenv("JOOBLE_API_KEY", "").strip()
BASE_URL = os.getenv("JOOBLE_BASE_URL", "https://jooble.org/api").rstrip("/")
CACHE = os.path.join(RACINE, "data", "raw", "offres_jooble_cache.json")
SORTIE = os.path.join(RACINE, "data", "raw", "offres_jooble.csv")

REQUETES = [
    ("internship developer", "Marrakech"),
    ("software developer", "Marrakech"),
    ("stage informatique", "Marrakech"),
    ("artificial intelligence", "Marrakech"),
    ("web developer", "Marrakech"),
    ("data analyst", "Marrakech"),
]

RE_STAGE = re.compile(r"\b(stages?|stagiaires?|interns?|internships?|pfe|pfa)\b", re.I)
RE_ALTERNANCE = re.compile(r"\b(alternance|apprentissage|apprenti)\b", re.I)
RE_MARRAKECH = re.compile(r"marrakech|marrakesh", re.I)

COLONNES = [
    "offre_id", "titre", "entreprise", "lieu", "type_offre", "date_publication",
    "lien", "source", "extrait", "salaire", "ajoute_le", "origine",
]


def nettoyer(texte):
    texte = re.sub(r"<[^>]+>", " ", str(texte or ""))
    texte = texte.replace("&nbsp;", " ").replace("&amp;", "&")
    return re.sub(r"\s+", " ", texte).strip()


def type_offre(titre):
    if RE_STAGE.search(titre):
        return "Stage"
    if RE_ALTERNANCE.search(titre):
        return "Alternance"
    return "Emploi"


def normaliser(job):
    titre = nettoyer(job.get("title"))
    lien = str(job.get("link") or "").strip()
    brut_id = job.get("id")
    if brut_id:
        offre_id = f"jooble_{brut_id}"
    else:
        offre_id = "jooble_" + hashlib.md5((titre + lien).encode("utf-8")).hexdigest()[:12]
    return {
        "offre_id": offre_id,
        "titre": titre,
        "entreprise": nettoyer(job.get("company")),
        "lieu": nettoyer(job.get("location")),
        "type_offre": type_offre(titre),
        "date_publication": str(job.get("updated") or "")[:10],
        "lien": lien,
        "source": nettoyer(job.get("source")) or "Jooble",
        "extrait": nettoyer(job.get("snippet"))[:400],
        "salaire": nettoyer(job.get("salary")),
        "ajoute_le": date.today().isoformat(),
        "origine": "jooble",
    }


def charger_cache():
    if os.path.exists(CACHE):
        with open(CACHE, encoding="utf-8") as f:
            return json.load(f)
    return {}


def sauver_cache(cache):
    os.makedirs(os.path.dirname(CACHE), exist_ok=True)
    with open(CACHE, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False)


def interroger(mot, lieu, page, cache, rafraichir):
    """Retourne (réponse_json, requete_reelle_faite)."""
    cle_cache = f"{mot}|{lieu}|{page}"
    if cle_cache in cache and not rafraichir:
        return cache[cle_cache], False
    r = requests.post(
        f"{BASE_URL}/{CLE}",
        json={"keywords": mot, "location": lieu, "page": str(page)},
        timeout=20,
    )
    if r.status_code == 403:
        raise SystemExit(
            "Erreur 403 : clé Jooble invalide, ou non autorisée pour cette adresse "
            f"({BASE_URL}). Vérifie JOOBLE_API_KEY (et JOOBLE_BASE_URL) dans .env."
        )
    r.raise_for_status()
    data = r.json()
    cache[cle_cache] = data
    sauver_cache(cache)
    return data, True


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pages", type=int, default=1, help="Pages par requête (1 par défaut)")
    parser.add_argument("--tout", action="store_true", help="Garder aussi les offres hors Marrakech")
    parser.add_argument("--rafraichir", action="store_true", help="Ignorer le cache (consomme des requêtes)")
    args = parser.parse_args()

    if not CLE:
        raise SystemExit("JOOBLE_API_KEY manquante dans .env (voir l'en-tête du script).")

    cache = charger_cache()
    lignes, requetes_reelles = [], 0
    for mot, lieu in REQUETES:
        for page in range(1, args.pages + 1):
            data, reelle = interroger(mot, lieu, page, cache, args.rafraichir)
            jobs = data.get("jobs", []) or []
            requetes_reelles += int(reelle)
            print(f"{mot!r} / {lieu} / page {page} : {len(jobs)} offres" + ("" if reelle else "  (cache)"))
            lignes += [normaliser(j) for j in jobs]
            if reelle:
                time.sleep(1)
            if not jobs:
                break

    df = pd.DataFrame(lignes, columns=COLONNES).drop_duplicates(subset="offre_id")
    total = len(df)
    if not args.tout and total:
        garde = df["lieu"].apply(lambda l: (not l) or bool(RE_MARRAKECH.search(l)))
        df = df[garde]
    os.makedirs(os.path.dirname(SORTIE), exist_ok=True)
    df.to_csv(SORTIE, index=False)

    print(f"\nRequêtes réellement envoyées à l'API : {requetes_reelles}")
    print(f"Offres uniques : {total}  |  gardées (Marrakech) : {len(df)}")
    if len(df):
        print(df["type_offre"].value_counts().to_string())
    print("Sauvegardé dans data/raw/offres_jooble.csv")


if __name__ == "__main__":
    main()
