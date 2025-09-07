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
        return echelon, compte_echelons


    def handle(self, *args, **options):
        # On parcourt chaque unité
        for unite in tqdm(Unite.objects.all()):

            # L'unité doit être un général
            if not unite.is_general():
                continue

            echelon = self.get_echelon_from_grade(unite.grade)

            if echelon is None:
                echelon = self.get_echelon_from_subordonne(unite)

            if echelon is not None:
                unite.echelon = echelon
                unite.save()