"""
This file is part of 1814parlescartes.

1814parlescartes is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

1814parlescartes is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with 1814parlescartes. If not, see <https://www.gnu.org/licenses/>.
"""


import os
from pathlib import Path
from google import genai
from tqdm import tqdm
import json
import time
from pydantic import BaseModel
from typing import List
from google.genai.types import Part
from google.genai import types


output_dir = Path("lettres")
os.makedirs(output_dir, exist_ok=True)


http_options = types.HttpOptions(timeout=240000)
# The client gets the API key from the environment variable `GEMINI_API_KEY`.
client = genai.Client(http_options=http_options)


def get_images(directory, images):
    liste = []
    for image in images:
        with open(directory/image, 'rb') as f:
            liste.append(Part.from_bytes(
                data= f.read(),
                mime_type='image/png'  # Assurez-vous que le MIME type correspond au fichier
            ))
    return liste



directories = [
    ["Grouchy",1,147],
    ["Marmont",10,365],
    ["Petiet", 93, 106]
]


class Lettre(BaseModel):
    expediteur:str
    destinataire:str
    lieu:str
    lettre:str
    date:str
    page:int

    def to_dict(self):
        return {
            "expediteur":self.expediteur,
            "destinataire":self.destinataire,
            "lieu":self.lieu,
            "lettre":self.lettre,
            "date":self.date,
            "page":self.page
        }


class Schema(BaseModel):
    lettres:List[Lettre]

    def to_dict(self):

        return {
            "positions":[l.to_dict() for l in self.lettres]
        }


def get_images_list(directory):
    images = []
    directory_name = directory[0]
    begin = directory[1]
    end = directory[2]
    for file in os.listdir(directory_name):
        if file[-4:]==".png":
            page_number = int(file.replace(".png", "").split("-")[1])
            if page_number>=begin and page_number<=end:
                images.append(file)
    return sorted(images)

prompt = f"""
    Voici quelques images d'un texte historique sur la campagne de France de 1814. On y trouve parfois, en tant que pièces que pièces justificatives, des reproductions des lettres d'époques.
    Je veux que tu extraits ces lettres en format json pour que je puisse ensuite les exploiter.
    Lis les images dans l'ordre.

    Réponds uniquement en JSON.
    Le json doit contenir un champ : "lettres".
    Dans le champ "lettres", pour chaque lettre historique identifiée, donne un dictionnaire avec les clés :
    - "expediteur". Je veux le nom du général qui a expédié la lettre.
    - "destinataire". Je veux le nom du général destinataire de la lettre
    - "lieu". Je veux le lieux où a été écrite la lettre. Je veux seulement le nom de la localité, pas de déterminant comme "de" qui précède le nom de la localité
    - "lettre". Cite la lettre dans son intégralité. Si cette phrase n'est pas en français, ajoute entre parenthèses la traduction en français.
    - "date". Je veux la date où la lettre a été écrite. La date doit être de la forme jj/mm/aaaa. Si l'année n'est pas précisée, sache que les dates sont comprises entre décembre 1813 et mai 1814. 
    - "page". Le numéro de la page de l'ouvrage où tu as trouvé l'information
    Liste-les dans une liste JSON. Pour chaque champ, si tu ne parviens pas à trouver l'information, mets "None".
    """

nb_requetes = 0

nb_images = 3

for directory in directories:
    directory_name = directory[0]
    
    images = get_images_list(directory)
    for i in tqdm(range(0, len(images), nb_images)):
        output_file = f"{directory_name}_{i}_{i+nb_images+1}.json"
        if os.path.exists(output_dir/output_file):
            continue

        if nb_requetes>51:
            break

        data = get_images(Path(directory_name), images[i:i+nb_images+1])

        contents = [prompt] + data
        nb_requetes += 1
        try:
            response = client.models.generate_content(
                model="gemini-2.5-pro", 
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
        
        usage = response.usage_metadata
        print(f"Nombre de jetons dans le prompt (input): {usage.prompt_token_count}")
        print(f"Nombre de jetons générés (output): {usage.candidates_token_count}")
        print(f"Nombre total de jetons utilisés: {usage.total_token_count}")
        if usage.prompt_token_count < 200000:
            cout_input = usage.prompt_token_count / 1000000 * 1.25
        else:
            cout_input = usage.prompt_token_count / 1000000 * 2.5

        if usage.candidates_token_count < 200000:
            cout_output = usage.candidates_token_count / 1000000 * 10
        else:
            cout_output = usage.candidates_token_count / 1000000 * 15.0

        print("cout entrée : ", cout_input)
        print("cout sortie : ", cout_output)
        print("cout_total : ", cout_input+cout_output)
        

        
        time.sleep(60)
        if response.parsed is not None:
            print(f"Réussi : {output_file}")
            with open(output_dir/output_file, "w") as f:
                json.dump(response.parsed.to_dict(), f)
        else:
            print(f"response.parsed is None : {output_file}")
            print(response)
            print(response.text)
            #print(response.candidates[0].content.parts)
        

        
