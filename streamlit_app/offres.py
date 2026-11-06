"""
Gestion des offres de stage / d'emploi.

Sources combinées au chargement :
  - data/raw/offres_jooble.csv              (collecte automatique : src/collect_offres.py)
  - data/processed/offres_manuelles.csv     (offres ajoutées à la main ou importées en CSV)
Les offres manuelles ne sont jamais écrasées par une nouvelle collecte.
"""
import datetime
import hashlib
import os
import re
import unicodedata

import pandas as pd

from data_access import charger_entreprises, charger_suivi, sauvegarder_suivi

DOSSIER_COURANT = os.path.dirname(__file__)
JOOBLE_CSV = os.path.join(DOSSIER_COURANT, "..", "data", "raw", "offres_jooble.csv")
MANUEL_CSV = os.path.join(DOSSIER_COURANT, "..", "data", "processed", "offres_manuelles.csv")

COLONNES = [
    "offre_id", "titre", "entreprise", "lieu", "type_offre", "date_publication",
    "lien", "source", "extrait", "salaire", "ajoute_le", "origine",
]
TYPES = ["Stage", "Emploi"]
COLONNES_IMPORT = ["titre", "entreprise", "type_offre", "lieu", "date_publication", "lien", "source", "extrait"]

RE_STAGE = re.compile(r"\b(stages?|stagiaires?|interns?|internships?|pfe|pfa)\b", re.I)
RE_ALTERNANCE = re.compile(r"\b(alternance|apprentissage|apprenti)\b", re.I)
MOTS_VIDES = re.compile(r"\b(sarl|sas|sa|ste|societe|maroc|morocco|marrakech|agence|group|groupe)\b")


def _normaliser_nom(s):
    s = unicodedata.normalize("NFKD", str(s)).encode("ascii", "ignore").decode().lower()
    s = re.sub(r"[^a-z0-9 ]+", " ", s)
    simple = re.sub(r"\s+", " ", s).strip()
    sans_mots_vides = re.sub(r"\s+", " ", MOTS_VIDES.sub(" ", simple)).strip()
    return sans_mots_vides or simple


def rapprocher(nom_societe, index):
    """Retourne le nom exact d'une entreprise connue qui correspond à `nom_societe`, sinon ''."""
    n = _normaliser_nom(nom_societe)
    if len(n) < 3:
        return ""
    if n in index:
        return index[n]
    for cle, vrai_nom in index.items():
        if min(len(n), len(cle)) >= 5 and (cle in n or n in cle):
            return vrai_nom
    return ""


def deviner_type(titre):
    if RE_STAGE.search(titre or ""):
        return "Stage"
    if RE_ALTERNANCE.search(titre or ""):
        return "Alternance"
    return "Emploi"


def charger_offres():
    """Toutes les offres + colonne entreprise_connue (nom exact dans ta base, ou '')."""
    morceaux = []
    for chemin in (JOOBLE_CSV, MANUEL_CSV):
        if os.path.exists(chemin):
            morceaux.append(pd.read_csv(chemin, dtype=str).fillna(""))
    df = pd.concat(morceaux, ignore_index=True) if morceaux else pd.DataFrame(columns=COLONNES)
    for c in COLONNES:
        if c not in df.columns:
            df[c] = ""
    df = df[COLONNES].drop_duplicates(subset="offre_id", keep="last")

    index = {_normaliser_nom(n): n for n in charger_entreprises()["nom"].dropna().unique()}
    df["entreprise_connue"] = df["entreprise"].apply(lambda n: rapprocher(n, index))
    return df.reset_index(drop=True)


def _sauver_manuel(nouvelles):
    existantes = pd.read_csv(MANUEL_CSV, dtype=str).fillna("") if os.path.exists(MANUEL_CSV) else pd.DataFrame(columns=COLONNES)
    tout = pd.concat([existantes, nouvelles], ignore_index=True)
    avant = len(existantes)
    tout = tout.drop_duplicates(subset="offre_id", keep="first")
    os.makedirs(os.path.dirname(MANUEL_CSV), exist_ok=True)
    tout[COLONNES].to_csv(MANUEL_CSV, index=False)
    return len(tout) - avant


def _id_manuel(titre, entreprise, lien):
    return "manuel_" + hashlib.md5(f"{titre}|{entreprise}|{lien}".lower().encode("utf-8")).hexdigest()[:10]


def ajouter_offre_manuelle(titre, entreprise, type_offre, lieu="", date_publication="", lien="", source="", extrait="", origine="manuel"):
    """Retourne (ok, message)."""
    titre, entreprise = titre.strip(), entreprise.strip()
    if not titre or not entreprise:
        return False, "Le titre et l'entreprise sont obligatoires."
    ligne = {
        "offre_id": _id_manuel(titre, entreprise, lien.strip()),
        "titre": titre, "entreprise": entreprise, "lieu": lieu.strip(),
        "type_offre": type_offre if type_offre in TYPES else deviner_type(titre),
        "date_publication": str(date_publication or ""), "lien": lien.strip(),
        "source": source.strip(), "extrait": extrait.strip(), "salaire": "",
        "ajoute_le": datetime.date.today().isoformat(), "origine": origine,
    }
    ajoutees = _sauver_manuel(pd.DataFrame([ligne], columns=COLONNES))
    return (True, "Offre ajoutée.") if ajoutees else (False, "Cette offre existe déjà.")


def importer_csv(fichier):
    """Importe un CSV (colonnes obligatoires : titre, entreprise). Retourne (nb_ajoutees, nb_ignorees, message)."""
    try:
        df = pd.read_csv(fichier, dtype=str, encoding="utf-8-sig").fillna("")
    except Exception as e:
        return 0, 0, f"Impossible de lire le fichier : {e}"
    df.columns = [c.strip().lower() for c in df.columns]
    if "titre" not in df.columns or "entreprise" not in df.columns:
        return 0, 0, "Colonnes obligatoires manquantes : titre, entreprise."

    lignes, ignorees = [], 0
    for _, r in df.iterrows():
        titre, entreprise = r.get("titre", "").strip(), r.get("entreprise", "").strip()
        if not titre or not entreprise:
            ignorees += 1
            continue
        lien = r.get("lien", "").strip()
        type_o = r.get("type_offre", "").strip().capitalize()
        lignes.append({
            "offre_id": _id_manuel(titre, entreprise, lien),
            "titre": titre, "entreprise": entreprise, "lieu": r.get("lieu", "").strip(),
            "type_offre": type_o if type_o in TYPES else deviner_type(titre),
            "date_publication": r.get("date_publication", "").strip(), "lien": lien,
            "source": r.get("source", "").strip(), "extrait": r.get("extrait", "").strip(),
            "salaire": "", "ajoute_le": datetime.date.today().isoformat(), "origine": "csv",
        })
    if not lignes:
        return 0, ignorees, "Aucune ligne valide dans le fichier."
    ajoutees = _sauver_manuel(pd.DataFrame(lignes, columns=COLONNES))
    return ajoutees, ignorees + (len(lignes) - ajoutees), "Import terminé."


def modele_csv():
    """Contenu d'un CSV modèle à télécharger."""
    exemple = pd.DataFrame([{
        "titre": "Stage développeur web (PFE)", "entreprise": "Nom de l'entreprise",
        "type_offre": "Stage", "lieu": "Marrakech", "date_publication": "2026-10-20",
        "lien": "https://exemple.ma/offre", "source": "LinkedIn", "extrait": "Courte description...",
    }], columns=COLONNES_IMPORT)
    return exemple.to_csv(index=False).encode("utf-8-sig")


def ajouter_au_suivi(titre, entreprise):
    """Crée/complète une ligne de suivi pour (entreprise, opportunité). Retourne True si ajouté."""
    df = charger_suivi()
    if "opportunite" not in df.columns:
        df["opportunite"] = ""
    df["opportunite"] = df["opportunite"].fillna("").astype(str)

    if ((df["nom"] == entreprise) & (df["opportunite"] == titre)).any():
        return False

    # Si l'entreprise a déjà une ligne sans opportunité, on la complète au lieu de dupliquer
    libres = df.index[(df["nom"] == entreprise) & (df["opportunite"] == "")]
    if len(libres):
        df.loc[libres[0], "opportunite"] = titre
    else:
        ligne = {c: "" for c in df.columns}
        ligne.update({"nom": entreprise, "opportunite": titre, "statut": "À contacter"})
        connue = charger_entreprises()
        connue = connue[connue["nom"] == entreprise]
        if len(connue):
            if "quartier" in ligne:
                ligne["quartier"] = connue.iloc[0]["quartier"]
            if "categorie_recherchee" in ligne:
                ligne["categorie_recherchee"] = connue.iloc[0]["categorie_recherchee"]
        df = pd.concat([df, pd.DataFrame([ligne])], ignore_index=True)
    sauvegarder_suivi(df)
    return True
