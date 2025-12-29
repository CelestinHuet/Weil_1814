"""
This file is part of 1814parlescartes.

1814parlescartes is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

1814parlescartes is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with 1814parlescartes. If not, see <https://www.gnu.org/licenses/>.
"""


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