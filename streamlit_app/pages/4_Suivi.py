import streamlit as st
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
# VÉRIFICATION
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
    "poste",
    "statut",
    "created_at",
]

for colonne in colonnes_obligatoires:
    if colonne not in df.columns:
        df[colonne] = ""


df["entreprise_nom"] = df["entreprise_nom"].astype(str).str.strip()
df["poste"] = df["poste"].astype(str).str.strip()
df["statut"] = df["statut"].astype(str).str.strip()
df["created_at"] = df["created_at"].astype(str).str.strip()

df = df[df["entreprise_nom"] != ""]

df = df.drop_duplicates(
    subset="entreprise_nom",
    keep="first",
).reset_index(drop=True)


# =========================================================
# PAGE
# =========================================================
st.title("Suivi des candidatures")
st.caption(
    "Modifiez le statut de vos candidatures enregistrées."
)


df_modifie = st.data_editor(
    df[
        [
            "entreprise_nom",
            "poste",
            "statut",
            "created_at",
        ]
    ],
    column_config={
        "entreprise_nom": st.column_config.TextColumn(
            "Entreprise"
        ),
        "poste": st.column_config.TextColumn(
            "Poste"
        ),
        "statut": st.column_config.SelectboxColumn(
            "Statut",
            options=[
                "Brouillon",
                "Envoyée",
                "En attente",
                "Entretien",
                "Acceptée",
                "Refusée",
            ],
        ),
        "created_at": st.column_config.TextColumn(
            "Date de candidature"
        ),
    },
    use_container_width=True,
    hide_index=True,
    key="editeur_suivi",
)


# =========================================================
# RÉPARTITION PAR STATUT
# =========================================================
st.subheader("Répartition par statut")

if not df_modifie.empty:
    st.bar_chart(df_modifie["statut"].value_counts())
