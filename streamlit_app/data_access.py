"""
Accès aux données pour l'application Streamlit.
Réutilise les fichiers déjà produits par src/cleaning.py et
src/imputation.py — aucune donnée n'est recalculée ici.
"""
import os
import pandas as pd

DOSSIER_COURANT = os.path.dirname(__file__)
CSV_PATH = os.path.join(DOSSIER_COURANT, "..", "data", "processed", "entreprises_final.csv")
SUIVI_PATH = os.path.join(DOSSIER_COURANT, "..", "data", "processed", "suivi.csv")


def charger_entreprises():
    """Charge le dataset final des entreprises (83 lignes, nettoyé + imputé)."""
    return pd.read_csv(CSV_PATH)


def charger_suivi():
    """Charge le fichier de suivi des candidatures.
    S'il n'existe pas encore, le crée à partir de la liste des entreprises,
    avec un statut par défaut pour chacune."""
    if os.path.exists(SUIVI_PATH):
        return pd.read_csv(SUIVI_PATH)

    else:
        df = charger_entreprises()[["nom", "quartier", "categorie_recherchee"]].copy()
        df["statut"] = "À contacter"
        df["date_candidature"] = ""
        df["remarque"] = ""

    # Forcer ces colonnes en texte pour éviter les conflits de type avec st.data_editor
    df["date_candidature"] = df["date_candidature"].fillna("").astype(str)
    df["remarque"] = df["remarque"].fillna("").astype(str)
    return df

def charger_suivi():
    if os.path.exists(SUIVI_PATH):
        df = pd.read_csv(SUIVI_PATH)
    else:
        df = charger_entreprises()[["nom", "quartier", "categorie_recherchee"]].copy()
        df["statut"] = "À contacter"
        df["date_candidature"] = ""
        df["remarque"] = ""

    # Forcer ces colonnes en texte pour éviter les conflits de type avec st.data_editor
    df["date_candidature"] = df["date_candidature"].fillna("").astype(str)
    df["remarque"] = df["remarque"].fillna("").astype(str)
    return df


def sauvegarder_suivi(df):
    """Sauvegarde l'état du suivi (persistant entre les sessions)."""
    df.to_csv(SUIVI_PATH, index=False)
