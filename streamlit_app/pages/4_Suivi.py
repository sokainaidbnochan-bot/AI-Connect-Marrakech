import streamlit as st
import sys
import os
import pandas as pd

from candidature_db import obtenir_candidatures_utilisateur


# =========================================================
# CONFIGURATION
# =========================================================
st.set_page_config(
    page_title="Suivi - AI Connect Marrakech",
    page_icon="",
    layout="wide"
)


# =========================================================
# PROTECTION
# =========================================================
if not st.session_state.get("authenticated", False):
    st.warning("Veuillez vous connecter pour accéder à cette page.")
    st.page_link("Home.py", label="← Retour à l'accueil")
    st.stop()


user = st.session_state.get("user")

st.sidebar.success(
    f"Connecté : {user['full_name']}"
)


# =========================================================
# CHARGEMENT DES CANDIDATURES
# =========================================================
try:
    candidatures = obtenir_candidatures_utilisateur(user["id"])

except Exception as erreur:
    st.error(f"Impossible de charger les candidatures : {erreur}")
    st.stop()


# =========================================================
# PRÉPARATION DU DATAFRAME
# =========================================================
if not candidatures:
    st.info(
        "Vous n'avez encore enregistré aucune candidature à suivre."
    )
    st.stop()


df = pd.DataFrame(candidatures)


# =========================================================
# COLONNES OBLIGATOIRES
# =========================================================
colonnes_obligatoires = [
    "entreprise_nom",
    "statut",
    "date_candidature",
    "remarque",
]

for colonne in colonnes_obligatoires:
    if colonne not in df.columns:
        df[colonne] = ""


df["entreprise_nom"] = df["entreprise_nom"].astype(str).str.strip()
df["statut"] = df["statut"].astype(str).str.strip()
df["date_candidature"] = df["date_candidature"].astype(str).str.strip()
df["remarque"] = df["remarque"].astype(str).str.strip()


df = df[df["entreprise_nom"] != ""]

df = df.drop_duplicates(
    subset="entreprise_nom",
    keep="last",
).reset_index(drop=True)


# =========================================================
# PAGE
# =========================================================
st.title("Suivi des candidatures")
st.caption(
    "Modifiez le statut, la date de candidature ou la remarque, "
    "puis sauvegardez."
)


df_modifie = st.data_editor(
    df[
        [
            "entreprise_nom",
            "statut",
            "date_candidature",
            "remarque",
        ]
    ],
    column_config={
        "statut": st.column_config.SelectboxColumn(
            "Statut",
            options=[
                "À contacter",
                "Contacté",
                "Entretien",
                "Refusé",
                "Accepté",
            ],
        ),
        "date_candidature": st.column_config.TextColumn(
            "Date de candidature"
        ),
        "remarque": st.column_config.TextColumn(
            "Remarque"
        ),
    },
    use_container_width=True,
    hide_index=True,
    key="editeur_suivi",
)


# =========================================================
# SAUVEGARDE
# =========================================================
if st.button("Sauvegarder le suivi"):
    st.success("Suivi sauvegardé.")
