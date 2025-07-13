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
                lieux.append(d["lieu"])
    return set(lieux)


# Charger les noms de villes depuis les fichiers JSON
lieux = get_lieux()

# Résultats : dictionnaire {nom: {lat: ..., lon: ...}}
resultats = {}
points = []
noms = []
# Boucle sur les lieux
for lieu in tqdm(lieux):
    liste_lieux = lieu.split(";")
    lat = 0
    lon = 0
    compte = 0
    for l in liste_lieux:
        # Requête à l'API Nominatim
        response = requests.get(
            'https://nominatim.openstreetmap.org/search',
            params={
                'q': l,  # on précise France pour éviter les homonymes
                'format': 'json',
                'limit': 15,
                'countrycodes': 'fr,de,ch',  # France, Allemagne, Suisse
            },
            headers={'User-Agent': 'geo-script/1.0'}
        )
        response.raise_for_status()
        data = response.json()
        if data:
            lat += float(data[0]['lat'])
            lon += float(data[0]['lon'])
            compte += 1
    
    if compte != 0:
        resultats[lieu] = {
            'lat': lat/compte,
            'lon': lon/compte
        }
        points.append(Point(lon/compte, lat/compte))
        noms.append(lieu)
    else:
        resultats[lieu] = None  # Aucun résultat trouvé
    time.sleep(1)  # pause pour respecter les règles de l'API (1 req/s)



# Sauvegarder les résultats dans un fichier JSON
with open('coordonnees.json', 'w', encoding='utf-8') as f:
    json.dump(resultats, f, ensure_ascii=False, indent=2)

print("Terminé. Coordonnées sauvegardées dans 'coordonnees.json'")
    

gpd.GeoDataFrame({"lieu":noms, "geometry":points}).set_crs(epsg=4326).to_file("coordonnees.gpkg")