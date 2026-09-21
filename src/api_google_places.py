import requests
import pandas as pd
import time
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from config.config import API_KEY
print("DEBUG - clé chargée :", repr(API_KEY))

URL = "https://places.googleapis.com/v1/places:searchText"

HEADERS = {
    "Content-Type": "application/json",
    "X-Goog-Api-Key": API_KEY,
    "X-Goog-FieldMask": ",".join([
        "places.id", "places.displayName", "places.formattedAddress",
        "places.location", "places.rating", "places.userRatingCount",
        "places.nationalPhoneNumber", "places.websiteUri", "places.primaryType",
    ])
}

REQUETES = [
    ("intelligence artificielle Marrakech", "ia"),
    ("développement web Marrakech", "web"),
    ("data science Marrakech", "data"),
    ("développement mobile Marrakech", "mobile"),
    ("agence digitale Marrakech", "web"),
    ("support informatique Marrakech", "it"),
]

resultats = []

for requete, categorie in REQUETES:
    print(f"Recherche : {requete}")
    body = {"textQuery": requete, "languageCode": "fr", "maxResultCount": 20}
    response = requests.post(URL, headers=HEADERS, json=body)

    if response.status_code != 200:
        print(f"  Erreur {response.status_code} : {response.text[:200]}")
        continue

    places = response.json().get("places", [])
    print(f"  {len(places)} résultats trouvés")

    for p in places:
        resultats.append({
            "nom": p.get("displayName", {}).get("text", ""),
            "categorie_recherchee": categorie,
            "adresse": p.get("formattedAddress", ""),
            "telephone": p.get("nationalPhoneNumber", ""),
            "site_web": p.get("websiteUri", ""),
            "note": p.get("rating", None),
            "nombre_avis": p.get("userRatingCount", None),
            "latitude": p.get("location", {}).get("latitude", None),
            "longitude": p.get("location", {}).get("longitude", None),
            "type_google": p.get("primaryType", ""),
            "place_id": p.get("id", ""),
        })
    time.sleep(1)

df = pd.DataFrame(resultats)
df = df.drop_duplicates(subset="place_id")
print(f"\nTotal après suppression des doublons : {len(df)} entreprises")

df.to_csv("../data/raw/entreprises_google_places.csv", index=False)
print("Sauvegardé dans data/raw/entreprises_google_places.csv")