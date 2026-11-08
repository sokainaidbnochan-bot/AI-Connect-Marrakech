import streamlit as st
import sys
from pathlib import Path
import numpy as np
import pandas as pd
import plotly.express as px


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


from auth_helpers import exiger_connexion


st.set_page_config(
    page_title="Analyse des offres",
    layout="wide",
)


exiger_connexion()


RAW = ROOT / "data" / "raw" / "offres_jooble.csv"
MANUEL = ROOT / "data" / "processed" / "offres_manuelles.csv"


st.title("Analyse des opportunités")
st.caption(
    "Analyse basée sur les offres collectées automatiquement via Jooble "
    "et les offres ajoutées manuellement."
)


@st.cache_data
def charger_donnees():
    cadres = []

    if RAW.exists():
        df_jooble = pd.read_csv(RAW, dtype=str).fillna("")
        df_jooble["origine"] = "Jooble"
        cadres.append(df_jooble)

    if MANUEL.exists():
        df_manuel = pd.read_csv(MANUEL, dtype=str).fillna("")
        df_manuel["origine"] = "Manuel"
        cadres.append(df_manuel)

    if not cadres:
        return pd.DataFrame()

    df = pd.concat(cadres, ignore_index=True)

    if "offre_id" in df.columns:
        df = df.drop_duplicates(subset="offre_id", keep="last")

    if "date_publication" in df.columns:
        df["date_publication"] = pd.to_datetime(
            df["date_publication"],
            errors="coerce",
        )

    return df


df = charger_donnees()


if df.empty:
    st.warning(
        "Aucune donnée disponible. Lancez d'abord `src/collect_offres.py`."
    )
    st.stop()


# ----------------------------------------------------------------
# INDICATEURS GLOBAUX
# ----------------------------------------------------------------
st.subheader("Indicateurs généraux")

total = len(df)

stages = 0
emplois = 0

if "type_offre" in df.columns:
    stages = (df["type_offre"] == "Stage").sum()
    emplois = (df["type_offre"] == "Emploi").sum()

avec_lien = 0

if "lien" in df.columns:
    avec_lien = df["lien"].astype(str).str.startswith("http").sum()

c1, c2, c3, c4 = st.columns(4)

c1.metric("Offres totales", total)
c2.metric("Stages", stages)
c3.metric("Emplois", emplois)
c4.metric("Avec lien", avec_lien)

st.divider()


# ----------------------------------------------------------------
# REPARTITION PAR TYPE
# ----------------------------------------------------------------
st.subheader("Répartition par type dopportunité")

if "type_offre" in df.columns:
    type_counts = (
        df["type_offre"]
        .astype(str)
        .str.strip()
        .replace("", np.nan)
        .dropna()
        .value_counts()
        .reset_index()
    )

    type_counts.columns = ["Type", "Nombre"]

    if not type_counts.empty:
        fig_type = px.bar(
            type_counts,
            x="Type",
            y="Nombre",
            color="Type",
            title="Nombre doffres par type",
        )

        st.plotly_chart(
            fig_type,
            use_container_width=True,
        )


# ----------------------------------------------------------------
# REPARTITION PAR SOURCE
# ----------------------------------------------------------------
st.subheader("Répartition par source")

if "source" in df.columns:
    source_counts = (
        df["source"]
        .astype(str)
        .str.strip()
        .replace("", np.nan)
        .dropna()
        .value_counts()
        .reset_index()
    )

    source_counts.columns = ["Source", "Nombre"]

    if not source_counts.empty:
        fig_source = px.pie(
            source_counts,
            names="Source",
            values="Nombre",
            title="Répartition des offres par source",
            hole=0.4,
        )

        st.plotly_chart(
            fig_source,
            use_container_width=True,
        )


# ----------------------------------------------------------------
# TOP ENTREPRISES
# ----------------------------------------------------------------
st.subheader("Entreprises les plus actives")

if "entreprise" not in df.columns:
    st.warning("Aucune donnée d'entreprise disponible.")
else:
    entreprises_clean = (
        df["entreprise"]
        .astype(str)
        .str.strip()
        .replace("", np.nan)
        .replace("nan", np.nan)
        .dropna()
    )

    if entreprises_clean.empty:
        st.warning("Aucune entreprise disponible pour l'analyse.")
    else:
        top_entreprises = (
            entreprises_clean
            .value_counts()
            .head(10)
        )

        st.bar_chart(top_entreprises)

# ----------------------------------------------------------------
# LIEUX
# ----------------------------------------------------------------
st.subheader("Répartition géographique")

if "lieu" not in df.columns:
    st.warning("Aucune donnée de lieu disponible.")
else:
    lieux_clean = (
        df["lieu"]
        .astype(str)
        .str.strip()
        .replace("", np.nan)
        .replace("nan", np.nan)
        .dropna()
    )

    if lieux_clean.empty:
        st.warning("Aucun lieu disponible pour l'analyse.")
    else:
        top_lieux = (
            lieux_clean
            .value_counts()
            .head(10)
            .reset_index()
        )

        top_lieux.columns = ["lieu", "nombre"]

        fig_lieux = px.bar(
            top_lieux,
            x="lieu",
            y="nombre",
            title="Top 10 des lieux",
            labels={
                "lieu": "Lieu",
                "nombre": "Nombre d'offres",
            },
        )

        st.plotly_chart(
            fig_lieux,
            use_container_width=True,
        )


# ----------------------------------------------------------------
# EVOLUTION TEMPORELLE
# ----------------------------------------------------------------
st.subheader("Évolution des offres")

if "date_publication" not in df.columns:
    st.warning("Aucune donnée de date disponible.")
else:
    df_dates = df.dropna(subset=["date_publication"])

    if df_dates.empty:
        st.warning("Aucune date valide disponible pour l'analyse.")
    else:
        df_dates["mois"] = df_dates["date_publication"].dt.to_period("M").astype(str)

        evolution = (
            df_dates
            .groupby("mois")
            .size()
            .reset_index(name="nombre")
        )

        fig_evolution = px.line(
            evolution,
            x="mois",
            y="nombre",
            markers=True,
            title="Évolution du nombre d'offres par mois",
        )

        st.plotly_chart(
            fig_evolution,
            use_container_width=True,
        )


# ----------------------------------------------------------------
# TABLEAU DETAILLE
# ----------------------------------------------------------------
st.subheader("Données analysées")

colonnes = [
    "titre",
    "entreprise",
    "type_offre",
    "lieu",
    "date_publication",
    "source",
    "origine",
]

colonnes = [c for c in colonnes if c in df.columns]

if colonnes:
    st.dataframe(
        df[colonnes],
        use_container_width=True,
        hide_index=True,
    )
else:
    st.warning("Aucune colonne disponible pour le tableau.")
