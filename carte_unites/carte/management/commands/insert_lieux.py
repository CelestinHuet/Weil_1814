"""
This file is part of 1814parlescartes.

1814parlescartes is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

1814parlescartes is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with 1814parlescartes. If not, see <https://www.gnu.org/licenses/>.
"""


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
