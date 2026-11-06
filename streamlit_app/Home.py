from pathlib import Path

import pandas as pd
import streamlit as st

from auth_db import (
    creer_table_users,
    valider_donnees_inscription,
    creer_utilisateur,
    authentifier_utilisateur,
)
from data_access import charger_entreprises


# =====================================================
# CONFIGURATION
# =====================================================
st.set_page_config(
    page_title="AI Connect Marrakech",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# =====================================================
# SESSION
# =====================================================
valeurs_initiales = {
    "authenticated": False,
    "user": None,
    "screen": "home",
    "auth_mode": "login",
}

for cle, valeur in valeurs_initiales.items():
    if cle not in st.session_state:
        st.session_state[cle] = valeur


# =====================================================
# CHEMINS DES PAGES
# =====================================================
DOSSIER_APP = Path(__file__).resolve().parent

PAGES = {
    "Dashboard": "pages/1_Tableau_de_bord.py",
    "Entreprises": "pages/2_Entreprises.py",
    "Carte": "pages/3_Carte.py",
    "Suivi des candidatures": "pages/4_Suivi.py",
    "Contact": "pages/5_Contact.py",
}


# =====================================================
# FONCTIONS
# =====================================================
def connecter_session(user):
    st.session_state.authenticated = True
    st.session_state.user = user
    st.session_state.screen = "home"
    st.session_state.auth_mode = "login"


def deconnecter():
    st.session_state.authenticated = False
    st.session_state.user = None
    st.session_state.screen = "home"
    st.session_state.auth_mode = "login"


def ouvrir_page(chemin):
    if not st.session_state.authenticated:
        st.session_state.screen = "auth"
        st.session_state.auth_mode = "login"
        st.rerun()

    if not (DOSSIER_APP / chemin).is_file():
        st.error(f"Page introuvable : {chemin}")
        return

    st.switch_page(chemin)


def afficher_statistiques(df):
    total = len(df)

    domaines = (
        df["categorie_recherchee"].nunique()
        if "categorie_recherchee" in df.columns
        else 0
    )

    quartiers = (
        df["quartier"].nunique()
        if "quartier" in df.columns
        else 0
    )

    gps = "Non disponible"

    if {"latitude", "longitude"}.issubset(df.columns):
        latitude = pd.to_numeric(
            df["latitude"],
            errors="coerce",
        )

        longitude = pd.to_numeric(
            df["longitude"],
            errors="coerce",
        )

        coordonnees_valides = (
            latitude.between(-90, 90)
            & longitude.between(-180, 180)
        )

        gps = (
            f"{coordonnees_valides.sum() / total:.0%}"
            if total
            else "0%"
        )

    statistiques = [
        (total, "Entreprises identifiées"),
        (domaines, "Domaines couverts"),
        (gps, "Géolocalisées (GPS)"),
        (quartiers, "Quartiers analysés"),
    ]

    for colonne, (valeur, libelle) in zip(
        st.columns(4),
        statistiques,
    ):
        with colonne:
            st.markdown(
                f"""
                <div class="stat-card">
                    <div class="stat-number">{valeur}</div>
                    <div class="stat-label">{libelle}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )


# =====================================================
# STYLE COMMUN
# =====================================================
st.markdown(
    """
    <style>
        .stApp {
            background: #f7f3e8;
        }

        .block-container {
            max-width: 1300px;
            padding-top: 5rem !important;
            padding-bottom: 3rem;
        }

        footer {
            visibility: hidden;
        }

        section[data-testid="stSidebar"] {
            background: #fcfaf4;
            border-right: 1px solid #e3dfd2;
        }

        .brand {
            color: #24211d;
            font-size: 21px;
            font-weight: 700;
            padding: 12px 0;
        }

        .brand i {
            color: #a68a68;
            font-family: Georgia, serif;
        }

        .brand span {
            color: #a68a68;
            font-size: 11px;
            font-weight: 400;
            margin-left: 6px;
        }

        .hero {
            box-sizing: border-box;
            min-height: 460px;
            padding: 80px 8%;
            margin: 15px 0 18px;
            background:
                linear-gradient(
                    90deg,
                    rgba(247,243,232,.98) 0%,
                    rgba(247,243,232,.92) 30%,
                    rgba(247,243,232,.25) 58%,
                    rgba(247,243,232,.05) 100%
                ),
                url("https://images.unsplash.com/photo-1516321318423-f06f85e504b3")
                center/cover;
        }

        .hero-content {
            max-width: 440px;
        }

        .hero h1 {
            color: #151515;
            font-family: Georgia, serif;
            font-size: 34px;
            line-height: 1.15;
            margin: 0 0 16px;
        }

        .hero h1 em {
            color: #294ca8;
            font-style: italic;
        }

        .hero p {
            color: #66625b;
            font-size: 13px;
            line-height: 1.7;
            margin-bottom: 22px;
        }

        .stat-card {
            background: white;
            border: 1px solid #e5dfd4;
            border-radius: 8px;

            
            padding: 12px 10px;

            text-align: center;
            box-shadow: 0 3px 8px rgba(0, 0, 0, 0.04);
        }

        .stat-number {
            font-family: Georgia, serif;
            font-size: 24px;
            line-height: 1.1;
            color: #181818;
            margin: 0;
        }

        .stat-label {
            color: #777168;
            font-size: 12px;
            line-height: 1.4;
            margin-top: 6px;
        }

        div[data-testid="stButton"] button {
            min-height: 44px;
            border-radius: 8px;
            font-weight: 600;
        }

        @media (max-width: 768px) {
            .hero {
                padding: 40px 7%;
            }

            .hero h1 {
                font-size: 28px;
            }
        }
    </style>
    """,
    unsafe_allow_html=True,
)


# =====================================================
# ÉCRAN CONNEXION / INSCRIPTION
# =====================================================
if (
    st.session_state.screen == "auth"
    and not st.session_state.authenticated
):
    st.markdown(
        """
        <style>
            section[data-testid="stSidebar"] {
                display: none;
            }

            [data-testid="stSidebarCollapsedControl"] {
                display: none;
            }

            .block-container {
                max-width: 1460px;
                padding-top: 4.5rem;
                padding-bottom: 4rem;
            }

            div[data-testid="stForm"] {
                background: white;
                border: 1px solid #ded8ca;
                border-radius: 18px;
                padding: 30px;
                box-shadow: 0 8px 24px rgba(60,48,28,.08);
            }

            .login-title {
                font-family: Georgia, serif;
                font-size: 25px;
                color: #24221d;
                text-align: center;
                margin-bottom: 22px;
            }

            div[data-testid="stTextInput"] input {
                background: #f6f2e9;
                color: #302e29;
            }

            div[data-testid="stFormSubmitButton"] button {
                background: #304fc1;
                color: white;
                border: 1px solid #304fc1;
                border-radius: 8px;
                min-height: 42px;
            }

            div[data-testid="stFormSubmitButton"] button:hover {
                background: #253fa0;
                border-color: #253fa0;
                color: white;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # La base est vérifiée uniquement sur l'écran
    # d'authentification pour ne pas bloquer l'accueil.
    base_disponible = True

    try:
        creer_table_users()
    except Exception:
        base_disponible = False

    gauche, carte, droite = st.columns([1, 1.4, 1])

    with carte:
        if not base_disponible:
            st.error(
                "Connexion MySQL impossible. Vérifiez le serveur "
                "et le fichier .streamlit/secrets.toml."
            )

        elif st.session_state.auth_mode == "login":

            # -----------------------------------------
            # CONNEXION
            # -----------------------------------------
            with st.form("form_login"):
                st.markdown(
                    '<div class="login-title">AI Connect Marrakech</div>',
                    unsafe_allow_html=True,
                )

                login = st.text_input(
                    "Nom d'utilisateur ou e-mail",
                    placeholder="Votre identifiant",
                    key="login_identifiant",
                )

                password_login = st.text_input(
                    "Mot de passe",
                    type="password",
                    key="login_password",
                )

                entrer = st.form_submit_button(
                    "Entrer",
                    use_container_width=True,
                )

            if entrer:
                if not login.strip() or not password_login:
                    st.error("Veuillez remplir les deux champs.")
                else:
                    try:
                        user, erreur = authentifier_utilisateur(
                            login.strip(),
                            password_login,
                        )
                    except Exception:
                        user = None
                        erreur = (
                            "Connexion impossible pour le moment. "
                            "Veuillez réessayer."
                        )

                    if erreur or user is None:
                        st.error(
                            erreur or "Identifiants incorrects."
                        )
                    else:
                        connecter_session(user)
                        st.rerun()

            if st.button(
                "Créer un compte",
                key="ouvrir_inscription",
                use_container_width=True,
            ):
                st.session_state.auth_mode = "register"
                st.rerun()

        else:

            # -----------------------------------------
            # INSCRIPTION
            # -----------------------------------------
            with st.form("form_register"):
                st.markdown(
                    '<div class="login-title">Créer un compte</div>',
                    unsafe_allow_html=True,
                )

                full_name = st.text_input(
                    "Nom complet",
                    key="register_full_name",
                )

                username = st.text_input(
                    "Nom d'utilisateur",
                    key="register_username",
                )

                email = st.text_input(
                    "Adresse e-mail",
                    key="register_email",
                )

                password_register = st.text_input(
                    "Mot de passe",
                    type="password",
                    key="register_password",
                )

                confirmation = st.text_input(
                    "Confirmer le mot de passe",
                    type="password",
                    key="register_confirmation",
                )

                creer = st.form_submit_button(
                    "Créer mon compte",
                    use_container_width=True,
                )

            if creer:
                # bcrypt utilise une limite en octets,
                # pas un simple nombre de caractères.
                if len(password_register.encode("utf-8")) > 72:
                    st.error(
                        "Le mot de passe ne doit pas dépasser "
                        "72 octets en UTF-8."
                    )

                else:
                    erreurs = valider_donnees_inscription(
                        full_name,
                        username,
                        email,
                        password_register,
                        confirmation,
                    )

                    if erreurs:
                        for erreur in erreurs:
                            st.error(erreur)

                    else:
                        try:
                            succes, message = creer_utilisateur(
                                full_name,
                                username,
                                email,
                                password_register,
                            )
                        except Exception:
                            succes = False
                            message = (
                                "Création du compte impossible "
                                "pour le moment."
                            )

                        if not succes:
                            st.error(message)

                        else:
                            try:
                                user, erreur = authentifier_utilisateur(
                                    username,
                                    password_register,
                                )
                            except Exception:
                                user = None
                                erreur = "Connexion automatique impossible."

                            if erreur or user is None:
                                st.success(
                                    "Compte créé. Utilisez maintenant "
                                    "le bouton « Se connecter »."
                                )
                            else:
                                connecter_session(user)
                                st.rerun()

            if st.button(
                "Déjà un compte ? Se connecter",
                key="retour_login",
                use_container_width=True,
            ):
                st.session_state.auth_mode = "login"
                st.rerun()

        # Disponible sur les deux formulaires,
        # même si MySQL est temporairement indisponible.
        if st.button(
            "← Retour à l'accueil",
            key="retour_accueil_auth",
            use_container_width=True,
        ):
            st.session_state.screen = "home"
            st.rerun()

    # Ne pas afficher l'accueil sous la carte.
    st.stop()


# =====================================================
# SIDEBAR : APRÈS CONNEXION
# =====================================================
if st.session_state.authenticated:
    with st.sidebar:
        st.markdown("## AI Connect Marrakech")

        st.page_link(
            "Home.py",
            label="Accueil",
        )

        for libelle, chemin in PAGES.items():
            if (DOSSIER_APP / chemin).is_file():
                st.page_link(
                    chemin,
                    label=libelle,
                )

        st.divider()

        if st.button(
            "Se déconnecter",
            key="logout_sidebar",
            use_container_width=True,
        ):
            deconnecter()
            st.rerun()


# =====================================================
# NAVBAR DE L'ACCUEIL
# =====================================================
col_logo, col_bouton = st.columns([4, 1.3])

with col_logo:
    st.markdown(
        """
        <div class="brand">
            <i>AC</i> AI Connect <span>Marrakech</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col_bouton:
    if not st.session_state.authenticated:
        if st.button(
            "Connexion",
            key="ouvrir_auth",
            use_container_width=True,
        ):
            st.session_state.screen = "auth"

            # Le bouton ouvre d'abord l'inscription,
            # avec la possibilité de passer à la connexion.
            st.session_state.auth_mode = "register"
            st.rerun()

    else:
        if st.button(
            "Déconnexion",
            key="deconnexion_accueil",
            use_container_width=True,
        ):
            deconnecter()
            st.rerun()


# =====================================================
# HERO ORIGINAL
# =====================================================
st.markdown(
    """
    <section class="hero">
        <div class="hero-content">
            <h1>
                Trouver et suivre les
                <em>opportunités tech</em>
                à Marrakech
            </h1>
            <p>
                Entreprises spécialisées en IA, développement
            </p>
        </div>
    </section>
    """,
    unsafe_allow_html=True,
)


# =====================================================
# BOUTONS DE NAVIGATION
# =====================================================
col1, col2, col3, espace = st.columns(
    [1.1, 1.1, 1.1, 3.7]
)

with col1:
    if st.button(
        "Entreprises",
        type="primary",
        key="accueil_entreprises",
        use_container_width=True,
    ):
        ouvrir_page(PAGES["Entreprises"])

with col2:
    if st.button(
        "Carte",
        key="accueil_carte",
        use_container_width=True,
    ):
        ouvrir_page(PAGES["Carte"])

with col3:
    if st.button(
        "Suivi",
        key="accueil_suivi",
        use_container_width=True,
    ):
        ouvrir_page(PAGES["Suivi des candidatures"])


# =====================================================
# STATISTIQUES
# =====================================================
 

try:
    df = charger_entreprises()
except Exception:
    st.warning(
        "Les statistiques sont temporairement indisponibles."
    )
else:
    afficher_statistiques(df)