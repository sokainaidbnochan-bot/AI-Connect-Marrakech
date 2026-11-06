import streamlit as st
import sys
from pathlib import Path

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
        "Aucune donnée disponible. Lancez dabord `src/collect_offres.py`."
    )
    st.stop()

# ----------------------------------------------------------------
# INDICATEURS GLOBAUX
# ----------------------------------------------------------------
st.subheader("Indicateurs généraux")

total = len(df)
stages = (df["type_offre"] == "Stage").sum()
emplois = (df["type_offre"] == "Emploi").sum()


avec_lien = df["lien"].str.startswith("http").sum()

c1, c2, c3, c4 = st.columns(4)

c1.metric("Offres totales", total)
c2.metric("Stages", stages)
c3.metric("Emplois", emplois)


st.divider()

# ----------------------------------------------------------------
# REPARTITION PAR TYPE
# ----------------------------------------------------------------
st.subheader("Répartition par type d’opportunité")

if "type_offre" in df.columns:
    type_counts = df["type_offre"].value_counts().reset_index()
    type_counts.columns = ["Type", "Nombre"]

    fig_type = px.bar(
        type_counts,
        x="Type",
        y="Nombre",
        color="Type",
        title="Nombre d’offres par type",
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
    source_counts = df["source"].value_counts().reset_index()
    source_counts.columns = ["Source", "Nombre"]

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

if "entreprise" in df.columns:
    entreprises = (
        df["entreprise"]
        .value_counts()
        .head(10)
        .reset_index()
    )

    entreprises.columns = ["Entreprise", "Nombre d’offres"]

    fig_entreprises = px.bar(
        entreprises,
        x="Nombre doffres",
        y="Entreprise",
        orientation="h",
        title="Top 10 des entreprises",
        color="Nombre doffres",
    )

    st.plotly_chart(
        fig_entreprises,
        use_container_width=True,
    )

# ----------------------------------------------------------------
# LIEUX
# ----------------------------------------------------------------
st.subheader("Répartition géographique")

if "lieu" in df.columns:
    lieux = (
        df["lieu"]
        .value_counts()
        .head(10)
        .reset_index()
    )

    lieux.columns = ["Lieu", "Nombre doffres"]

    fig_lieux = px.bar(
        lieux,
        x="Lieu",
        y="Nombre doffres",
        title="Top 10 des lieux",
        color="Nombre doffres",
    )

    st.plotly_chart(
        fig_lieux,
        use_container_width=True,
    )

# ----------------------------------------------------------------
# EVOLUTION TEMPORELLE
# ----------------------------------------------------------------
st.subheader("Évolution des offres")

if "date_publication" in df.columns and df["date_publication"].notna().any():

    df["mois"] = df["date_publication"].dt.to_period("M").astype(str)

    evolution = (
        df.groupby("mois")
        .size()
        .reset_index(name="Nombre doffres")
    )

    fig_evolution = px.line(
        evolution,
        x="mois",
        y="Nombre d’offres",
        markers=True,
        title="Évolution du nombre d’offres par mois",
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

st.dataframe(
    df[colonnes],
    width="stretch",
    hide_index=True,
)