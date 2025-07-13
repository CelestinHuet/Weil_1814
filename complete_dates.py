from pathlib import Path
import os
import json


input_dir = Path("resultats/gemini_2-5_dates")
output_dir = Path("resultats/gemini_2-5_dates_corrected")

json_files = [[i, int(i.replace(".json", "").split("-")[1])] for i in os.listdir(input_dir) if i[-5:]==".json"]
json_files.sort(key=lambda x: x[1])
current_date = "10/01/1814"
for json_file in sorted(json_files):
    with open(input_dir/json_file[0], "r") as f:
        data = json.load(f)
    for position in data["positions"]:
        if position["date"] is None:
            position["date"] = current_date
    
    os.makedirs(output_dir, exist_ok=True)
    with open(output_dir/json_file[0], "w") as f:
        json.dump(data, f)