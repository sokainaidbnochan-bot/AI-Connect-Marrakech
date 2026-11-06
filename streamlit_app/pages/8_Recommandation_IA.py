import streamlit as st
import sys
from pathlib import Path

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

ROOT = Path(__file__).resolve().parents[2]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from auth_helpers import exiger_connexion

st.set_page_config(
    page_title="Recommandation IA",
    layout="wide",
)

exiger_connexion()

RAW = ROOT / "data" / "raw" / "offres_jooble.csv"
MANUEL = ROOT / "data" / "processed" / "offres_manuelles.csv"

st.title("Recommandation intelligente d’offres")
st.caption(
    "Entrez vos compétences ou votre domaine, et l’IA propose les offres "
    "les plus pertinentes parmi les opportunités collectées."
)


@st.cache_data
def charger_offres():
    cadres = []

    if RAW.exists():
        df = pd.read_csv(RAW, dtype=str).fillna("")
        df["origine"] = "Jooble"
        cadres.append(df)

    if MANUEL.exists():
        df = pd.read_csv(MANUEL, dtype=str).fillna("")
        df["origine"] = "Manuel"
        cadres.append(df)

    if not cadres:
        return pd.DataFrame()

    df = pd.concat(cadres, ignore_index=True)

    if "offre_id" in df.columns:
        df = df.drop_duplicates(subset="offre_id", keep="last")

    df["texte"] = (
        df.get("titre", "").astype(str) + " "
        + df.get("entreprise", "").astype(str) + " "
        + df.get("extrait", "").astype(str)
    )

    return df.reset_index(drop=True)


df = charger_offres()

if df.empty:
    st.warning(
        "Aucune offre disponible. Lancez d’abord `src/collect_offres.py`."
    )
    st.stop()

st.subheader("Votre profil")

competences = st.text_input(
    "Vos compétences",
    placeholder="Python, SQL, Machine Learning, développement web…",
)

domaine = st.selectbox(
    "Domaine souhaité",
    [
        "Développement web",
        "Data / analyse de données",
        "Intelligence artificielle",
        "Réseaux et cybersécurité",
        "Marketing digital",
        "Gestion de projet",
    ],
)

nombres = st.slider(
    "Nombre de recommandations",
    min_value=3,
    max_value=15,
    value=5,
)

if st.button(
    "Trouver les offres adaptées",
    type="primary",
):
    if not competences.strip():
        st.warning("Veuillez entrer au moins une compétence.")
        st.stop()

    profil = competences + " " + domaine

    vectoriseur = TfidfVectorizer(
        stop_words="english",
        max_features=5000,
    )

    try:
        vecteurs = vectoriseur.fit_transform(df["texte"])
        profil_vecteur = vectoriseur.transform([profil])

        similarites = cosine_similarity(
            profil_vecteur,
            vecteurs,
        ).flatten()

        df["score_ia"] = similarites
        resultats = df.sort_values(
            "score_ia",
            ascending=False,
        ).head(nombres)

    except Exception:
        st.error(
            "Impossible de générer les recommandations pour le moment."
        )
        st.stop()

    st.subheader("Offres recommandées")

    if resultats.empty:
        st.info("Aucune offre correspondante n’a été trouvée.")

    else:
        for _, offre in resultats.iterrows():

            score = round(float(offre["score_ia"]) * 100, 1)

            with st.container(border=True):
                st.markdown(f"### {offre['titre']}")

                st.write(
                    f"**Entreprise :** {offre['entreprise']}  ·  "
                    f"**Type :** {offre['type_offre']}  ·  "
                    f"**Lieu :** {offre['lieu'] or '—'}"
                )

                st.progress(
                    min(score / 100, 1.0),
                    text=f"Compatibilité estimée : {score}%",
                )

                if offre["extrait"]:
                    with st.expander("Voir la description"):
                        st.write(offre["extrait"])

                if offre["lien"].startswith("http"):
                    st.link_button(
                        "Ouvrir l’offre",
                        offre["lien"],
                    )