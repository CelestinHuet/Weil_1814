"""
This file is part of 1814parlescartes.

1814parlescartes is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

1814parlescartes is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with 1814parlescartes. If not, see <https://www.gnu.org/licenses/>.
"""


from pathlib import Path
import os
import json
from datetime import datetime

input_dir = Path("resultats_v2")
output_dir = Path("resultats_v2_merge")
os.makedirs(output_dir, exist_ok=True)

def get_radicaux(files):
    radicaux = []
    for file in files:
        radical = "_".join(file.replace(".json", "").split("_")[:-2])
        if radical not in radicaux:
            radicaux.append(radical)
    return radicaux


def date_valide(date):
    try:
        splitted = date.split("/")
        if len(splitted)!=3:
            return False
        if len(splitted[0])!=2:
            return False
        if len(splitted[1])!=2:
            return False
        if len(splitted[2])!=4:
            return False
        
        jour = int(date[:2])
        mois = int(date[3:5])
        annee = int(date[6:])
        
        try:
            datetime(year=annee, month=mois, day=jour)
        except:
            return False

        return True

    except:
        return False


def complete_date(liste):
    for element in liste:
        if date_valide(element["date"]):
            current_date = element["date"]
            break
    
    for element in liste:
        if date_valide(element["date"]):
            element["date_approx"] = False
            current_date = element["date"]
        else:
            element["date_approx"] = True
            element["date"] = current_date
    
    return liste


def set_date_odb(data):
    current_date = None
    if date_valide(data["date"]):
        current_date = data["date"]
    else:
        for element in data["positions"]:
            if date_valide(element["date"]):
                current_date = element["date"]
                break
    for odb in data["ordre_de_bataille"]:
        odb["date"] = current_date


def run(radical, all_files):
    files = []
    for f in all_files:
        if radical in f:
            files.append([f, int(f.split("_")[-2])])
    files = sorted(files, key=lambda x:  x[1])

    merge_dict = {
        "positions":[],
        "ordre_de_bataille":[],
        "combat":[]
    }



    for file in files:
        with open(input_dir/file[0], "r") as f:
            data = json.load(f)

        set_date_odb(data)

        for position in data["positions"]:
            if position not in merge_dict["positions"]:
                merge_dict["positions"].append(position)
        
        for ordre_bataille in data["ordre_de_bataille"]:
            if ordre_bataille not in merge_dict["ordre_de_bataille"]:
                merge_dict["ordre_de_bataille"].append(ordre_bataille)

        for combat in data["combat"]:
            if combat not in merge_dict["combat"]:
                merge_dict["combat"].append(combat)
        
    merge_dict["positions"] = complete_date(merge_dict["positions"])
    merge_dict["ordre_de_bataille"] = complete_date(merge_dict["ordre_de_bataille"])
    merge_dict["combat"] = complete_date(merge_dict["combat"])

    with open(output_dir/f"{radical}.json", "w") as f:
        json.dump(merge_dict, f)

    

files = [i for i in os.listdir(input_dir) if i[-5:]==".json"]

radicaux = get_radicaux(files)

for radical in radicaux:
    run(radical, files)