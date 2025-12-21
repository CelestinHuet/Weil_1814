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

# The client gets the API key from the environment variable `GEMINI_API_KEY`.
client = genai.Client()


input_dir = Path("prompts_mise_au_propre")
output_dir =  Path("resultats_mise_au_propre")

class Schema(BaseModel):
    corps:str
    notes:str

    def to_dict(self):
        return {
            "corps":self.corps,
            "notes":self.notes
        }


input_files = sorted([i for i in os.listdir(input_dir) if i[-4:]==".txt"])

nb_requetes = 0

for input_file in tqdm(input_files):

    output_file = input_file.replace(".txt", ".json")
    output_file_path = output_dir/output_file
    if os.path.isfile(output_file_path):
        continue
   
   
    print(input_file)
    with open(input_dir/input_file, "r") as f:
        contents = f.read()

    nb_requetes += 1
    if nb_requetes>251:
        break
        
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash", 
            #model="gemini-2.5-pro", 
            contents=contents,
            config={
                "response_mime_type": "application/json",
                "response_schema": Schema,
            },
        )
    except Exception as e:
        print(e)
        time.sleep(60)
        continue
    
    
    with open(output_file_path, "w") as f:
        json.dump(response.parsed.to_dict(), f)


    time.sleep(10)
