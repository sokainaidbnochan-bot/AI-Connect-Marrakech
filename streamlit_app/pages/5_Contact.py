import pandas as pd
import streamlit as st

from data_access import charger_entreprises
from candidature_db import (
    creer_table_candidatures,
    creer_candidature,
    obtenir_candidatures_utilisateur
)


# =========================================================
# CONFIGURATION
# =========================================================
st.set_page_config(
    page_title="Contact - AI Connect Marrakech",
    page_icon="",
    layout="wide"
)


# =========================================================
# PROTECTION
# =========================================================
if not st.session_state.get("authenticated", False):
    st.warning("Veuillez vous connecter depuis la page d'accueil.")
    st.page_link("Home.py", label="← Retour à l'accueil")
    st.stop()


user = st.session_state.user

creer_table_candidatures()


# =========================================================
# CSS
# =========================================================
st.markdown("""
<style>
    #MainMenu, footer, header {
        visibility: hidden;
    }

    .stApp {
        background-color: #f7f3e8;
    }

    .contact-box {
        background: white;
        border: 1px solid #e4ded2;
        border-radius: 12px;
        padding: 22px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, .08);
        margin-bottom: 22px;
    }
</style>
""", unsafe_allow_html=True)


# =========================================================
# DONNÉES ENTREPRISES
# =========================================================
try:
    df = charger_entreprises().copy()

except Exception as erreur:
    st.error(f"Impossible de charger les entreprises : {erreur}")
    st.stop()


# =========================================================
# PRÉPARATION DES ENTREPRISES
# =========================================================
# Adapter les noms selon les colonnes réelles de ton CSV.
nom_colonne = None

for colonne in ["nom", "name", "entreprise", "nom_entreprise"]:
    if colonne in df.columns:
        nom_colonne = colonne
        break


if nom_colonne is None:
    st.error(
        "Impossible de trouver la colonne contenant le nom des entreprises. "
        "Ajoute une colonne nom, name, entreprise ou nom_entreprise dans tes données."
    )
    st.stop()


# Créer une colonne id stable si ton CSV n'a pas id.
if "id" not in df.columns:
    df["id"] = range(1, len(df) + 1)


# =========================================================
# PAGE
# =========================================================
st.title(" Contact et candidatures")

st.write(
    "Sélectionnez une entreprise ayant une offre disponible, "
    "ajoutez votre CV au format PDF et enregistrez votre candidature."
)

st.caption(
    f"Connectée : {user['full_name']} — @{user['username']}"
)


# =========================================================
# FILTRE : ENTREPRISES AVEC OFFRE
# =========================================================
df_offres = df.copy()

# Si le fichier contient une colonne offre / job / poste, filtrer les entreprises.
colonne_offre = None

for colonne in ["offre", "offres", "poste", "job_title", "has_offer"]:
    if colonne in df_offres.columns:
        colonne_offre = colonne
        break


if colonne_offre is not None:
    df_offres = df_offres[
        df_offres[colonne_offre].notna()
        & (df_offres[colonne_offre].astype(str).str.strip() != "")
    ]


if df_offres.empty:
    st.warning(
        "Aucune entreprise avec une offre n'est actuellement disponible."
    )
    st.stop()


# Nom affiché dans la liste
df_offres["label_entreprise"] = df_offres.apply(
    lambda ligne: (
        f"{ligne[nom_colonne]}"
        + (
            f" — {ligne[colonne_offre]}"
            if colonne_offre is not None else ""
        )
    ),
    axis=1
)

entreprises_dict = dict(
    zip(
        df_offres["label_entreprise"],
        df_offres.index
    )
)


# =========================================================
# FORMULAIRE
# =========================================================
st.markdown('<div class="contact-box">', unsafe_allow_html=True)

with st.form("form_candidature", clear_on_submit=True):

    choix_entreprise = st.selectbox(
        "Entreprise et offre",
        options=list(entreprises_dict.keys())
    )

    index_choisi = entreprises_dict[choix_entreprise]
    entreprise = df_offres.loc[index_choisi]

    entreprise_nom = str(entreprise[nom_colonne])

    entreprise_id = int(entreprise["id"])

    # Récupération e-mail éventuel
    entreprise_email = None

    for colonne_email in ["email", "email_contact", "contact_email"]:
        if colonne_email in df_offres.columns:
            valeur_email = entreprise[colonne_email]

            if pd.notna(valeur_email):
                entreprise_email = str(valeur_email)

            break

    # Récupération poste éventuel
    if colonne_offre is not None:
        poste_defaut = str(entreprise[colonne_offre])
    else:
        poste_defaut = ""

    poste = st.text_input(
        "Poste / Offre",
        value=poste_defaut,
        placeholder="Exemple : Data Analyst Junior"
    )

    message = st.text_area(
        "Message pour l'entreprise",
        placeholder=(
            "Bonjour,\n\n"
            "Je souhaite vous proposer ma candidature pour le poste indiqué. "
            "Vous trouverez mon CV en pièce jointe.\n\n"
            "Cordialement."
        ),
        height=150
    )

    cv_pdf = st.file_uploader(
        "Ajouter votre CV (PDF uniquement)",
        type=["pdf"],
        help="Le fichier doit être au format PDF."
    )

    envoyer = st.form_submit_button(
        " Enregistrer ma candidature",
        type="primary",
        use_container_width=True
    )

st.markdown("</div>", unsafe_allow_html=True)


# =========================================================
# VALIDATION + SAUVEGARDE
# =========================================================
if envoyer:

    if not poste.strip():
        st.error("Veuillez renseigner le poste ou l'offre.")

    elif cv_pdf is None:
        st.error("Veuillez ajouter votre CV au format PDF.")

    else:
        # Limite choisie : 5 Mo
        taille_max = 5 * 1024 * 1024

        if cv_pdf.size > taille_max:
            st.error(
                "Le fichier PDF est trop grand. "
                "La taille maximale autorisée est de 5 Mo."
            )

        else:
            cv_data = cv_pdf.getvalue()

            succes, message_resultat = creer_candidature(
                user_id=user["id"],
                entreprise_id=entreprise_id,
                entreprise_nom=entreprise_nom,
                entreprise_email=entreprise_email,
                poste=poste.strip(),
                message=message.strip(),
                cv_filename=cv_pdf.name,
                cv_data=cv_data,
                cv_mimetype=cv_pdf.type or "application/pdf"
            )

            if succes:
                st.success(message_resultat)

                st.info(
                    "Votre candidature est actuellement enregistrée comme "
                    "« Brouillon ». Elle n'a pas encore été envoyée "
                    "automatiquement à l'entreprise."
                )

            else:
                st.error(message_resultat)


# =========================================================
# MES CANDIDATURES
# =========================================================
st.markdown("---")

st.subheader(" Mes candidatures enregistrées")

candidatures = obtenir_candidatures_utilisateur(user["id"])

if candidatures:
    df_candidatures = pd.DataFrame(candidatures)

    st.dataframe(
        df_candidatures,
        use_container_width=True,
        hide_index=True
    )

else:
    st.info("Vous n'avez encore enregistré aucune candidature.")