from django.core.management.base import BaseCommand
from carte.models import Unite, Subordonne, Commande
from tqdm import tqdm
import logging

logging.basicConfig(
    filename='fusionner_unites.log',           # Nom du fichier de log
    filemode='w',                 # 'a' pour ajouter (append), 'w' pour écraser (write)
    level=logging.INFO,           # Niveau de log minimum à enregistrer
    format='%(asctime)s - %(levelname)s - %(message)s' # Format du message de log
)

class Command(BaseCommand):


    def is_general(self, unites):
        for unite in unites:
            if unite.is_general():
                return True
        return False
    
    def get_grade(self, unites):
        dict_grade = {}
        for unite in unites:
            grade = unite.grade
            if grade is not None:
                grade = grade.lower()
            if grade in dict_grade.keys():
                dict_grade[grade] += 1
            else:
                dict_grade[grade] = 1
        return max(dict_grade, key=dict_grade.get)
    

    def get_camp(self, unites):
        dict_camp = {}
        for unite in unites:
            camp = unite.camp
            if camp =="NONE":
                continue
            if camp in dict_camp.keys():
                dict_camp[camp] += 1
            else:
                dict_camp[camp] = 1
        if len(list(dict_camp.keys()))>0:
            return max(dict_camp, key=dict_camp.get)
        return "NONE"


    def handle(self, *args, **options):

        # On fusionne toutes les unités qui sont des généraux et qui ont le même nom
        
        
        # On récupère tous les noms d'unités
        unites = set(list(Unite.objects.values_list('nom', flat=True)))
        
        # Pour chaque nom d'unité
        for nom_unite in tqdm(unites):
            # On récupère toutes les unités qui ont le même nom
            unites_noms = list(Unite.objects.filter(nom=nom_unite))

            if len(unites_noms)<2:
                continue
            
            
            # Si l'unité est un général
            if self.is_general(unites_noms):
                
                # On crée une nouvelle unité
                new_grade = self.get_grade(unites_noms)
                new_camp = self.get_camp(unites_noms)

                new_unite = Unite.objects.create(
                    nom=nom_unite,
                    grade=new_grade,
                    camp=new_camp
                )
                logging.info(f"\n On crée une nouvelle unité : {new_unite.nom}, pk = {new_unite.pk}")

                unites_delete = []
            
                # On remplace toutes les unités par la nouvelle unité
                for u in unites_noms:
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
                    unites_delete.append(u)
                
                
                
                for u in unites_delete:
                    logging.info(f"\n On supprime l'unité {u.nom}, pk = {u.pk}")
                    u.delete()
                


