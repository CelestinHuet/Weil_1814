"""
This file is part of 1814parlescartes.

1814parlescartes is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

1814parlescartes is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with 1814parlescartes. If not, see <https://www.gnu.org/licenses/>.
"""


from django.core.management.base import BaseCommand
from carte.models import Unite
from tqdm import tqdm
import logging


logging.basicConfig(
    filename='associate_unite_camp.log',           # Nom du fichier de log
    filemode='w',                 # 'a' pour ajouter (append), 'w' pour écraser (write)
    level=logging.INFO,           # Niveau de log minimum à enregistrer
    format='%(asctime)s - %(levelname)s - %(message)s' # Format du message de log
)


class Command(BaseCommand):


    def find_allies(self, unite):

        mots_coalises = ["pruss", "autrich", "russe", "allié", "coalisé", "anglais", "wurtembergois", "suédois", "silésie", "hesse", "bavarois", "cosaque"]
        for mot_coalise in mots_coalises:
            if mot_coalise in unite.nom.lower():
                return True
        return False
    
    def find_francais(self, unite):

        mots_francais = ["français", "france", "gardes d'honneur", "garde d'honneur", "gardes d’honneur"]
        for mot_francais in mots_francais:
            if mot_francais in unite.nom.lower():
                return True
        return False


    def handle(self, *args, **options):


        generaux = [unite for unite in Unite.objects.all() if unite.is_general()]


        # On parcourt chaque unité
        for unite in tqdm(Unite.objects.all()):

            if unite.camp=="NONE":
                if self.find_allies(unite):
                    unite.camp = "COALISES"
                    unite.save()
                    logging.info(f"On associe le camp {unite.camp} à {unite}")
                elif self.find_francais(unite):
                    unite.camp = "FRANCAIS"
                    unite.save()
                    logging.info(f"On associe le camp {unite.camp} à {unite}")
                else:
                    for general in generaux:
                        if general.nom in unite.nom:
                            unite.camp = general.camp
                            unite.save()
                            logging.info(f"On associe le camp {unite.camp} à {unite} en utilisant {general}")
            if unite.camp=="NONE":
                logging.info(f"On n'est pas parvenu à associer un camp à {unite}")