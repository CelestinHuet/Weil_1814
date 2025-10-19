import requests
import json
import time
from shapely import Point
import geopandas as gpd
import os
from tqdm import tqdm




def get_appariement(lieux_appariements, lieu):
    for appariement in lieux_appariements:
        if lieu in appariement["appariement"]:
            return appariement["resultats"]
    return None


def get_lieux():
    lieux = []
    json_files = [i for i in os.listdir("resultats") if i[-5:]==".json"]
    for file in json_files:
        with open(os.path.join("resultats", file), 'r') as f:
            data = json.load(f)
            for d in data["positions"]:
                positions_split = d["lieu"].split(";")
                for p in positions_split:
                    lieux.append(p)
            
            if not "combat" in data.keys():
                continue
            for d in data["combat"]:
                positions_split = d["lieu"].split(";")
                for p in positions_split:
                    lieux.append(p)
    return set(lieux)


def requete(l):
    print(l)
    countrycodes = 'fr,de,ch,be,lu,nl'
    time.sleep(1)  # pause pour respecter les règles de l'API (1 req/s)
    try:
        response = requests.get(
            'https://nominatim.openstreetmap.org/search',
            params={
                'q': l,  # on précise France pour éviter les homonymes
                'format': 'json',
                'limit': 100,
                'countrycodes':countrycodes ,  # France, Allemagne, Suisse
            },
            headers={'User-Agent': 'geo-script/1.0'}
        )
        response.raise_for_status()
    except:
        time.sleep(60)
        response = requests.get(
            'https://nominatim.openstreetmap.org/search',
            params={
                'q': l,  # on précise France pour éviter les homonymes
                'format': 'json',
                'limit': 100,
                'countrycodes': countrycodes,  # France, Allemagne, Suisse, Blegique, Luxembourg, Pays-bas
            },
            headers={'User-Agent': 'geo-script/1.0'}
        )
        response.raise_for_status()
    return response


# Charger les noms de villes depuis les fichiers JSON
lieux = get_lieux()

accepted_types = [
    "administrative",
    "city",
    "bridge",
    "forest",
    "hamlet",
    "locality",
    "wood"
]

with open("appariements_lieux.json", "r") as f:
    appariements = json.load(f)

lieux_appariements = []

for appariement in tqdm(appariements):
    resultats_appariements = []
    for l in appariement:
        response = requete(l)
        data = response.json()
        if data:
            for d in data:
                if d["type"] in accepted_types:
                    resultats_appariements.append({"lat":d['lat'], "lon":d['lon'], "type":d["type"]})
    lieux_appariements.append({"appariement":appariement,"resultats":resultats_appariements})



# Résultats : dictionnaire {nom: {lat: ..., lon: ...}}
resultats = []

# Boucle sur les lieux
for lieu in tqdm(lieux):
    liste_lieux = lieu.split(";")
    lat = 0
    lon = 0
    compte = 0
    for l in liste_lieux:
        lieux_equivalents = get_appariement(lieux_appariements, l)
        if lieux_equivalents is not None:
            for l_equi in lieux_equivalents:
                resultats.append({"lieu":l, "lat":l_equi['lat'], "lon":l_equi['lon']})
        else:
            response = requete(l)
            data = response.json()
            if data:
                for d in data:
                    if d["type"] in accepted_types:
                        resultats.append({"lieu":lieu, "lat":d['lat'], "lon":d['lon'], "type":d["type"]})


# Sauvegarder les résultats dans un fichier JSON
with open('coordonnees.json', 'w', encoding='utf-8') as f:
    json.dump(resultats, f, ensure_ascii=False, indent=2)

print("Terminé. Coordonnées sauvegardées dans 'coordonnees.json'")