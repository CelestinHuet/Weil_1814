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
        files = os.listdir(directory)
        for file in files:
            with open(directory/file, "r") as f:
                data = json.load(f)

            page = os.path.basename(file).split("-")[1]
        
            for position_dict in tqdm(data["positions"]):
                position_unite = position_dict["unite"]
                unite, _ = Unite.objects.get_or_create(nom=position_unite)
                position_lieu = position_dict["lieu"]

                lieu = Lieu.objects.get(nom=position_lieu)
                date_position_str = position_dict["date"].split("/")
                date_position = datetime.datetime(
                    day=int(date_position_str[0]),
                    month=int(date_position_str[1]),
                    year=int(date_position_str[2])
                )

                position = Position.objects.create(
                    lieu=lieu,
                    date=date_position,
                    planifie=position_dict["planifié"],
                    justification=position_dict["details"],
                    effectif=position_dict["effectif"],
                    source=f"Weil T.{options.get("tome")}, p.{page}"
                )
                unite.positions.add(position)
                unite.save()

                 
