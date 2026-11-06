import streamlit as st
import sys
import os

import streamlit as st


st.set_page_config(
    page_title="Entreprises - AI Connect Marrakech",
    page_icon="",
    layout="wide"
)


# Vérification : l'utilisateur est-il connecté ?
if not st.session_state.get("authenticated", False):
    st.warning("Veuillez vous connecter pour accéder à cette page.")
    st.page_link("Home.py", label="← Retour à l'accueil")
    st.stop()


# Informations de l'utilisateur connecté
user = st.session_state.get("user")

st.sidebar.success(
    f"Connecté : {user['full_name']}"
)

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from data_access import charger_entreprises

st.set_page_config(page_title="Carte", page_icon="", layout="wide")
st.title("Carte")
st.caption("Répartition géographique réelle des entreprises identifiées à Marrakech.")

df = charger_entreprises()
carte_df = df.rename(columns={"latitude": "lat", "longitude": "lon"})[["lat", "lon"]].dropna()

st.map(carte_df, zoom=12)
st.caption(f"{len(carte_df)} entreprises géolocalisées affichées sur {len(df)} au total.")
