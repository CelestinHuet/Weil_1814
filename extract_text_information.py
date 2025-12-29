"""
This file is part of 1814parlescartes.

1814parlescartes is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

1814parlescartes is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with 1814parlescartes. If not, see <https://www.gnu.org/licenses/>.
"""


from google import genai
from pathlib import Path
import os
from tqdm import tqdm
import json
import time
from pydantic import BaseModel
from typing import List

# The client gets the API key from the environment variable `GEMINI_API_KEY`.
client = genai.Client()


input_dir = Path("prompts")
output_dir =  Path("resultats")




class Position(BaseModel):
    unite:str
    lieu:str
    details:str
    date:str
    planifie:str
    effectif:str

    def to_dict(self):
        return {
            "unite":self.unite,
            "lieu":self.lieu,
            "details":self.details,
            "date":self.date,
            "planifie":self.planifie,
            "effectif":self.effectif
        }
    

class OrdreBataille(BaseModel):
    nom_du_general:str
    grade:str
    commande:str
    subordonne:str
    camp:str

    def to_dict(self):
        return {
            "nom_du_general":self.nom_du_general,
            "grade":self.grade,
            "commande":self.commande,
            "subordonne":self.subordonne,
            "camp":self.camp,
        }
    

class Combat(BaseModel):
    nom_affrontement:str
    date:str
    lieu:str
    details:str

    def to_dict(self):
        return {
            "nom_affrontement":self.nom_affrontement,
            "lieu":self.lieu,
            "date":self.date,
            "details":self.details
        }


class Schema(BaseModel):
    positions:List[Position]
    date:str
    ordre_de_bataille:List[OrdreBataille]
    combat:List[Combat]

    def to_dict(self):

        return {
            "positions":[p.to_dict() for p in self.positions],
            "date":self.date,   
            "ordre_de_bataille":[ob.to_dict() for ob in self.ordre_de_bataille],
            "combat":[ob.to_dict() for ob in self.combat]
        }


input_files = sorted([i for i in os.listdir(input_dir) if i[-4:]==".txt"])

nb_requetes = 0

for input_file in tqdm(input_files):

    output_file = input_file.replace(".txt", ".json")
    output_file_path = output_dir/output_file
    if os.path.isfile(output_file_path):
        continue

    if "Hiller" in input_file:
        continue
   
    with open(input_dir/input_file, "r") as f:
        contents = f"request id : {output_file} \n Timestamp : {time.time()}" + f.read()

    nb_requetes += 1
    if nb_requetes>251:
        break
        
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash", 
            contents=contents,
            config={
                "response_mime_type": "application/json",
                "response_schema": Schema,
                "temperature":0.0,
            },
        )
    except Exception as e:
        print(e)
        time.sleep(60)
        continue
    
    
    if response.parsed is not None:
        print(f"Réussi : {output_file}")
        with open(output_file_path, "w") as f:
            json.dump(response.parsed.to_dict(), f)
    else:
        print(f"response.parsed is None : {output_file}")
        print(response)
        print(response.text)
        print(response.candidates[0].content.parts)

    time.sleep(30)
