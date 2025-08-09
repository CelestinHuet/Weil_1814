from django.core.management.base import BaseCommand
from carte.models import Unite, Subordonne, Commande
from tqdm import tqdm

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
        
        
        unites = set(list(Unite.objects.values_list('nom', flat=True)))
        for nom_unite in tqdm(unites):
            unites_noms = list(Unite.objects.filter(nom=nom_unite))
            
            
            if len(unites_noms)>=2:
               
                done = []
                for i in range(len(unites_noms)):
                    u0 = unites_noms[i]
                    if u0 in done:
                        continue
                    if len(u0.est_dirigee_par.all())==0:
                        continue
                    general0 = u0.est_dirigee_par.all()[0].general
                    fusion = [u0]
                    for j in range(i+1, len(unites_noms)):
                        u1 = unites_noms[j]
                        if len(u1.est_dirigee_par.all())==0:
                            continue
                        general1 = u1.est_dirigee_par.all()[0].general
                        if general0==general1:
                            fusion.append(u1)
                    
                    if len(fusion)>=2:
                        new_grade = self.get_grade(unites_noms)
                        new_camp = self.get_camp(unites_noms)

                        new_unite = Unite.objects.create(
                            nom=nom_unite,
                            grade=new_grade,
                            camp=new_camp
                        )
                    
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
                        
                        done += fusion
                        
                        for u in done:
                            u.delete()
                                
                        

                    
