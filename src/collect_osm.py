import requests
import pandas as pd

# Mirror alternatif (parfois plus fiable que overpass-api.de)
OVERPASS_URL = "https://overpass.kumi.systems/api/interpreter"

BBOX = "31.55,-8.10,31.70,-7.90"

QUERY = f"""
[out:json][timeout:60];
(
  node["office"~"it|coworking|software"]({BBOX});
  way["office"~"it|coworking|software"]({BBOX});
  node["shop"="computer"]({BBOX});
  node["name"~"tech|digital|data|informatique|software",i]({BBOX});
  way["name"~"tech|digital|data|informatique|software",i]({BBOX});
);
out center tags;
"""

HEADERS = {
    "Content-Type": "text/plain; charset=utf-8",
    "User-Agent": "AIConnectMarrakech-EtudianteProjet/1.0 (contact: exemple@etu.ma)",
    "Accept": "*/*",
}

response = requests.post(OVERPASS_URL, data=QUERY.encode("utf-8"), headers=HEADERS)

if response.status_code != 200:
    print(f"Erreur {response.status_code} : {response.text[:300]}")
else:
    elements = response.json().get("elements", [])
    print(f"{len(elements)} résultats trouvés sur OpenStreetMap")

    resultats = []
    for el in elements:
        tags = el.get("tags", {})
        nom = tags.get("name")
        if not nom:
            continue

        lat = el.get("lat") or el.get("center", {}).get("lat")
        lon = el.get("lon") or el.get("center", {}).get("lon")

        adresse_parts = [
            tags.get("addr:housenumber", ""),
            tags.get("addr:street", ""),
            tags.get("addr:suburb", ""),
        ]
        adresse = " ".join(p for p in adresse_parts if p).strip()

        resultats.append({
            "nom": nom,
            "categorie_recherchee": tags.get("office", tags.get("shop", "non_categorise")),
            "adresse": adresse if adresse else None,
            "telephone": tags.get("contact:phone", tags.get("phone")),
            "site_web": tags.get("contact:website", tags.get("website")),
            "note": None,
            "nombre_avis": None,
            "latitude": lat,
            "longitude": lon,
            "type_google": "osm",
            "place_id": f"osm_{el.get('type')}_{el.get('id')}",
        })

    df = pd.DataFrame(resultats)
    df = df.drop_duplicates(subset="place_id")
    print(f"Après nettoyage des doublons : {len(df)} entreprises")

    df.to_csv("../data/raw/entreprises_osm.csv", index=False)
    print("Sauvegardé dans data/raw/entreprises_osm.csv")