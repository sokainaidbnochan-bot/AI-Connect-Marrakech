import streamlit as st
import sys
import os
import pandas as pd

from data_access import charger_suivi, sauvegarder_suivi


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
# CHARGEMENT DU SUIVI
# =========================================================
try:
    df = charger_suivi().copy()

except Exception as erreur:
    st.error(f"Impossible de charger le suivi : {erreur}")
    st.stop()


# =========================================================
# PRÉPARATION DES COLONNES
# =========================================================
colonnes_obligatoires = [
    "entreprise",
    "statut",
    "date_candidature",
    "remarque",
]

for colonne in colonnes_obligatoires:
    if colonne not in df.columns:
        df[colonne] = ""


df["entreprise"] = df["entreprise"].astype(str).str.strip()

df = df[df["entreprise"] != ""]

df = df.drop_duplicates(
    subset="entreprise",
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


if df.empty:
    st.info(
        "Vous n'avez encore enregistré aucune candidature à suivre."
    )
    st.stop()


df_modifie = st.data_editor(
    df,
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


if st.button("Sauvegarder le suivi"):
    sauvegarder_suivi(df_modifie)
    st.success("Suivi sauvegardé.")


# =========================================================
# RÉPARTITION PAR STATUT
# =========================================================
st.subheader("Répartition par statut")

if not df_modifie.empty:
    st.bar_chart(df_modifie["statut"].value_counts())
