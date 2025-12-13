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


output_dir = Path("resultats_v2")
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
    "Bogdanovich_T1",
    "Bogdanovich_T2",
    "Bouvier",
    "Calmon_Maison",
    "duCasse",
    "Fabvier",
    "Foch",
    "Grouchy",
    "Hiller",
    "Koch_T1",
    "Koch_T2",
    "Marmont",
    "Mormant",
    "Petiet",
    "Plotho_T3",
    "Segur",
    "Vaudoncourt_T1",
    "Vaudoncourt_T2",
    "Weil_T1",
    "Weil_T2",
    "Weil_T3",
    "Weil_T4"
]


class Position(BaseModel):
    unite:str
    lieu:str
    details:str
    date:str
    planifie:str
    effectif:str
    page:int

    def to_dict(self):
        return {
            "unite":self.unite,
            "lieu":self.lieu,
            "details":self.details,
            "date":self.date,
            "planifie":self.planifie,
            "effectif":self.effectif,
            "page":self.page
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
    page:int

    def to_dict(self):
        return {
            "nom_affrontement":self.nom_affrontement,
            "lieu":self.lieu,
            "date":self.date,
            "details":self.details,
            "page":self.page
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


prompt = f"""
    Voici quelques images d'un texte historique sur la campagne de France de 1814 dont je veux extraire des informations.
    Lis les images dans l'ordre.

    Réponds uniquement en JSON.
    Le json doit contenir quatre champs : "positions", "date", "ordre_de_bataille" et "combat".
    Dans le champ "positions", pour chaque mouvement ou position de troupe identifié, donne un dictionnaire avec les clés :
    - "unite". Je ne veux que le nom du général de l'unité ou sinon le numéro de du corps d'armée ou de la division. Par exemple, je ne veux pas "corps de Sacken" mais "Sacken". Si le texte n'est pas en français, met la réponse en français. Par exemple, "1. leichte Divifion" devient "1ère division légère"
    - "lieu". Si l'unité se trouve entre deux villes, mets un point-virgule entre les deux noms de ville. Si l'unité se trouve dans deux villes différentes à la fois, crée deux dictionnaires. Je ne veux que des noms de localités, pas de localisation vague comme "dans ses cantonnements" ou "le long du fleuve". Je ne veux pas non plus de noms de pays, de région ou de cours d'eau, mais seulement des noms de ville, village ou hameau.
    - "details". Cite la phrase complète qui justifie ce mouvement de troupe. Je ne veux pas un extrait de phrase, mais bien la phrase complète. Si cette phrase n'est pas en français, ajoute entre parenthèses la traduction en français.
    - "date". Si la date n'est pas précisée, mets None. La date doit être de la forme jj/mm/aaaa. Si l'année n'est pas précisée, sache que les dates sont comprises entre décembre 1813 et mai 1814. 
    - "planifie". Je veux True ou False, mais rien d'autres. Ce doit être True dans le cas où c'est un mouvement planifié mais qui n'a pas été encore réalisé.
    - "effectif". Si l'effectif n'est pas précisé, mets None. Si le texte n'est pas en français, met la réponse en français
    - "page". Le numéro de la page de l'ouvrage où tu as trouvé l'information
    Liste-les dans une liste JSON.

    Dans le champ "date", il peut exister en tête d'un paragraphe la mention d'une date. Indique-là sous la forme jj/mm/aaaa. Si l'année n'est pas précisée, sache que les dates sont comprises entre décembre 1813 et mai 1814. Par exemple, si en début de paragraphe il y a "11 Janvier. —", mets 11/01/1814
    
    Dans le champ "ordre_de_bataille", pour chaque général, identifie :
    - "nom_du_general"
    - "grade" : grade ou fonction (ex. général de division, maréchal, commandant en chef, etc.). Si le texte n'est pas en français, met la réponse en français
    - "commande" : ce qu’il commande (ex. 1er corps d’armée, 3e division, réserve de cavalerie, etc.). Si le texte n'est pas en français, met la réponse en français
    - "subordonne" : s’il est subordonné à un supérieur, indique le nom de ce supérieur ou l'unité commandée par ce supérieur. Si le texte n'est pas en français, met la réponse en français
    - "camp" : Répond soit par "France", soit par "Coalition", soit par "None" si tu ne sais pas. Utilise en priorité le texte. Tu as le droit d'utiliser tes connaissances sur la Campagne de France de 1814. Pour rappel, "Coalition" regroupe les forces coalisées opposées à Napoléon (russes, prussiens, autrichiens, bavarois, wurtembourgeois, saxons, suédois...) 
    IMPORTANT : ta réponse doit être un JSON **valide**. Pas d'explications ni de texte hors JSON.

    Dans le champ "combat", pour chaque combat ou bataille (je ne veux pas d'engagements mineurs comme une escarmouche, ni de terme trop générique comme invasion) entre deux armées ennemies, identifie :
    - "nom_affrontement". Si le texte n'est pas en français, met la réponse en français
    - "date". Si la date n'est pas précisée, mets None. La date doit être de la forme jj/mm/aaaa. Si l'année n'est pas précisée, sache que les dates sont comprises entre décembre 1813 et mai 1814. 
    - "lieu". Si l'affrontement se déroule dans plusieurs lieux, mets un point-virgule entre les noms de lieux. Je ne veux que des noms de localités, pas de localisation vague comme "dans ses cantonnements" ou "le long du fleuve". Je ne veux pas non plus de noms de pays, de région ou de cours d'eau, mais seulement des noms de ville, village ou hameau.
    - "details". Cite la phrase complète qui justifie ce combat ou cette bataille. Je ne veux pas un extrait de phrase, mais bien la phrase complète. Si cette phrase n'est pas en français, ajoute entre parenthèses la traduction en français.
    - "page". Le numéro de la page de l'ouvrage où tu as trouvé l'information
    """

nb_requetes = 0

nb_images = 3

for directory in directories:
    images = sorted([i for i in os.listdir(directory) if i[-4:]==".png"])
    for i in tqdm(range(0, len(images), nb_images)):
        output_file = f"{directory}_{i}_{i+nb_images+1}.json"
        if os.path.exists(output_dir/output_file):
            continue

        if nb_requetes>51:
            break

        data = get_images(Path(directory), images[i:i+nb_images+1])

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
        

        
