from django.core.management.base import BaseCommand
from carte.models import Unite, Subordonne, Commande
import difflib
import logging
from tqdm import tqdm
from typing import List

logging.basicConfig(
    filename='fusionner_unites_1bis.log',           # Nom du fichier de log
    filemode='w',                 # 'a' pour ajouter (append), 'w' pour écraser (write)
    level=logging.INFO,           # Niveau de log minimum à enregistrer
    format='%(asctime)s - %(levelname)s - %(message)s' # Format du message de log
)



class UniteVoisin:

    def __init__(self, unite:Unite):
        self.unite = unite
        self.voisins:List[UniteVoisin] = []
        self.done = False

    def add(self, voisin:Unite):
        self.voisins.append(voisin)


    def __str__(self):
        return self.unite.nom


class Command(BaseCommand):

    """
    On regroupe les généraux qui ont presque le même nom
    """    

    def add(self, appariements, unite_i, unite_j):
        logging.info(f"On ajoute {unite_i.nom} et {unite_j.nom}")
        for appariement in appariements:
            if unite_i in appariement:
                appariement.append(unite_j)
                return appariements
            elif unite_j in appariement:
                appariement.append(unite_i)
                return appariements
        appariements.append([unite_i, unite_j])
        return appariements
    

    def get_all_voisins(self, unite:UniteVoisin):
        a_visiter = [unite]
        done = []
        appariements = []
        
        while len(a_visiter)>0:
            v = a_visiter.pop()
            for voisin in v.voisins:
                if voisin not in a_visiter and voisin not in done:
                    a_visiter.append(voisin)
            appariements.append(v)
            done.append(v)
        return appariements



    def handle(self, *args, **options):

        unites = Unite.objects.all()
        unites_voisins:List[UniteVoisin] = []

        for unite in tqdm(unites):
            unites_voisins.append(UniteVoisin(unite))
        
        for i in tqdm(range(len(unites_voisins))):
            unite_i = unites_voisins[i]
            for j in range(i+1, len(unites_voisins)):
                unite_j = unites_voisins[j]
                ratio = difflib.SequenceMatcher(None, unite_i.unite.nom, unite_j.unite.nom).ratio()
                if ratio > 0.9:
                    unite_i.add(unite_j)
                    unite_j.add(unite_i)
            #if i > 5:
            #    break

        appariements = []
        for unite in unites_voisins:
            if not unite.done:
                appariement = self.get_all_voisins(unite)
                if len(appariement)>=2:
                    for u in appariement:
                        u.done = True
                    appariements.append(appariement)
        
        for appariement in tqdm(appariements):
            print(appariement[0].unite.nom, len(appariement))
            logging.info("")
            maximum = 0
            unite_max = appariement[0].unite
            for unite in appariement:
                nb_positions = len(unite.unite.positions.all())
                if nb_positions > maximum:
                    maximum = nb_positions
                    unite_max = unite.unite
                logging.info(f"{unite} : {len(unite.unite.positions.all())}")

            new_unite = Unite.objects.create(
                    nom=unite_max.nom,
                    grade=unite_max.grade,
                    camp=unite_max.camp
                )
            logging.info(f"\n On crée une nouvelle unité : {new_unite.nom}, pk = {new_unite.pk}")
        
            # On remplace toutes les unités par la nouvelle unité
            for un in appariement:
                u = un.unite
                for p in u.positions.all():
                    new_unite.positions.add(p)
                new_unite.save()
                subordonnee = Subordonne.objects.filter(unite_commandant=u)
                for s in subordonnee:
                    s.unite_commandant = new_unite
                    s.save()
                subordonnee = Subordonne.objects.filter(unite_subordonnee=u)
                for s in subordonnee:
                    s.unite_subordonnee = new_unite
                    s.save()
                commande = Commande.objects.filter(general=u)
                for c in commande:
                    c.general = new_unite
                    c.save()
                commande = Commande.objects.filter(unite_commandee=u)
                for c in commande:
                    c.unite_commandee = new_unite
                    c.save()
            for un in appariement:
                u = un.unite
                logging.info(f"On supprime l'unité {u.nom}, pk = {u.pk}")
                u.save()
                u.delete()

        logging.info(f"Nombre d'unités restantes : {len(Unite.objects.all())}")