import requests
import json
import time
from shapely import Point
import geopandas as gpd
import os
from tqdm import tqdm


def get_lieux():
    lieux = []
    json_files = [i for i in os.listdir("resultats/gemini_2-5_dates") if i[-5:]==".json"]
    for file in json_files:
        with open(os.path.join("resultats/gemini_2-5_dates", file), 'r') as f:
            data = json.load(f)
            for d in data["positions"]:
                lieux_unite = d["lieu"].split(";")
                lieux += lieux_unite
    return set(lieux)


# Charger les noms de villes depuis les fichiers JSON
lieux = get_lieux()

# Résultats : dictionnaire {nom: {lat: ..., lon: ...}}
resultats = {}
points = []
# Boucle sur les lieux
for lieu in tqdm(lieux):
    try:
        # Requête à l'API Nominatim
        response = requests.get(
            'https://nominatim.openstreetmap.org/search',
            params={
                'q': "bois des Forges",  # on précise France pour éviter les homonymes
                'format': 'json',
                'limit': 15,
                'countrycodes': 'fr,de,ch',  # France, Allemagne, Suisse
            },
            headers={'User-Agent': 'geo-script/1.0'}
        )

        response.raise_for_status()
        data = response.json()
        
        if data:
            resultats[lieu] = {
                'lat': data[0]['lat'],
                'lon': data[0]['lon']
            }
            points.append(Point(data[0]['lon'], data[0]['lat']))
        else:
            resultats[lieu] = None  # Aucun résultat trouvé

        time.sleep(1)  # pause pour respecter les règles de l'API (1 req/s)

    except Exception as e:
        print(f"Erreur pour le lieu '{lieu}': {e}")
        resultats[lieu] = None

# Sauvegarder les résultats dans un fichier JSON
with open('coordonnees.json', 'w', encoding='utf-8') as f:
    json.dump(resultats, f, ensure_ascii=False, indent=2)

print("Terminé. Coordonnées sauvegardées dans 'coordonnees.json'")
    

gpd.GeoDataFrame({"geometry":points}).set_crs(epsg=4326).to_file("coordonnees.gpkg")