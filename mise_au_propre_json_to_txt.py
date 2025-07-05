import json
import os


input = "resultats_mise_au_propre"
os.makedirs(os.path.join(input, "corps"), exist_ok=True)
os.makedirs(os.path.join(input, "notes"), exist_ok=True)
fichiers_json = [i for i in os.listdir(input) if i[-5:]==".json"]

for file in fichiers_json:
    with open(os.path.join(input, file), "r") as f:
        data = json.load(f)

        file_txt = file.replace(".json", ".txt")

        with open(os.path.join(input, "corps", file_txt), "w") as f:
            f.write(data["corps"])

        with open(os.path.join(input, "notes", file_txt), "w") as f:
            f.write(data["notes"])