import requests
import json
import time
from shapely import Point
import geopandas as gpd
import os
from tqdm import tqdm




nouveaux_noms = {
    "Ligny":["Ligny-en-Barrois"],
    "Vassy":["Wassy"],
    "Eurville":["Eurville-Bienville"],
    "Dommartin":["Dommartin-lès-Toul"],
    "Bar":["Bar-sur-Aube", "Bar-sur-Seine"],
    "Vendeuvre":["Vendeuvre-sur-Barse"],
    "La Chaussée":["La Chaussée-sur-Marne"],
    "Brienne":["Brienne-le-Château"],
    "Saint-Urbain":["Saint-Urbain-Maconcourt"],
    "Thaon":["Thaon-les-Vosges"],
    "Perthes":["Perthes-lès-Brienne"],
    "Sainte-Croix":["Sainte-Croix-en-Plaine"],
    "Saint-Laurent":["Epinal"],
    "Bray":["Bray-sur-Seine"],
    "Mouy":["Mouy-sur-Seine"],
    "Nogent":["Nogent-sur-Seine"],
    "Bourg":["Bourg-en-Bresse"],
    "Tournay":["Tournai"],
    "La Ferté":["La Ferté-sous-Jouarre", "Laferté-sur-Aube"],
    "La Villette":["Pantin"],
    "Villette":["Villette-sur-Aube"],
    "Villeneuve":["Villeneuve-le-Comte", "Villeneuve-les-Bordes"],
    "Saint-Jean":["Saint-Jean-Saverne"],
    "Châlons":["Châlons-en-Champagne"],
    "Saint-Amand":["Saint-Amand-sur-Fion"],
    "Semilly":["Semilly-sous-Laon"],
    "Maisons-Blanches":["Buchères"],
    "Surville":["Montereau-Fault-Yonne"],
    "Varennes":["Varennes-le-Grand"],
    "Boulancourt":["Longeville-sur-la-Laisnes"],
    "Vitry":["Vitry-le-François"],
    "Somme-sous":["Sommesous"],
    "Saint-Michel":["Saint-Michel-sur-Meurthe"],
    "Saint-Hilaire":["Saint-Hilaire-sous-Romilly"],
    "Mont-Louis":["Charonne"],
    "Corbeil":["Corbeil-Essonnes"]
}


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

# Résultats : dictionnaire {nom: {lat: ..., lon: ...}}
resultats = []
points = []
noms = []
types = []
# Boucle sur les lieux
for lieu in tqdm(lieux):
    liste_lieux = lieu.split(";")
    lat = 0
    lon = 0
    compte = 0
    for l in liste_lieux:
        response = requete(l)
        data = response.json()
        if data:
            for d in data:
                if d["type"] in accepted_types:
                    resultats.append({"lieu":lieu, "lat":d['lat'], "lon":d['lon'], "type":d["type"]})
                    points.append(Point(d['lon'], d['lat']))
                    noms.append(lieu)
                    types.append(d["type"])
    
        if l in list(nouveaux_noms.keys()):
            for nouveau_nom in nouveaux_noms[l]:
                response = requete(nouveau_nom)
                data = response.json()
                if data:
                    for d in data:
                        if d["type"] in accepted_types:
                            resultats.append({"lieu":lieu, "lat":d['lat'], "lon":d['lon'], "type":d["type"]})
                            points.append(Point(d['lon'], d['lat']))
                            noms.append(lieu)
                            types.append(d["type"])




# Sauvegarder les résultats dans un fichier JSON
with open('coordonnees.json', 'w', encoding='utf-8') as f:
    json.dump(resultats, f, ensure_ascii=False, indent=2)

print("Terminé. Coordonnées sauvegardées dans 'coordonnees.json'")
    

gpd.GeoDataFrame({"lieu":noms, "type":types, "geometry":points}).set_crs(epsg=4326).to_file("coordonnees.gpkg")