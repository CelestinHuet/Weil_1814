import json
from pathlib import Path
import difflib
import os
from tqdm import tqdm

appariements = [
    ["Ligny","Ligny-en-Barrois"],
    ["Vassy","Wassy"],
    ["Eurville","Eurville-Bienville"],
    ["Dommartin","Dommartin-lès-Toul"],
    ["Bar","Bar-sur-Aube", "Bar-sur-Seine"],
    ["Vendeuvre","Vendeuvre-sur-Barse"],
    ["La Chaussée","La Chaussée-sur-Marne"],
    ["Brienne","Brienne-le-Château"],
    ["Saint-Urbain","Saint-Urbain-Maconcourt"],
    ["Thaon","Thaon-les-Vosges"],
    ["Perthes","Perthes-lès-Brienne"],
    ["Sainte-Croix","Sainte-Croix-en-Plaine"],
    ["Saint-Laurent","Epinal"],
    ["Bray","Bray-sur-Seine"],
    ["Mouy","Mouy-sur-Seine"],
    ["Nogent","Nogent-sur-Seine"],
    ["Bourg","Bourg-en-Bresse"],
    ["Tournay","Tournai"],
    ["La Ferté","La Ferté-sous-Jouarre", "Laferté-sur-Aube"],
    ["La Villette","Pantin"],
    ["Villette","Villette-sur-Aube"],
    ["Villeneuve","Villeneuve-le-Comte", "Villeneuve-les-Bordes"],
    ["Saint-Jean","Saint-Jean-Saverne"],
    ["Châlons","Châlons-en-Champagne"],
    ["Saint-Amand","Saint-Amand-sur-Fion"],
    ["Semilly","Semilly-sous-Laon"],
    ["Maisons-Blanches","Buchères"],
    ["Surville","Montereau-Fault-Yonne"],
    ["Varennes","Varennes-le-Grand"],
    ["Boulancourt","Longeville-sur-la-Laisnes"],
    ["Vitry","Vitry-le-François"],
    ["Somme-sous","Sommesous"],
    ["Saint-Michel","Saint-Michel-sur-Meurthe"],
    ["Saint-Hilaire","Saint-Hilaire-sous-Romilly"],
    ["Mont-Louis","Charonne"],
    ["Corbeil","Corbeil-Essonnes"],
    ["Marchais", "Marchais-en-Brie"],
    ["Vandoeuvres", "Vendeuvre-sur-Barse"]
]



def get_lieux():
    lieux = []
    json_files = [i for i in os.listdir("resultats_v2_merge") if i[-5:]==".json"]
    for file in json_files:
        with open(os.path.join("resultats_v2_merge", file), 'r') as f:
            data = json.load(f)
            for d in data["positions"]:
                positions_split = d["lieu"].split(";")
                for p in positions_split:
                    lieux.append(p.strip())
            
            if not "combat" in data.keys():
                continue
            for d in data["combat"]:
                positions_split = d["lieu"].split(";")
                for p in positions_split:
                    lieux.append(p.strip())
    return set(lieux)



def add(appariements, nom1, nom2):
    for appariement in appariements:
        if nom1 in appariement:
            appariement.append(nom2)
            return appariements
        elif nom2 in appariement:
            appariement.append(nom1)
            return appariements
    appariements.append([nom1, nom2])
    return appariements
    

lieux = list(get_lieux())
print(len(lieux))
for i in tqdm(range(len(lieux))):
    for j in range(i+1, len(lieux)):
        nom_i = lieux[i]
        nom_j = lieux[j]
        if nom_i != nom_j:
            ratio = difflib.SequenceMatcher(None, nom_i, nom_j).ratio()
            if ratio > 0.9:
                print(nom_i, nom_j)
                appariements = add(appariements, nom_i, nom_j)

with open("appariements_lieux.json", "w") as f:
    json.dump(appariements, f)
