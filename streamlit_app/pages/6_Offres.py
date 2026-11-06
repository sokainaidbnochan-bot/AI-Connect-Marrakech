import streamlit as st
import sys
from pathlib import Path
from datetime import date

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from auth_helpers import exiger_connexion
from data_access import charger_entreprises
from offres import (
    charger_offres,
    ajouter_offre_manuelle,
    ajouter_au_suivi,
    TYPES,
)

st.set_page_config(page_title="Offres", layout="wide")
exiger_connexion()

PAGE_CONTACT = "pages/5_Contact.py"

st.title("Offres de stage et d'emploi")

df = charger_offres()

tab_liste, tab_ajout = st.tabs(
    ["Offres", "Ajouter une offre"]
)

# ----------------------------------------------------------------
# LISTE DES OFFRES
# ----------------------------------------------------------------
with tab_liste:

    if df.empty:
        st.info(
            "Aucune offre pour le moment. Lancez `src/collect_offres.py` "
            "avec une clé Jooble, ou ajoutez une offre manuellement."
        )

    else:

        df["source_aff"] = df["source"].replace("", "Non précisée")

        c1, c2, c3, c4 = st.columns(4)

        type_f = c1.selectbox(
            "Type",
            ["Tous"] + TYPES,
        )

        source_f = c2.selectbox(
            "Source",
            ["Toutes"] + sorted(df["source_aff"].unique()),
        )

        mot = c3.text_input(
            "Mot-clé",
            placeholder="Titre, entreprise ou description",
        )

        tri = c4.selectbox(
            "Trier par",
            [
                "Plus récentes",
                "Plus anciennes",
                "Entreprise A-Z",
            ],
        )

        connues = st.checkbox(
            "Afficher seulement les entreprises de ma base"
        )

        filtre = df.copy()

        if type_f != "Tous":
            filtre = filtre[filtre["type_offre"] == type_f]

        if source_f != "Toutes":
            filtre = filtre[filtre["source_aff"] == source_f]

        if mot:
            texte = mot.lower().strip()

            masque = (
                filtre["titre"].str.lower().str.contains(texte, na=False)
                | filtre["entreprise"].str.lower().str.contains(texte, na=False)
                | filtre["extrait"].str.lower().str.contains(texte, na=False)
            )

            filtre = filtre[masque]

        if connues:
            filtre = filtre[filtre["entreprise_connue"] != ""]

        if tri == "Plus récentes":
            filtre = filtre.sort_values(
                "date_publication",
                ascending=False,
            )

        elif tri == "Plus anciennes":
            filtre = filtre.sort_values(
                "date_publication",
                ascending=True,
            )

        else:
            filtre = filtre.sort_values(
                "entreprise",
                ascending=True,
            )

        filtre = filtre.reset_index(drop=True)

        st.metric(
            "Offres trouvées",
            len(filtre),
        )

        st.caption(
            "Cliquez sur une ligne pour voir les détails et suivre loffre."
        )

        event = st.dataframe(
            filtre[
                [
                    "titre",
                    "entreprise",
                    "type_offre",
                    "lieu",
                    "date_publication",
                    "source_aff",
                ]
            ],
            width="stretch",
            hide_index=True,
            on_select="rerun",
            selection_mode="single-row",
            key="tableau_offres",
        )

        lignes = event.selection.rows

        if lignes and len(filtre) > 0 and lignes[0] < len(filtre):

            o = filtre.iloc[lignes[0]]

            st.divider()
            st.subheader(o["titre"])

            st.write(
                f"**Entreprise :** {o['entreprise']}  ·  "
                f"**Type :** {o['type_offre']}  ·  "
                f"**Lieu :** {o['lieu'] or '—'}"
            )

            if o["entreprise_connue"]:
                st.success(
                    f"Cette entreprise est dans votre base : "
                    f"{o['entreprise_connue']}"
                )

            st.write(
                f"**Publiée / mise à jour :** "
                f"{o['date_publication'] or '—'}  ·  "
                f"**Source :** {o['source_aff']}"
            )

            if o["salaire"]:
                st.write(f"**Salaire :** {o['salaire']}")

            if o["extrait"]:
                with st.expander("Voir la description"):
                    st.write(o["extrait"])

            b1, b2, b3 = st.columns(3)

            if o["lien"].startswith("http"):
                b1.link_button(
                    "Ouvrir loffre",
                    o["lien"],
                    width="stretch",
                )

            if b2.button(
                "Suivre cette offre",
                type="primary",
                width="stretch",
                key="suivre_offre",
            ):
                nom_suivi = (
                    o["entreprise_connue"]
                    or o["entreprise"]
                )

                if ajouter_au_suivi(o["titre"], nom_suivi):
                    st.success("Offre ajoutée à la page Suivi.")

                else:
                    st.info("Cette offre est déjà dans le Suivi.")

            if o["entreprise_connue"] and b3.button(
                "Contacter lentreprise",
                width="stretch",
                key="contacter_offre",
            ):
                st.session_state["entreprise_cible"] = (
                    o["entreprise_connue"]
                )

                st.switch_page(PAGE_CONTACT)

# ----------------------------------------------------------------
# AJOUT MANUEL
# ----------------------------------------------------------------
with tab_ajout:

    st.caption(
        "Ajoutez une offre trouvée sur LinkedIn, le site dune entreprise "
        "ou toute autre source."
    )

    noms = sorted(
        charger_entreprises()["nom"].dropna().unique()
    )

    with st.form("form_offre", clear_on_submit=True):

        titre = st.text_input("Titre de loffre *")

        choix = st.selectbox(
            "Entreprise de ma base",
            ["—"] + noms,
        )

        autre = st.text_input(
            "… ou autre entreprise",
            placeholder="Nom de lentreprise si elle nest pas dans la liste",
        )

        col_a, col_b = st.columns(2)

        type_offre = col_a.selectbox(
            "Type",
            TYPES,
        )

        lieu = col_b.text_input(
            "Lieu",
            value="Marrakech",
        )

        col_c, col_d = st.columns(2)

        date_pub = col_c.date_input(
            "Date de publication",
            value=date.today(),
        )

        source = col_d.text_input(
            "Source",
            placeholder="LinkedIn, site de lentreprise…",
        )

        lien = st.text_input("Lien de loffre")

        extrait = st.text_area(
            "Description courte",
            height=100,
        )

        envoyer = st.form_submit_button(
            "Ajouter loffre",
            type="primary",
        )

    if envoyer:

        entreprise = autre.strip() or (
            choix if choix != "—" else ""
        )

        ok, message = ajouter_offre_manuelle(
            titre,
            entreprise,
            type_offre,
            lieu,
            date_pub.isoformat(),
            lien,
            source,
            extrait,
        )

        if ok:
            st.success(message)

        else:
            st.error(message)

