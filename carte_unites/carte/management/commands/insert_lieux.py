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
        
        for lieu, value in tqdm(data.items()):
            if value is None:
                Lieu.objects.get_or_create(nom=lieu)
            else:
                Lieu.objects.get_or_create(nom=lieu, latitude=value["lat"], longitude=value["lon"])
