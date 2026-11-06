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
from data_access import charger_suivi, sauvegarder_suivi

st.set_page_config(page_title="Suivi", page_icon="", layout="wide")
st.title("Suivi des candidatures")
st.caption("Modifie le statut, la date de candidature ou la remarque directement dans le tableau, puis sauvegarde.")

df = charger_suivi()

df_modifie = st.data_editor(
    df,
    column_config={
        "statut": st.column_config.SelectboxColumn(
            "Statut",
            options=["À contacter", "Contacté", "Entretien", "Refusé", "Accepté"],
        ),
        "date_candidature": st.column_config.TextColumn("Date de candidature"),
        "remarque": st.column_config.TextColumn("Remarque"),
    },
    use_container_width=True,
    hide_index=True,
    key="editeur_suivi",
)

if st.button("Sauvegarder le suivi"):
    sauvegarder_suivi(df_modifie)
    st.success("Suivi sauvegardé.")

st.subheader("Répartition par statut")
st.bar_chart(df_modifie["statut"].value_counts())
