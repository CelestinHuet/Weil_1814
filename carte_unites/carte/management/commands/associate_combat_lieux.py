"""
This file is part of 1814parlescartes.

1814parlescartes is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

1814parlescartes is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with 1814parlescartes. If not, see <https://www.gnu.org/licenses/>.
"""


from django.core.management.base import BaseCommand
from carte.models import Lieu, Combat
from tqdm import tqdm
import logging

logging.basicConfig(
    filename='associate_combat_lieux.log',           # Nom du fichier de log
    filemode='w',                 # 'a' pour ajouter (append), 'w' pour écraser (write)
    level=logging.INFO,           # Niveau de log minimum à enregistrer
    format='%(asctime)s - %(levelname)s - %(message)s' # Format du message de log
)


class Command(BaseCommand):


    def handle(self, *args, **options):

        # On parcourt chaque unité
        for combat in tqdm(Combat.objects.all()):

            lieux = Lieu.objects.filter(nom=combat.lieu_str)
            
            if len(lieux)==0:
                continue

            nb_max = -1
            lieu_max = lieux[0]

            for lieu in lieux:
                nb = len(lieu.position.all())
                if nb > nb_max:
                    nb_max = nb
                    lieu_max = lieu
            
            combat.lieu = lieu_max
            combat.save()
            logging.info(f"On associe {lieu_max} à {combat}")








                 
