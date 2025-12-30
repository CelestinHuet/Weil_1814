"""
This file is part of 1814parlescartes.

1814parlescartes is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

1814parlescartes is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with 1814parlescartes. If not, see <https://www.gnu.org/licenses/>.
"""


import json
import os
from django.core.management.base import BaseCommand
from carte.models import Unite, Position, Subordonne, Commande, Combat, Lettre, Lieu
from pathlib import Path
import datetime
from tqdm import tqdm
import logging
import difflib


logging.basicConfig(
    filename='insert_letters.log',           # Nom du fichier de log
    filemode='w',                 # 'a' pour ajouter (append), 'w' pour écraser (write)
    level=logging.INFO,           # Niveau de log minimum à enregistrer
    format='%(asctime)s - %(levelname)s - %(message)s' # Format du message de log
)

class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('--directory', type=str, help="")

    def find_unite(self, expediteur):
        if expediteur=="Alexandre":
            expediteur = "Berthier"
        unites = list(Unite.objects.filter(nom=expediteur))
        if len(unites)==1:
            logging.info(f"L'unité a été trouvée : {expediteur}")
            return unites[0]
        
        else:
            ratio_max = 0
            for general in list(Unite.objects.values_list("nom", flat=True)):
                expediteur_name = expediteur.title()
                if expediteur_name[:3]=="Le " or expediteur_name[:3]=="le ":
                    expediteur_name = expediteur_name[3:]

                
             
                ratio = difflib.SequenceMatcher(None, expediteur_name, general).ratio()
                if ratio > ratio_max:
                    ratio_max = ratio
                    general_max = general
            
            if ratio > 0.85:
                logging.info(f"L'unité a été trouvée avec un score de {ratio} : {expediteur}, {general_max}")  
                return Unite.objects.get(nom=general_max)

        logging.info(f"On crée l'unité {expediteur}")    
        return Unite.objects.create(nom=expediteur)
    

    def find_lieu(self, lieu, expediteur, date):
        if lieu == "None":
            return None
        lieux = Lieu.objects.filter(nom=lieu)
        if len(lieux)==1:
            logging.info(f"Lieu trouvé : {lieu}")
            return lieux[0]
        elif len(lieux)==0:
            return None
        
        positions_expediteurs = expediteur.positions.all()
        distance_min = 1e10
        lieu_min = None
        p_min = None
        for l in lieux:
            for p in positions_expediteurs:
                if p.lieu is None:
                    continue
                if date is not None:
                    delta = p.date - date.date()
                if (date is not None and abs(delta.days) < 5) or date is None:
                    distance = p.lieu.distance(l)
                    if distance < distance_min:
                        distance_min = distance
                        lieu_min = l
                        p_min = p
        if lieu_min is not None:
            logging.info(f"Lieu déduit : {expediteur}, {date}, {lieu_min}, {distance_min}, {p_min}")
            return lieu_min
        
        lieu_max = None
        score_max = 0
        for l in lieux:
            positions = l.position.all()
            score = 0
            for p in positions:
                if date is not None:
                    delta = p.date - date.date()
                if (date is not None and abs(delta.days) < 5) or date is None:
                    score += 1
                if score > score_max:
                    score_max = score
                    lieu_max = p
        if lieu_max is not None:
            logging.info(f"Lieu déduit : {lieu_max}, {date}, {score}")
            return lieu_max.lieu
        
        return None


    def handle_letter(self, lettre, json_file):
        date = self.convert_date(lettre["date"])
        expediteur = self.find_unite(lettre["expediteur"])
        destinataire = self.find_unite(lettre["destinataire"])
        contenu = lettre["lettre"]
        source = f"{json_file.split('_')[0]} p.{lettre['page']}"
        lieu = self.find_lieu(lettre["lieu"], expediteur, date)

        Lettre.objects.create(
            expediteur=expediteur,
            destinataire=destinataire,
            date=date,
            lieu=lieu,
            contenu=contenu,
            source=source
        )

    def convert_date(self, date):
        try:
            date_split = date.split("/")
            date_dt = datetime.datetime(
                day=int(date_split[0]),
                month=int(date_split[1]),
                year=int(date_split[2])
            )
            return date_dt
        except:
            return None

    def handle(self, *args, **options):
        directory = Path(options.get("directory"))
        json_files = [i for i in os.listdir(directory) if i[-5:]==".json"]

        
        for json_file in tqdm(json_files):
            
            with open(directory/json_file, "r") as f:
                data = json.load(f)
            
            for lettre in data["positions"]:
                self.handle_letter(lettre, json_file)