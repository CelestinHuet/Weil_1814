"""
This file is part of 1814parlescartes.

1814parlescartes is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

1814parlescartes is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with 1814parlescartes. If not, see <https://www.gnu.org/licenses/>.
"""


from django.core.management.base import BaseCommand
from carte.models import Unite
from tqdm import tqdm


class Command(BaseCommand):

    echelons = ["corps", "armée", "division", "brigade", "régiment", "bataillon", "escadron"]

    def get_echelon_from_grade(self, grade):
        if grade is None:
            return None
        for e in self.echelons:
            if e in grade.lower():
                return e
        return None


    def get_echelon_from_subordonne(self, unite:Unite):
        unites_commandees = [c.unite_commandee for c in unite.dirige.all()]

        compte_echelons = {
            "armée":0,
            "corps":0,
            "division":0,
            "brigade":0,
            "régiment":0,
            "bataillon":0,
            "escadron":0
        }

        for unite_commandee in unites_commandees:
            for echelon in compte_echelons.keys():
                if echelon in unite_commandee.nom.lower():
                    compte_echelons[echelon] += 1

        maximum = 0
        echelon = None

        for key, value in compte_echelons.items():
            if value > maximum:
                echelon = key
                maximum = value
        return echelon


    def handle(self, *args, **options):
        # On parcourt chaque unité
        for unite in tqdm(Unite.objects.all()):

            echelon = self.get_echelon_from_grade(unite.grade)

            if echelon is None:
                echelon = self.get_echelon_from_grade(unite.nom)

            if echelon is None:
                echelon = self.get_echelon_from_subordonne(unite)

            if echelon is not None:
                
                unite.echelon = echelon.replace("é", "e")
                unite.save()
            else:
                unite.echelon = "inconnu"
                unite.save()