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
   
   
    with open(input_dir/input_file, "r") as f:
        contents = f.read()
        
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash", 
            contents=contents,
            config={
                "response_mime_type": "application/json",
                "response_schema": Schema,
            },
        )
    except:
        time.sleep(60)
    
    
    with open(output_file_path, "w") as f:
        json.dump(response.parsed.to_dict(), f)


    time.sleep(10)

    nb_requetes += 1
    if nb_requetes>240:
        break