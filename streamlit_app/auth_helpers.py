import streamlit as st


def exiger_connexion():
    if not st.session_state.get("authenticated"):
        st.warning("Veuillez vous connecter pour accéder à cette page.")
        st.stop()