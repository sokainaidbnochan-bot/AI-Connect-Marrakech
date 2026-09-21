import pandas as pd
import math

df_google = pd.read_csv("../data/raw/entreprises_google_places.csv")
df_osm = pd.read_csv("../data/raw/entreprises_osm.csv")

print(f"Google Places : {len(df_google)} lignes")
print(f"OpenStreetMap : {len(df_osm)} lignes")

df = pd.concat([df_google, df_osm], ignore_index=True)
print(f"Total combiné : {len(df)} lignes")

df = df.dropna(subset=["nom"])
df["nom_normalise"] = df["nom"].str.strip().str.lower()
df = df.drop_duplicates(subset="nom_normalise")
df = df.drop(columns="nom_normalise")

df["telephone"] = df["telephone"].fillna("Non renseigné")
df["site_web"] = df["site_web"].fillna("Non renseigné")
# note et nombre_avis restent avec leurs valeurs manquantes (NaN) -> imputation.py s'en charge

QUARTIER_CENTRES = {
    "Guéliz":       (31.6395, -8.0086),
    "Hivernage":    (31.6255, -8.0025),
    "Médina":       (31.6295, -7.9811),
    "Sidi Ghanem":  (31.6620, -8.0210),
    "Targa":        (31.6550, -8.0430),
    "Semlalia":     (31.6480, -8.0150),
    "Mhamid":       (31.5850, -8.0250),
}

def quartier_le_plus_proche(lat, lon):
    if pd.isna(lat) or pd.isna(lon):
        return "Non géolocalisé"
    distances = {
        nom: math.dist((lat, lon), centre)
        for nom, centre in QUARTIER_CENTRES.items()
    }
    return min(distances, key=distances.get)

df["quartier"] = df.apply(lambda row: quartier_le_plus_proche(row["latitude"], row["longitude"]), axis=1)

CATEGORIES_NON_TECH = [
    "educational_institution", "electronics", "government", "car", "beauty"
]
avant = len(df)
df = df[~df["categorie_recherchee"].isin(CATEGORIES_NON_TECH)]
print(f"\n{avant - len(df)} entreprises hors-sujet retirées "
      f"({', '.join(CATEGORIES_NON_TECH)})")

colonnes_finales = [
    "nom", "categorie_recherchee", "type_google", "quartier",
    "adresse", "telephone", "site_web", "note", "nombre_avis",
    "latitude", "longitude", "place_id"
]
df = df[colonnes_finales]

print(f"\nTotal après nettoyage et dédoublonnage : {len(df)} entreprises")
print("\nRépartition par quartier :")
print(df["quartier"].value_counts())
print("\nValeurs manquantes restantes :")
print(df[["note", "nombre_avis"]].isna().sum())

df.to_excel("../data/cleaned/entreprises_cleaned.xlsx", index=False)
print("\nSauvegardé : data/cleaned/entreprises_cleaned.xlsx")
print("(prochaine étape : lancer imputation.py pour traiter les valeurs manquantes de note/nombre_avis)")