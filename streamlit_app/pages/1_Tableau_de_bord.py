import pandas as pd
import plotly.express as px
import streamlit as st

from data_access import charger_entreprises


# =====================================================
# 1. CONFIGURATION
# =====================================================
st.set_page_config(
    page_title="Dashboard - AI Connect Marrakech",
    layout="wide",
    initial_sidebar_state="expanded",
)


# =====================================================
# 2. PROTECTION DE LA PAGE
# =====================================================
if (
    not st.session_state.get("authenticated", False)
    or not st.session_state.get("user")
):
    st.warning("Veuillez vous connecter depuis la page d'accueil.")
    st.page_link("Home.py", label="← Retour à l'accueil")
    st.stop()


# =====================================================
# 3. STYLE
# =====================================================
st.markdown(
    """
    <style>
        .stApp {
            background-color: #f6f2e9;
        }

        .block-container {
            padding-top: 2rem;
            padding-bottom: 3rem;
            max-width: 1400px;
        }

        footer {
            visibility: hidden;
        }

        section[data-testid="stSidebar"] {
            background-color: #fcfaf4;
            border-right: 1px solid #e5dfd4;
        }

        .dashboard-title {
            font-family: Georgia, serif;
            font-size: 36px;
            font-weight: 600;
            color: #24221d;
            margin-bottom: 6px;
        }

        .dashboard-subtitle {
            color: #787168;
            font-size: 14px;
            margin-bottom: 25px;
        }

        div[data-testid="stMetric"] {
            background: #ffffff;
            border: 1px solid #e5dfd4;
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.04);
        }

        div[data-testid="stMetricValue"] {
            color: #304fc1;
        }

        div[data-testid="stPlotlyChart"] {
            background: #ffffff;
            border: 1px solid #e5dfd4;
            border-radius: 12px;
            padding: 8px;
        }

        div[data-testid="stButton"] button {
            border-radius: 8px;
            min-height: 42px;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


# =====================================================
# 4. SIDEBAR
# =====================================================
with st.sidebar:
    st.markdown("## AI Connect Marrakech")
    st.caption("Explorer l'écosystème technologique local.")

    st.divider()

    st.page_link(
        "Home.py",
        label="Accueil",
    )

    st.page_link(
        "pages/1_Tableau_de_bord.py",
        label="Dashboard",
    )

    st.page_link(
        "pages/2_Entreprises.py",
        label="Entreprises",
    )

    st.page_link(
        "pages/3_Carte.py",
        label="Carte",
    )

    st.page_link(
        "pages/4_Suivi.py",
        label="Suivi des candidatures",
    )

    # Décommenter uniquement si ce fichier existe.
    # st.page_link(
    #     "pages/5_Contact.py",
    #     label="Contact",
    # )

    st.divider()

    if st.button(
        "Déconnexion",
        key="dashboard_logout",
        use_container_width=True,
    ):
        st.session_state.authenticated = False
        st.session_state.user = None
        st.session_state.screen = "home"
        st.session_state.auth_mode = "login"

        st.switch_page("Home.py")


# =====================================================
# 5. CHARGEMENT DES DONNÉES
# =====================================================
try:
    df = charger_entreprises().copy()

except Exception:
    st.error(
        "Impossible de charger les entreprises. "
        "Vérifiez la fonction charger_entreprises()."
    )
    st.stop()

if df.empty:
    st.info("Aucune entreprise disponible pour le moment.")
    st.stop()


# =====================================================
# 6. NETTOYAGE
# =====================================================
for colonne in ["categorie_recherchee", "quartier"]:
    if colonne in df.columns:
        df[colonne] = (
            df[colonne]
            .fillna("Non renseigné")
            .astype(str)
            .str.strip()
            .replace("", "Non renseigné")
        )


# Détecter la colonne du nom des entreprises.
colonne_nom = next(
    (
        colonne
        for colonne in [
            "nom",
            "name",
            "entreprise",
            "nom_entreprise",
        ]
        if colonne in df.columns
    ),
    None,
)


# =====================================================
# 7. TITRE
# =====================================================
st.markdown(
    '<div class="dashboard-title">Dashboard</div>',
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="dashboard-subtitle">
        Analyse des entreprises technologiques de Marrakech.
    </div>
    """,
    unsafe_allow_html=True,
)


# =====================================================
# 8. FILTRES
# =====================================================
st.subheader("Filtres")

col_filtre1, col_filtre2, col_filtre3 = st.columns(3)

domaines_selectionnes = []
quartiers_selectionnes = []
recherche = ""

with col_filtre1:
    if "categorie_recherchee" in df.columns:
        domaines_selectionnes = st.multiselect(
            "Domaine",
            options=sorted(
                df["categorie_recherchee"].unique().tolist()
            ),
            placeholder="Tous les domaines",
            key="dashboard_domaines",
        )
    else:
        st.caption("Colonne categorie_recherchee absente.")

with col_filtre2:
    if "quartier" in df.columns:
        quartiers_selectionnes = st.multiselect(
            "Quartier",
            options=sorted(
                df["quartier"].unique().tolist()
            ),
            placeholder="Tous les quartiers",
            key="dashboard_quartiers",
        )
    else:
        st.caption("Colonne quartier absente.")

with col_filtre3:
    if colonne_nom:
        recherche = st.text_input(
            "Rechercher une entreprise",
            placeholder="Nom de l’entreprise...",
            key="dashboard_recherche",
        )
    else:
        st.caption("Colonne du nom des entreprises introuvable.")


# =====================================================
# 9. APPLICATION DES FILTRES
# =====================================================
df_filtre = df.copy()

if domaines_selectionnes:
    df_filtre = df_filtre[
        df_filtre["categorie_recherchee"].isin(
            domaines_selectionnes
        )
    ]

if quartiers_selectionnes:
    df_filtre = df_filtre[
        df_filtre["quartier"].isin(
            quartiers_selectionnes
        )
    ]

if colonne_nom and recherche.strip():
    df_filtre = df_filtre[
        df_filtre[colonne_nom]
        .fillna("")
        .astype(str)
        .str.contains(
            recherche.strip(),
            case=False,
            regex=False,
        )
    ]


# =====================================================
# 10. CALCUL DES INDICATEURS
# =====================================================
total = len(df_filtre)

nombre_domaines = 0
nombre_quartiers = 0
pourcentage_gps = "Non disponible"

if "categorie_recherchee" in df_filtre.columns:
    nombre_domaines = df_filtre.loc[
        df_filtre["categorie_recherchee"] != "Non renseigné",
        "categorie_recherchee",
    ].nunique()

if "quartier" in df_filtre.columns:
    nombre_quartiers = df_filtre.loc[
        df_filtre["quartier"] != "Non renseigné",
        "quartier",
    ].nunique()

if {"latitude", "longitude"}.issubset(df_filtre.columns):
    latitude = pd.to_numeric(
        df_filtre["latitude"],
        errors="coerce",
    )

    longitude = pd.to_numeric(
        df_filtre["longitude"],
        errors="coerce",
    )

    coordonnees_valides = (
        latitude.between(-90, 90)
        & longitude.between(-180, 180)
    )

    pourcentage_gps = (
        f"{coordonnees_valides.sum() / total:.0%}"
        if total
        else "0%"
    )


# =====================================================
# 11. AFFICHAGE DES INDICATEURS
# =====================================================
st.divider()

col1, col2, col3, col4 = st.columns(4)

col1.metric("Entreprises affichées", total)
col2.metric("Domaines représentés", nombre_domaines)
col3.metric("Quartiers représentés", nombre_quartiers)
col4.metric("Coordonnées GPS valides", pourcentage_gps)

st.caption(
    f"{total} ligne(s) affichée(s) sur {len(df)}. "
    "Le comptage suppose une ligne par entreprise. "
    "Les valeurs « Non renseigné » sont exclues du nombre "
    "de domaines et de quartiers."
)

if df_filtre.empty:
    st.info(
        "Aucune entreprise ne correspond aux filtres. "
        "Modifiez vos critères pour afficher des résultats."
    )
    st.stop()


# =====================================================
# 12. FONCTION DE STYLE DES GRAPHIQUES
# =====================================================
def styliser_graphique(figure, hauteur=420):
    figure.update_layout(
        height=hauteur,
        template="plotly_white",
        paper_bgcolor="#ffffff",
        plot_bgcolor="#ffffff",
        font=dict(
            family="Arial",
            color="#49443c",
        ),
        margin=dict(
            l=25,
            r=30,
            t=65,
            b=35,
        ),
        title=dict(
            font=dict(size=18),
            x=0.03,
        ),
    )

    return figure


# =====================================================
# 13. GRAPHIQUES PAR DOMAINE
# =====================================================
st.divider()
st.subheader("Répartition des entreprises")

couleurs = [
    "#304FC1",
    "#6B83D6",
    "#A68A68",
    "#D4B88F",
    "#579A91",
    "#8F79B8",
    "#D58B78",
]

if "categorie_recherchee" in df_filtre.columns:
    repartition_domaines = (
        df_filtre["categorie_recherchee"]
        .value_counts()
        .rename_axis("Domaine")
        .reset_index(name="Nombre")
    )

    graphique1, graphique2 = st.columns(2)

    # ---------------------------------------------
    # BAR CHART
    # ---------------------------------------------
    with graphique1:
        fig_domaines = px.bar(
            repartition_domaines,
            x="Domaine",
            y="Nombre",
            text="Nombre",
            title="Entreprises par domaine",
            color_discrete_sequence=["#304FC1"],
        )

        fig_domaines.update_traces(
            textposition="outside",
            cliponaxis=False,
            hovertemplate=(
                "Domaine : %{x}"
                "<br>Entreprises : %{y}"
                "<extra></extra>"
            ),
        )

        styliser_graphique(fig_domaines)

        fig_domaines.update_layout(
            xaxis_title=None,
            yaxis_title="Nombre d’entreprises",
        )

        fig_domaines.update_yaxes(
            rangemode="tozero",
            tickformat=",d",
        )

        st.plotly_chart(
            fig_domaines,
            use_container_width=True,
            key="dashboard_graph_domaines",
        )

    # ---------------------------------------------
    # DONUT CHART
    # ---------------------------------------------
    with graphique2:
        fig_donut = px.pie(
            repartition_domaines,
            names="Domaine",
            values="Nombre",
            hole=0.55,
            title="Part des entreprises par domaine",
            color_discrete_sequence=couleurs,
        )

        fig_donut.update_traces(
            textinfo="percent",
            hovertemplate=(
                "%{label}"
                "<br>Entreprises : %{value}"
                "<br>Part : %{percent}"
                "<extra></extra>"
            ),
        )

        styliser_graphique(fig_donut)

        fig_donut.update_layout(
            legend_title_text="Domaine",
        )

        st.plotly_chart(
            fig_donut,
            use_container_width=True,
            key="dashboard_graph_donut",
        )

else:
    st.info(
        "Ajoutez la colonne categorie_recherchee "
        "pour afficher les graphiques par domaine."
    )


# =====================================================
# 14. GRAPHIQUE PAR QUARTIER
# =====================================================
if "quartier" in df_filtre.columns:
    repartition_quartiers = (
        df_filtre["quartier"]
        .value_counts()
        .head(10)
        .rename_axis("Quartier")
        .reset_index(name="Nombre")
        .sort_values("Nombre", ascending=True)
    )

    fig_quartiers = px.bar(
        repartition_quartiers,
        x="Nombre",
        y="Quartier",
        orientation="h",
        text="Nombre",
        title="Les 10 quartiers les plus représentés",
        color_discrete_sequence=["#A68A68"],
    )

    fig_quartiers.update_traces(
        textposition="outside",
        cliponaxis=False,
        hovertemplate=(
            "Quartier : %{y}"
            "<br>Entreprises : %{x}"
            "<extra></extra>"
        ),
    )

    styliser_graphique(fig_quartiers, hauteur=450)

    fig_quartiers.update_layout(
        xaxis_title="Nombre d'entreprises",
        yaxis_title=None,
    )

    fig_quartiers.update_xaxes(
        rangemode="tozero",
        tickformat=",d",
    )

    st.plotly_chart(
        fig_quartiers,
        use_container_width=True,
        key="dashboard_graph_quartiers",
    )

else:
    st.info(
        "Ajoutez la colonne quartier pour afficher "
        "la répartition géographique."
    )


# =====================================================
# 15. TABLEAU DES RÉSULTATS
# =====================================================
st.divider()
st.subheader("Entreprises correspondant aux filtres")

colonnes_visibles = []

if colonne_nom:
    colonnes_visibles.append(colonne_nom)

for colonne in [
    "categorie_recherchee",
    "quartier",
    "adresse",
    "telephone",
    "website",
]:
    if (
        colonne in df_filtre.columns
        and colonne not in colonnes_visibles
    ):
        colonnes_visibles.append(colonne)

if colonnes_visibles:
    st.dataframe(
        df_filtre[colonnes_visibles],
        use_container_width=True,
        hide_index=True,
    )
else:
    st.info(
        "Adaptez les noms des colonnes du tableau "
        "à ceux de votre fichier de données."
    )