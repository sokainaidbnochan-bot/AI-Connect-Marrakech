# AI Connect Marrakech

**AI Connect Marrakech** est une plateforme web permettant de rechercher, collecter, analyser, visualiser, postuler et suivre les opportunités professionnelles et les offres de stage à Marrakech.

## Problématique

Les candidats à Marrakech rencontrent des difficultés pour trouver, comparer et suivre les offres d’emploi et de stage disponibles. Les informations sont souvent dispersées entre plusieurs sources, sans outil centralisé permettant d’analyser le marché local et de suivre ses candidatures.

## Objectifs

- Collecter automatiquement des offres à Marrakech.
- Nettoyer et préparer les données avec Python.
- Analyser le marché de l’emploi local.
- Visualiser les opportunités par secteur, entreprise, type de contrat et zone.
- Permettre la recherche, le filtrage et le suivi des offres.
- Intégrer une recommandation intelligente des offres.

## Fonctionnalités

- Inscription et connexion sécurisées.
- Collecte automatique des offres via l’API Jooble.
- Recherche et filtrage des offres.
- Classification des offres : Emploi, Stage, Alternance.
- Ajout manuel et import CSV.
- Suivi des candidatures.
- Tableau de bord analytique.
- Carte des entreprises et opportunités.
- Recommandation d’offres selon les compétences.

## Architecture

```text
Jooble API / Google Places / OpenStreetMap / CSV
                        ↓
              Collecte des données
                        ↓
        Nettoyage et préparation avec Python
                        ↓
              CSV / MySQL
                        ↓
         Backend Python et logique métier
                        ↓
             Interface Streamlit
                        ↓
                Utilisateur
```

## Stack technique

| Composant | Technologie |
|---|---|
| Frontend | Streamlit |
| Backend | Python |
| Base de données | MySQL |
| Collecte | Jooble API, Google Places API, OpenStreetMap |
| Traitement des données | Pandas, NumPy |
| Analyse | Pandas, Matplotlib, Seaborn |
| IA | Scikit-learn, TF-IDF, similarité cosinus |
| Versioning | GitHub |
| Déploiement | Streamlit Community Cloud |

## Structure du projet

```text
AI_Connect_Marrakech/
│
├── streamlit_app/
│   ├── Home.py
│   ├── auth_db.py
│   ├── auth_helpers.py
│   ├── candidature_db.py
│   ├── data_access.py
│   ├── offres.py
│   ├── suivi_db.py
│   ├── pages/
│   └── .streamlit/
│
├── src/
│   ├── collect_offres.py
│   ├── api_google_places.py
│   ├── collect_osm.py
│   ├── cleaning.py
│   ├── imputation.py
│   └── analysis.py
│
├── notebooks/
│   ├── 01_collecte_donnees.ipynb
│   ├── 02_nettoyage.ipynb
│   ├── 03_analyse.ipynb
│   └── 04_visualisation.ipynb
│
├── data/
│   ├── raw/
│   ├── cleaned/
│   └── processed/
│
├── outputs/
│   └── figures/
│
├── config/
├── requirements.txt
├── README.md
└── .gitignore
```

## Installation

### Prérequis

- Python 3.10 ou plus
- MySQL
- Une clé API Jooble
- Une clé API Google Places, si utilisée

### 1. Cloner le projet

```bash
git clone https://github.com/sokainaidbnochan-bot/AI-Connect-Marrakech.git
cd AI_Connect_Marrakech
```

### 2. Créer un environnement virtuel

```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Installer les dépendances

```bash
pip install -r requirements.txt
```

### 4. Configuration

Créez un fichier `.env` à partir de `.env.example` :

```env
JOOBLE_API_KEY=your_jooble_api_key
JOOBLE_BASE_URL=https://ma.jooble.org/api

MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=your_mysql_password
MYSQL_DATABASE=ai_connect_marrakech
```

Créez également le fichier :

```text
streamlit_app/.streamlit/secrets.toml
```

à partir de :

```text
streamlit_app/.streamlit/secrets.toml.example
```

## Lancement de l’application

Depuis le dossier `streamlit_app` :

```bash
cd streamlit_app
streamlit run Home.py
```

L’application sera disponible sur :

```text
http://localhost:8501
```

## Collecte des offres

Depuis la racine du projet :

```bash
python src/collect_offres.py
```

Les offres collectées sont enregistrées dans :

```text
data/raw/offres_jooble.csv
```

## Sources de données

- **Jooble API** : offres d’emploi et de stage.
- **Google Places API** : informations sur les entreprises.
- **OpenStreetMap** : localisation des entreprises.
- **CSV** : offres ajoutées manuellement et données de suivi.

## Nettoyage des données

Le nettoyage comprend :

- Suppression des doublons.
- Gestion des valeurs manquantes.
- Normalisation des noms d’entreprises.
- Nettoyage des textes.
- Extraction et classification des types d’offres.
- Imputation des valeurs manquantes.

## Intelligence artificielle

La plateforme utilise une approche de recommandation basée sur **TF-IDF** et la **similarité cosinus**. L’utilisateur saisit ses compétences, puis le système compare son profil avec les descriptions des offres afin de proposer les opportunités les plus pertinentes.

## Déploiement

L’application est déployée sur Streamlit Community Cloud :

https://ai-connect-marrakech-b6dcwcnwqqvg4va9nktthd.streamlit.app/Suivi
