"""
This file is part of 1814parlescartes.

1814parlescartes is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

1814parlescartes is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with 1814parlescartes. If not, see <https://www.gnu.org/licenses/>.
"""


import json
import os
from django.core.management.base import BaseCommand
from carte.models import Unite, Position, Subordonne, Commande, Combat
from pathlib import Path
import datetime
from tqdm import tqdm
import logging
from django.db.models import F, Value
from django.db.models.functions import Substr, StrIndex


logging.basicConfig(
    filename='statistiques.log',           # Nom du fichier de log
    filemode='w',                 # 'a' pour ajouter (append), 'w' pour écraser (write)
    level=logging.INFO,           # Niveau de log minimum à enregistrer
    format='%(asctime)s - %(levelname)s - %(message)s' # Format du message de log
)

class Command(BaseCommand):

    def add_arguments(self, parser):
        pass


    def handle(self, *args, **options):

        positions = Position.objects.all()
        logging.info(f"Nombre de positions : {len(positions)}")

        positions_fiables = Position.objects.filter(date_approx=False,planifie=False)
        logging.info(f"Nombre de positions fiables : {len(positions_fiables)}")
        
        qs = Position.objects.annotate(
            source_prefix=Substr(
                F('source'),
                1,
                StrIndex(F('source'), Value('_')) - 1
            )
        )
        sources = sorted(set(list(qs.values_list('source_prefix', flat=True))))
        print(sources)

        for source in sources:
            filtered = qs.filter(source_prefix=source,date_approx=False,planifie=False)
            filtered_total = qs.filter(source_prefix=source)
            filtered_dates_incertaines = qs.filter(source_prefix=source,date_approx=True)
            filtered_planifie = qs.filter(source_prefix=source,planifie=True)
            logging.info(f"{source} : total : {len(filtered_total)}, date incertaine : {len(filtered_dates_incertaines)}, planifié : {len(filtered_planifie)}, fiable : {len(filtered)}")
            

        unites = Unite.objects.all()
        logging.info(f"Nombre d'unités : {len(unites)}")
        generaux = [u for u in unites if u.is_general()]
        logging.info(f"Nombre de généraux : {len(generaux)}")