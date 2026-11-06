import streamlit as st
import sys
import os
import streamlit as st
from data_access import charger_entreprises

st.set_page_config(
    page_title="Entreprises - AI Connect Marrakech",
    layout="wide"
)


# Vérification : l'utilisateur est-il connecté ?
if not st.session_state.get("authenticated", False):
    st.warning("Veuillez vous connecter pour accéder à cette page.")
    st.page_link("Home.py", label="← Retour à l'accueil")
    st.stop()


st.set_page_config(page_title="Entreprises", page_icon="", layout="wide")
st.title("Entreprises")

df = charger_entreprises()

col1, col2, col3 = st.columns(3)
domaine = col1.selectbox("Domaine", ["Tous"] + sorted(df["categorie_recherchee"].dropna().unique().tolist()))
quartier = col2.selectbox("Quartier", ["Tous"] + sorted(df["quartier"].dropna().unique().tolist()))
recherche = col3.text_input("Rechercher par nom")

filtre = df.copy()
if domaine != "Tous":
    filtre = filtre[filtre["categorie_recherchee"] == domaine]
if quartier != "Tous":
    filtre = filtre[filtre["quartier"] == quartier]
if recherche:
    filtre = filtre[filtre["nom"].str.contains(recherche, case=False, na=False)]

st.write(f"{len(filtre)} entreprise(s) trouvée(s)")
st.dataframe(
    filtre[["nom", "categorie_recherchee", "quartier", "adresse", "telephone", "site_web", "note", "nombre_avis"]],
    use_container_width=True,
    hide_index=True,
)
