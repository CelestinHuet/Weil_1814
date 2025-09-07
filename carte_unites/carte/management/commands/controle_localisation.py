import json
from tqdm import tqdm
from django.core.management.base import BaseCommand
from carte.models import Lieu, Unite


class Command(BaseCommand):

    def __init__(self):
        self.erreurs = {}

    def add_arguments(self, parser):
        parser.add_argument('--file', type=str, help="")


    def delete(self, p_remove, voisin):
        l = p_remove.lieu
        if l in self.erreurs:
            self.erreurs[l]["compte"]+=1
            if voisin not in self.erreurs[l]["voisins"]:
                self.erreurs[l]["voisins"].append(voisin)
        else:
            self.erreurs[l] = {
                "compte":1,
                "voisins":[voisin]
            }
        
        for u in p_remove.unites.all():
            u.positions.remove(p_remove)
            u.save()


    def handle(self, *args, **options):
        seuil = 90
        for unite in tqdm(Unite.objects.all()):
            
            print("")
            print(unite)

            
            unites = unite.get_equivalence()

            positions = []
            for u in unites:
                for p in u.positions.all():
                    if not p.planifie:
                        positions.append(p)

            positions = sorted(positions, key=lambda x: x.date)

            list_dict = []
            for i in range(len(positions)-1):
                p0 = positions[i]
                p1 = positions[i+1]
                l0 = p0.lieu
                l1 = p1.lieu
                if l0 is not None and l1 is not None:

                    delta = positions[i+1].date - positions[i].date
                    delta_days = delta.days
                    if delta.days == 0:
                        delta_days = 1
                    distance_moyenne = l0.distance(l1) / delta_days
                    list_dict.append({"l0":l0, "l1":l1, "distance":distance_moyenne, "p0":p0, "p1":p1})
                    print(f"{l0} - {l1} : {distance_moyenne} km")

            for i in range(1, len(list_dict)-1):
                print(list_dict[i]["distance"], seuil)
                if list_dict[i]["distance"] >= seuil and list_dict[i+1]["distance"] >= seuil:
                    if list_dict[i]["l1"]==list_dict[i+1]["l0"]:
                        self.delete(list_dict[i]["p1"], list_dict[i]["p0"])
                        
                if list_dict[i]["distance"] >= seuil and list_dict[i+1]["distance"] < seuil:
                    if list_dict[i]["l1"]==list_dict[i+1]["l0"]:
                        self.delete(list_dict[i]["p0"], list_dict[i]["p1"])

                if list_dict[i]["distance"] >= seuil and list_dict[i-1]["distance"] < seuil:
                    if list_dict[i]["l0"]==list_dict[i-1]["l1"]:
                        self.delete(list_dict[i]["p1"], list_dict[i]["p0"])

                if list_dict[i]["distance"] >= seuil:
                    if list_dict[i-1]["l1"]!=list_dict[i]["l0"] and list_dict[i]["l1"]!=list_dict[i+1]["l0"]:
                        self.delete(list_dict[i]["p1"], list_dict[i+1]["p0"])
                        self.delete(list_dict[i]["p0"], list_dict[i-1]["p1"])

        trie = dict(sorted(self.erreurs.items(), key=lambda item: item[1]["compte"], reverse=True))
        for key, value in trie.items():
            print()
            print(f"{key} : {value["compte"]}, {value["voisins"]}")

        with open("controle_localisation.json", "r") as f:
            json.dump(trie, f)
