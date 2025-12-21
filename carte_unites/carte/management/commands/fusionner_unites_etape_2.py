"""
This file is part of 1814parlescartes.

1814parlescartes is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

1814parlescartes is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with 1814parlescartes. If not, see <https://www.gnu.org/licenses/>.
"""


from django.core.management.base import BaseCommand
from carte.models import Unite, Subordonne, Commande
from tqdm import tqdm

import logging

logging.basicConfig(
    filename='fusionner_etape_2.log',           # Nom du fichier de log
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

        # On fusionne toutes les unités qui ont le même nom et qui sont commandées par le même général
        
        
        # On récupère tous les noms d'unités
        unites = set(list(Unite.objects.values_list('nom', flat=True)))

        delete = []
        
        # Pour chaque nom d'unité
        for nom_unite in tqdm(unites):

            # On récupère toutes les unités qui ont le même nom
            unites_noms = list(Unite.objects.filter(nom=nom_unite))
            
            
            # S'il y en a au moins deux
            if len(unites_noms)>=2:
               
                # On parcourt toutes les unités qui ont le même nom et on regarde celles qui sont commandées par le même général
                done = []
                for i in range(len(unites_noms)):
                    
                    # On récupère l'unité i si elle n'a pas déjà été faite
                    u0 = unites_noms[i]
                    if u0 in done:
                        continue
                    # Si on n'a pas d'informations sur le général qui dirige cette unité, on passe
                    if len(u0.est_dirigee_par.all())==0:
                        continue
                    
                    # On récupère le général de l'unité
                    general0 = u0.est_dirigee_par.all()[0].general
                    fusion = [u0]
                    
                    # On parcourt toutes les unités suivantes
                    for j in range(i+1, len(unites_noms)):
                        # Si elles ont le même général, alors on va les fusionner
                        u1 = unites_noms[j]
                        if len(u1.est_dirigee_par.all())==0:
                            continue
                        general1 = u1.est_dirigee_par.all()[0].general
                        if general0==general1:
                            fusion.append(u1)
                    
                    if len(fusion)>=2:
                        new_grade = self.get_grade(fusion)
                        new_camp = self.get_camp(fusion)

                        new_unite = Unite.objects.create(
                            nom=nom_unite,
                            grade=new_grade,
                            camp=new_camp
                        )
                        logging.info(f"\n On crée une nouvelle unité : {new_unite.nom}, pk = {new_unite.pk}")

                        print(f"On fusionne {fusion}. La nouvelle unité est {new_unite}")
                    
                        for u in fusion:
                            for p in u.positions.all():
                                new_unite.positions.add(p)
                            new_unite.save()
                            print(new_unite, new_unite.positions.all())

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
                        
                        done += fusion
                        delete += fusion
                        
        for u in delete:
            logging.info(f"\n On supprime l'unité {u.nom}, pk = {u.pk}")
            u.delete()