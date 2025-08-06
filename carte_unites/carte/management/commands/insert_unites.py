import json
import os
from django.core.management.base import BaseCommand
from carte.models import Lieu, Unite, Position
from pathlib import Path
import datetime
from tqdm import tqdm

class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('--directory', type=str, help="")
        parser.add_argument('--tome', type=str, help="")

    def handle(self, *args, **options):
        directory = Path(options.get("directory"))
        files = [i for i in os.listdir(directory) if i[-5:]==".json"]
        for file in tqdm(files):
            with open(directory/file, "r") as f:
                data = json.load(f)

            page = file.replace(".json", "").split("-")[1]
        
            for position_dict in data["positions"]:
                position_unite = position_dict["unite"]
                unite, _ = Unite.objects.get_or_create(nom=position_unite)
                position_lieu = position_dict["lieu"]

                lieu = list(Lieu.objects.filter(nom=position_lieu))[0]
                date_position_str = position_dict["date"].split("/")
                date_position = datetime.datetime(
                    day=int(date_position_str[0]),
                    month=int(date_position_str[1]),
                    year=int(date_position_str[2])
                )

                if position_dict["planifie"]=="true":
                    position_dict["planifie"]=True
                if position_dict["planifie"]=="false":
                    position_dict["planifie"]=False

                position = Position.objects.create(
                    lieu=lieu,
                    date=date_position,
                    planifie=position_dict["planifie"],
                    justification=position_dict["details"],
                    effectif=position_dict["effectif"],
                    source=f"Weil T.{options.get("tome")}, p.{page}"
                )
                unite.positions.add(position)
                unite.save()

                 
