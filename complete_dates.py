from pathlib import Path
import os
import json




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
        return True

    except:
        return False

input_dir = Path("resultats/")
output_dir = Path("resultats/gemini_2-5_dates_corrected")

json_files = [[i, int(i.replace(".json", "").split("-")[1])] for i in os.listdir(input_dir) if i[-5:]==".json"]
json_files.sort(key=lambda x: x[1])
current_date = "01/12/1813"
for json_file in sorted(json_files):
    with open(input_dir/json_file[0], "r") as f:
        data = json.load(f)
    for position in data["positions"]:
        if not date_valide(position["date"]):
            position["date"] = current_date

    
    
    os.makedirs(output_dir, exist_ok=True)
    with open(output_dir/json_file[0], "w") as f:
        json.dump(data, f)

    if date_valide(data["date"]):
        current_date = data["date"]