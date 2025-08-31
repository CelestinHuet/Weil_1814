from django.core.management.base import BaseCommand
from carte.models import Lieu, Unite, Position
from tqdm import tqdm
from typing import List
from itertools import product
from math import sin, cos, acos, pi


class Voisin:

    def __init__(self, lieu_voisin, lieu_0):
        self.voisin = lieu_voisin
        self.distance = self.compute_distance(lieu_0, lieu_voisin)
        self.lieu_0 = lieu_0

    def compute_distance(self, l1, l2):

        l1_lat = l1.lat * pi / 180
        l2_lat = l2.lat * pi / 180
        l1_lon = l1.lon * pi / 180
        l2_lon = l2.lon * pi / 180

        sinus = sin(l1_lat) * sin(l2_lat)
        cosinus = cos(l1_lat) * cos(l2_lat) * cos(l1_lon - l2_lon)
        try:
            arccos = acos(sinus+cosinus)
        except:
            arccos = acos(1)
        return 6371 * arccos
    
    def update(self):
        if self.voisin.precedent is None:
            self.voisin.precedent = self.lieu_0
            self.voisin.distance = self.lieu_0.distance + self.distance
        else:
            distance = self.lieu_0.distance + self.distance
            if distance < self.voisin.distance:
                self.voisin.precedent = self.lieu_0
                self.voisin.distance = distance




class Lieu_d:

    def __init__(self, lieux:List[Lieu], position:Position):
        self.lieux = lieux
        self.voisins:List[Voisin] = []
        self.lat, self.lon = self.compute_lat_lon()
        self.position = position

        self.distance = 0
        self.precedent = None
        self.d_max = self.distance_max()

    def compute_lat_lon(self):
        lat = []
        lon = []
        for l in self.lieux:
            lat.append(l.latitude)
            lon.append(l.longitude)
        return sum(lat)/len(lat), sum(lon)/len(lon)
    
    def distance_max(self):
        d_max = 0
        for i in range(len(self.lieux)-1):
            l0 = self.lieux[i]
            l1 = self.lieux[i+1]
            d_max = max(l0.distance(l1), d_max)
        return d_max


    
    def add_voisin(self, lieu1):
        self.voisins.append(Voisin(lieu1, self))

    def __str__(self):
        return " ".join(self.lieux.__str__())
    
    def get_precedent(self):
        compte = 0
        lieu = self
        liste = [self]
        while lieu.precedent is not None:
            liste.append(lieu.precedent)
            lieu = lieu.precedent
            compte += 1
            if compte > 5000:
                print("b erreur 5000")
                break

        return reversed(liste)
        

    def set_lieu(self):
        if len(self.lieux)==1:
            self.position.lieu = self.lieux[0]
        else:
            self.position.lieu, _ = Lieu.objects.get_or_create(
                nom=self.position.lieu_str,
                latitude=self.lat,
                longitude=self.lon
            )
        self.position.save()


    

class List_Lieu_d:

    def __init__(self, positions:List[Position]):
        self.positions = positions
        self.list:List[List[Lieu_d]] = self.get_all_lieu_d()
        self.add_voisins()


    def get_all_lieu_d(self):
        """
        Créer une liste de sous-listes.
        Chaque sous-listes contient toutes les possibilités pour un seul nom de lieu
        """
        list_all = []
        for position in self.positions:
            list_lieu_d = []
            
            # Gestion des cas avec ; car il faut prendre le barycentre
            p_l_str = position.lieu_str.split(";")
            liste = []
            for p_l_str_item in p_l_str:
                liste.append(list(Lieu.objects.filter(nom=p_l_str_item)))
            combinaisons = list(product(*liste))
            for combinaison in combinaisons:
                lieu_d = Lieu_d(combinaison, position)
                if lieu_d.d_max < 100:
                    list_lieu_d.append(lieu_d)
            if len(list_lieu_d)!=0:
                list_all.append(list_lieu_d)
        return list_all


    def add_voisins(self):
        for i in range(len(self.list)-1):
            list0 = self.list[i]
            list1 = self.list[i+1]
            for lieu0 in list0:
                for lieu1 in list1:
                    lieu0.add_voisin(lieu1)


    def dikjstra(self, entree0):
        a_faire = [entree0]
        deja_fait = []

        lieu_en_cours:Lieu_d = entree0
        compte = 0
        while lieu_en_cours not in self.list[-1]:
            deja_fait.append(lieu_en_cours)
            for v in lieu_en_cours.voisins:
                v.update()
                if not v.voisin in a_faire and not v.voisin in deja_fait:
                    a_faire.append(v.voisin)
            a_faire = sorted(a_faire, key=lambda x : x.distance)
            lieu_en_cours = a_faire.pop(0)
            compte += 1
            if compte > 5000:
                print("erreur 5000")
                return None, None
        return lieu_en_cours.get_precedent(), lieu_en_cours.distance


    def find_best_trajet(self):
        parcours_min = None
        distance_min = 1e10
        if len(self.list)==0:
            return None
    
        for entree_0 in self.list[0]:
            parcours, distance = self.dikjstra(entree_0)
            if parcours is None:
                return
            if distance < distance_min:
                parcours_min = parcours
                distance_min = distance
            
            for element in self.list:
                for e in element:
                    e.distance = 0
                    e.precedent = None

        for lieu in parcours_min:
            lieu.set_lieu()




class Command(BaseCommand):


    def handle(self, *args, **options):

        done = []

        # On parcourt chaque unité
        for unite in tqdm(Unite.objects.all()):
            if unite in done:
                continue

            # L'unité doit être un général
            if not unite.is_general():
                continue
            
            # On récupère les unités sous ses ordres
            unites = unite.get_equivalence()

            # On récupère toutes les positions
            positions = []
            for u in unites:
                positions += u.positions.all()

            # On trie les positions par date
            positions = sorted(positions, key=lambda x: x.date)

            list_lieu_d = List_Lieu_d(positions)

            list_lieu_d.find_best_trajet()

            done += unites



                 
