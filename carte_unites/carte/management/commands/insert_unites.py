import json
import os
from django.core.management.base import BaseCommand
from carte.models import Unite, Position, Subordonne, Commande, Combat
from pathlib import Path
import datetime
from tqdm import tqdm
import logging


logging.basicConfig(
    filename='insert_unites.log',           # Nom du fichier de log
    filemode='w',                 # 'a' pour ajouter (append), 'w' pour écraser (write)
    level=logging.INFO,           # Niveau de log minimum à enregistrer
    format='%(asctime)s - %(levelname)s - %(message)s' # Format du message de log
)

class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('--directory', type=str, help="")


    def get_unite_from_odb(self, unite, data_odb):
        for u in data_odb:
            if u["nom_du_general"]==unite:
                return u
        return None
    

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
    

    def convert_camp(self, odb):
        camp = odb["camp"]
        if camp=="Coalition":
            return "COALISES"
        elif camp=="France":
            return "FRANCAIS"
        else:
            return "NONE"
        

    def get_or_create_unite(self, unites, nom, camp):
        for unite in unites:
            if unite.nom==nom:
                return unite, False
        u = Unite.objects.create(nom=nom, camp=camp)
        logging.info(f"On ajoute Unite {u.nom} : pk = {u.pk}")
        return u, True



    def handle(self, *args, **options):
        directory = Path(options.get("directory"))
        files = sorted([i for i in os.listdir(directory) if i[-5:]==".json"])
        for i, file in tqdm(enumerate(files)):

            #if i >= 100:
            #    break
            with open(directory/file, "r") as f:
                data = json.load(f)

            page = file.replace(".json", "").split("-")[1]
            unites_creees = []

            for odb in data["ordre_de_bataille"]:
                date_dt = self.convert_date(odb["date"])
                if date_dt is None:
                    continue
                camp = self.convert_camp(odb)
                general = Unite.objects.create(
                    nom=odb["nom_du_general"],
                    camp=camp,
                    grade=odb["grade"]
                )
                logging.info(f"On ajoute Unite {general.nom} : pk = {general.pk}")
                unites_creees.append(general)
                

                if odb["commande"]!="None" and odb["commande"]!="null" and odb["commande"] is not None:
                    unite_commandee, boolean = self.get_or_create_unite(unites_creees, odb["commande"], camp)
                    if boolean:
                        unites_creees.append(unite_commandee)
                    c = Commande.objects.create(general=general, unite_commandee=unite_commandee, date=date_dt)
                    logging.info(f"On ajoute Commande {c.pk} : {unite_commandee} {unite_commandee.pk}, {general} {general.pk}")

                
                if odb["subordonne"]!="None" and odb["subordonne"]!="null" and odb["subordonne"] is not None:
                    unite_commandant, boolean = self.get_or_create_unite(unites_creees, odb["subordonne"], camp)
                    if boolean:
                        unites_creees.append(unite_commandee)
                    s = Subordonne.objects.create(unite_commandant=unite_commandant, unite_subordonnee=general, date=date_dt)
                    logging.info(f"On ajoute Subordonne {s.pk} : {unite_commandant} {unite_commandant.pk}, {general} {general.pk}")

        
            # Pour chaque position :
            for position_dict in data["positions"]:
                if position_dict["unite"] is not None:
                    unite, boolean = self.get_or_create_unite(unites_creees, position_dict["unite"], "NONE")
                    if boolean:
                        unites_creees.append(unite)
                
                # On récupère le lieu, sous forme de str
                position_lieu = position_dict["lieu"]

                # On récupère la date
                date_position = self.convert_date(position_dict["date"])
                if date_position is None:
                    continue

                # On récupère si le mouvement est planifié ou réel
                if position_dict["planifie"]=="true":
                    position_dict["planifie"]=True
                elif position_dict["planifie"]=="false":
                    position_dict["planifie"]=False
                if not (position_dict["planifie"] == True or position_dict["planifie"] == "True" or position_dict["planifie"] == False or position_dict["planifie"] == "False"):
                    position_dict["planifie"]=True
                # On crée la position

                position = Position.objects.create(
                    lieu_str=position_lieu,
                    date=date_position,
                    planifie=position_dict["planifie"],
                    justification=position_dict["details"],
                    effectif=position_dict["effectif"],
                    source=file.replace("-", " p.").replace(".json", "")
                )
                logging.info(f"On crée la position {position.pk} : {position.lieu_str}, {unite}")
                unite.positions.add(position)
                unite.save()


            if not "combat" in data.keys():
                continue
            for combat_dict in data["combat"]:

                nom = combat_dict["nom_affrontement"]
                position_lieu = combat_dict["lieu"]
                date_combat = self.convert_date(combat_dict["date"])
                combat, created = Combat.objects.get_or_create(
                    nom=nom,
                    date=date_combat,
                    lieu_str=position_lieu
                )
                if created:
                    logging.info(f"On crée le combat {combat.pk} : {combat}")