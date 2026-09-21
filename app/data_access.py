"""
Accès aux données des entreprises.
Lit désormais data/processed/entreprises_final.csv (données réelles,
collectées via Google Places + OpenStreetMap, nettoyées et imputées).
"""
import os
import pandas as pd

CSV_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "processed", "entreprises_final.csv")

MAPPING_CATEGORIES = {
    "ia":               ("ia", "Intelligence artificielle"),
    "web":               ("web", "Développement web"),
    "data":              ("data", "Data / Analytics"),
    "mobile":            ("mobile", "Développement mobile"),
    "it":                ("it", "IT support"),
    "coworking":         ("web", "Coworking / Tech"),
    "software":          ("web", "Développement web"),
    "non_categorise":    ("it", "Autre / Non catégorisé"),
}


def _charger_dataframe():
    df = pd.read_csv(CSV_PATH)
    return df


def _ligne_vers_dict(row):
    code_cat, label_cat = MAPPING_CATEGORIES.get(
        row["categorie_recherchee"], ("it", "Autre / Non catégorisé")
    )
    return {
        "nom": row["nom"],
        "cat": code_cat,
        "cat_label": label_cat,
        "quartier": row["quartier"],
        "adresse": row["adresse"] if pd.notna(row["adresse"]) else "Adresse non renseignée",
        "tel": row["telephone"],
        "site": row["site_web"],
        "note": round(float(row["note"]), 1) if pd.notna(row["note"]) else 0.0,
        "avis": int(row["nombre_avis"]) if pd.notna(row["nombre_avis"]) else 0,
        "lat": row["latitude"],
        "lng": row["longitude"],
    }


def get_entreprises():
    df = _charger_dataframe()
    return [_ligne_vers_dict(row) for _, row in df.iterrows()]


def get_repartition_categorie():
    df = _charger_dataframe()
    labels = df["categorie_recherchee"].map(
        lambda c: MAPPING_CATEGORIES.get(c, ("it", "Autre / Non catégorisé"))[1]
    )
    return labels.value_counts().to_dict()


def get_repartition_quartier():
    df = _charger_dataframe()
    return df["quartier"].value_counts().to_dict()