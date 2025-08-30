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

for i in range(len(list_dates)-5):
    d0 = list_dates[i]
    if d0["nouvelle_date"] is not None:
        continue
    if not date_valide(d0["date"]):
        continue
    for j in range(5, 0, -1):
        if list_dates[i+j]["date"]==d0["date"]:
            break
    for k in range(1, j):
        if list_dates[i+k]["date"]!=d0["date"] and list_dates[i+k]["nouvelle_date"] is None:
            print(f"Dans {list_dates[i+k]["file"]}, on remplace {list_dates[i+k]["date"]} par {d0["date"]}")
            list_dates[i+k]["nouvelle_date"] = d0["date"]


current_date = "01/12/1813"
for element in list_dates:
    filename = element["file"][0]
    with open(input_dir/filename, "r") as f:
        data = json.load(f)

        if date_valide(element["nouvelle_date"]):
            date_remplacant = element["nouvelle_date"]
        elif date_valide(element["date"]):
            date_remplacant = element["date"]
        else:
            date_remplacant = current_date

        print(filename, date_remplacant)
        for position in data["positions"]:
            if not date_valide(position["date"]):
                position["date"] = current_date

        for odb in data["ordre_de_bataille"]:
            odb["date"] = current_date

    with open(output_dir/filename, "w") as f:
        json.dump(data, f)

    current_date = date_remplacant
