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


def convert(date):
    jour = int(date[:2])
    mois = int(date[3:5])
    annee = int(date[6:])
    return datetime(year=annee, month=mois, day=jour)


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

input_dir = Path("resultats/")
output_dir = Path("resultats/gemini_2-5_dates_corrected")
os.makedirs(output_dir, exist_ok=True)


json_files = [[i, int(i.replace(".json", "").split("-")[1])] for i in os.listdir(input_dir) if i[-5:]==".json"]

list_dates = []

# Pour chaque fichier json, on récupère la date et on met un champ nouvelle date
for json_file in sorted(json_files):
    with open(input_dir/json_file[0], "r") as f:
        data = json.load(f)
    list_dates.append(
        {
            "file":json_file,
            "date":data["date"],
            "nouvelle_date":None
        }
    )

# On parcourt chaque fichier json
for i in range(len(list_dates)-5):
    d0 = list_dates[i]
    # Si on a déjà mis une nouvelle date, on passe au fichier suivant
    if d0["nouvelle_date"] is not None:
        continue
    # Si la date n'est pas valide, on passe au fichier suivant
    if not date_valide(d0["date"]):
        continue
    # On parcourt les cinq fichiers suivants. Si l'un des cinq a la même date que le fichier en cours
    # alors on s'arrête
    for j in range(5, 0, -1):
        if list_dates[i+j]["date"]==d0["date"]:
            break
    # On rempli le champ nouvelle date pour chaque fichier json
    #  intercalé entre les deux à la cndition qu'il n'a pas la même date 
    for k in range(1, j):
        if list_dates[i+k]["date"]!=d0["date"] and list_dates[i+k]["nouvelle_date"] is None:
            print(f"Dans {list_dates[i+k]["file"]}, on remplace {list_dates[i+k]["date"]} par {d0["date"]}")
            list_dates[i+k]["nouvelle_date"] = d0["date"]

# On parcourt chaque fichier json
current_date = "01/12/1813"
for element in list_dates:
    filename = element["file"][0]
    with open(input_dir/filename, "r") as f:
        data = json.load(f)

        # On récupère la date remlaçant : celle récupérée précédemment, celle issue de Gemini, ou current date
        if date_valide(element["nouvelle_date"]):
            date_remplacant = element["nouvelle_date"]
        elif date_valide(element["date"]):
            date_remplacant = element["date"]
        else:
            date_remplacant = current_date

        print(filename, date_remplacant)
        
        # Pour chaque position ou combat, si la date n'est pas valide, on la remplace par date_remplacant
        for position in data["positions"]:
            if not date_valide(position["date"]):
                position["date"] = date_remplacant
                position["date_approx"] = True
            else:
                position["date_approx"] = False

        for odb in data["ordre_de_bataille"]:
            odb["date"] = date_remplacant

        if not "combat" in data.keys():
            continue
        for combat in data["combat"]:
            if not date_valide(combat["date"]):
                combat["date"] = date_remplacant
                combat["date_approx"] = True
            else:
                combat["date_approx"] = False

        data["date"] = date_remplacant

    with open(output_dir/filename, "w") as f:
        json.dump(data, f)

    current_date = date_remplacant
