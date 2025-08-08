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
        
        for lieu in tqdm(data):
            Lieu.objects.get_or_create(nom=lieu["lieu"], latitude=lieu["lat"], longitude=lieu["lon"])
