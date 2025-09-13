import json
from tqdm import tqdm
from django.core.management.base import BaseCommand
from carte.models import Lieu


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('--file', type=str, help="")

    def handle(self, *args, **options):
        file = options.get("file")
        with open(file, "r") as f:
            data = json.load(f)


        removed_list = [
            "null",
            "France",
            "rive gauche",
            "Pont",
            "Moselle",
            "Marne",
            "Aube",
            "Sambre",
            "Meuse",
            "Rhin",
            "Seine"
        ]
        
        for lieu in tqdm(data):
            if not lieu["lieu"] in removed_list:
                Lieu.objects.get_or_create(nom=lieu["lieu"], latitude=lieu["lat"], longitude=lieu["lon"])
