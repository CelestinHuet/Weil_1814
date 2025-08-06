import json
import os
from django.core.management.base import BaseCommand
from carte.models import Lieu, Unite, Position, Subordonne, Commande
from pathlib import Path
import datetime
from tqdm import tqdm

class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('--directory', type=str, help="")
        parser.add_argument('--tome', type=str, help="")


    def get_unite_from_odb(self, unite, data_odb):
        for u in data_odb:
            if u["nom_du_general"]==unite:
                return u
        return None
    

    def convert_date(self, date):
        date_split = date.split("/")
        date_dt = datetime.datetime(
            day=int(date_split[0]),
            month=int(date_split[1]),
            year=int(date_split[2])
        )
        return date_dt


    def handle(self, *args, **options):
        directory = Path(options.get("directory"))
        files = [i for i in os.listdir(directory) if i[-5:]==".json"]
        for file in tqdm(files):
            with open(directory/file, "r") as f:
                data = json.load(f)

            page = file.replace(".json", "").split("-")[1]

            odb = data["ordre_de_bataille"]
        
            # Pour chaque position :
            for position_dict in data["positions"]:
                
                # On récupère l'unité
                position_unite = position_dict["unite"]
                unite, _ = Unite.objects.get_or_create(nom=position_unite)
                
                # On récupère le lieu, sous forme de str
                position_lieu = position_dict["lieu"]

                # On récupère la date
                date_position = self.convert_date(position_dict["date"])

                # On récupère si le mouvement est planifié ou réel
                if position_dict["planifie"]=="true":
                    position_dict["planifie"]=True
                if position_dict["planifie"]=="false":
                    position_dict["planifie"]=False

                # On crée la position
                position = Position.objects.create(
                    lieu_str=position_lieu,
                    date=date_position,
                    planifie=position_dict["planifie"],
                    justification=position_dict["details"],
                    effectif=position_dict["effectif"],
                    source=f"Weil T.{options.get("tome")}, p.{page}"
                )
                unite.positions.add(position)


                unite_dict = self.get_unite_from_odb(position_unite, odb)
                if unite_dict is not None:
                    camp = unite_dict["camp"]
                    if camp=="Coalition":
                        unite.camp = "COALISES"
                    elif camp=="France":
                        unite.camp = "FRANCAIS"
                    else:
                        print(camp)
                    
                    grade = unite_dict["grade"]
                    unite.grade = grade
                unite.save()

                if unite_dict is not None:
                    if unite_dict["subordonne"] is not None:
                        unite_commandant,_ = Unite.objects.get_or_create(nom=unite_dict["subordonne"])
                        date_dt = self.convert_date(unite_dict["date"])
                        subordonnee = Subordonne.objects.create(unite_commandant=unite_commandant, unite_subordonnee=unite, date=date_dt)

                    if unite_dict["commande"] is not None:
                        unite_commandee,_ = Unite.objects.get_or_create(nom=unite_dict["commande"])
                        date_dt = self.convert_date(unite_dict["date"])
                        commande = Commande.objects.create(general=unite, unite_commandee=unite_commandee, date=date_dt)




                 
