import pandas as pd
import streamlit as st
import urllib.parse
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

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

    .whatsapp-button {
        background-color: #25D366;
        color: white;
        padding: 12px 20px;
        border: none;
        border-radius: 8px;
        font-weight: bold;
        cursor: pointer;
        text-decoration: none;
        display: inline-block;
    }
</style>
""", unsafe_allow_html=True)


# =========================================================
# FONCTION ENVOI EMAIL
# =========================================================
def envoyer_candidature_email(
    email_entreprise,
    sujet,
    message,
    cv_filename,
    cv_data,
):
    try:
        smtp_email = st.secrets["smtp"]["email"]
        smtp_password = st.secrets["smtp"]["password"]

        msg = MIMEMultipart()
        msg["From"] = smtp_email
        msg["To"] = email_entreprise
        msg["Subject"] = sujet

        msg.attach(MIMEText(message, "plain", "utf-8"))

        cv_attachment = MIMEApplication(cv_data, _subtype="pdf")
        cv_attachment.add_header(
            "Content-Disposition",
            "attachment",
            filename=cv_filename
        )

        msg.attach(cv_attachment)

        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(smtp_email, smtp_password)
            server.send_message(msg)

        return True, "Email envoyé avec succès à l'entreprise."

    except Exception as erreur:
        return False, f"Erreur lors de l'envoi de l'email : {erreur}"


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


if "id" not in df.columns:
    df["id"] = range(1, len(df) + 1)


# =========================================================
# PAGE
# =========================================================
st.title("Contact et candidatures")

st.write(
    "Sélectionnez une entreprise ayant une offre disponible, "
    "ajoutez votre CV au format PDF et envoyez votre candidature."
)

st.caption(
    f"Connectée : {user['full_name']} — @{user['username']}"
)


# =========================================================
# FILTRE : ENTREPRISES AVEC OFFRE
# =========================================================
df_offres = df.copy()

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

    entreprise_email = None

    for colonne_email in ["email", "email_contact", "contact_email"]:
        if colonne_email in df_offres.columns:
            valeur_email = entreprise[colonne_email]

            if pd.notna(valeur_email) and str(valeur_email).strip() != "":
                entreprise_email = str(valeur_email).strip()

            break

    entreprise_telephone = None

    for colonne_tel in [
        "telephone",
        "tel",
        "phone",
        "numero_telephone",
        "contact_phone",
    ]:
        if colonne_tel in df_offres.columns:
            valeur_tel = entreprise[colonne_tel]

            if pd.notna(valeur_tel) and str(valeur_tel).strip() != "":
                entreprise_telephone = str(valeur_tel).strip()

            break

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
        "Envoyer ma candidature",
        type="primary",
        use_container_width=True
    )


st.markdown("</div>", unsafe_allow_html=True)


# =========================================================
# VALIDATION + SAUVEGARDE + EMAIL / WHATSAPP
# =========================================================
if envoyer:

    if not poste.strip():
        st.error("Veuillez renseigner le poste ou l'offre.")

    elif cv_pdf is None:
        st.error("Veuillez ajouter votre CV au format PDF.")

    else:
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
                st.success("Candidature enregistrée avec succès.")

                if entreprise_email:
                    sujet_email = (
                        f"Candidature - {poste.strip()} - {entreprise_nom}"
                    )

                    message_email = f"""
Bonjour,

Je souhaite vous proposer ma candidature pour le poste suivant :

Poste : {poste.strip()}

Message :

{message.strip()}

Cordialement,
{user['full_name']}
Email : {user.get('email', '')}
"""

                    email_envoye, message_email_resultat = envoyer_candidature_email(
                        email_entreprise=entreprise_email,
                        sujet=sujet_email,
                        message=message_email,
                        cv_filename=cv_pdf.name,
                        cv_data=cv_data,
                    )

                    if email_envoye:
                        st.success(message_email_resultat)
                        st.info(
                            f"Votre candidature a été envoyée à : {entreprise_email}"
                        )

                    else:
                        st.error(message_email_resultat)
                        st.warning(
                            "La candidature a été enregistrée, "
                            "mais l'email n'a pas pu être envoyé."
                        )

                elif entreprise_telephone:
                    telephone_propre = "".join(
                        chiffre for chiffre in entreprise_telephone if chiffre.isdigit()
                    )

                    if not telephone_propre.startswith("212"):
                        telephone_propre = "212" + telephone_propre.lstrip("0")

                    message_whatsapp = (
                        f"Bonjour {entreprise_nom},\n\n"
                        f"Je souhaite postuler au poste : {poste.strip()}.\n\n"
                        f"{message.strip()}\n\n"
                        f"Cordialement,\n"
                        f"{user['full_name']}"
                    )

                    lien_whatsapp = (
                        "https://wa.me/"
                        + telephone_propre
                        + "?text="
                        + urllib.parse.quote(message_whatsapp)
                    )

                    st.markdown(
                        f"""
                        <a href="{lien_whatsapp}" target="_blank">
                            <button class="whatsapp-button">
                                Envoyer ma candidature via WhatsApp
                            </button>
                        </a>
                        """,
                        unsafe_allow_html=True,
                    )

                    st.info(
                        "Cliquez sur le bouton WhatsApp pour envoyer votre candidature."
                    )

                else:
                    st.warning(
                        "Cette entreprise n'a ni email ni numéro WhatsApp enregistré."
                    )

            else:
                st.error(message_resultat)


# =========================================================
# MES CANDIDATURES
# =========================================================
st.markdown("---")

st.subheader("Mes candidatures enregistrées")

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
