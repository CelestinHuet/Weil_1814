from django.core.management.base import BaseCommand
from carte.models import Unite, Subordonne, Commande
import difflib
import logging

logging.basicConfig(
    filename='fusionner_unites_1bis.log',           # Nom du fichier de log
    filemode='w',                 # 'a' pour ajouter (append), 'w' pour écraser (write)
    level=logging.INFO,           # Niveau de log minimum à enregistrer
    format='%(asctime)s - %(levelname)s - %(message)s' # Format du message de log
)

class Command(BaseCommand):

    """
    On regroupe les généraux qui ont presque le même nom
    """
    

    def detecter_ressemblance(self):
        unites_general = []
        unites = Unite.objects.all()
        for unite in unites:
            if unite.is_general():
                unites_general.append(unite)
        

        for i in range(len(unites_general)):
            unite_0 = unites_general[i]
            for j in range(i+1, len(unites_general)):
                unite_1 = unites_general[j]
                ratio = difflib.SequenceMatcher(None, unite_0.nom, unite_1.nom).ratio()
                if ratio > 0.9:
                    positions_0 = len(unite_0.positions.all())
                    positions_1 = len(unite_1.positions.all())
                    print("")
                    print(f"{unite_0.nom} - {unite_1.nom} : {ratio}")
                    if positions_0 > positions_1:
                        print(f"On remplace {unite_1.nom} par {unite_0.nom} : {positions_0} - {positions_1}")
                        return True, unite_1, unite_0
                    else:
                        print(f"On remplace {unite_0.nom} par {unite_1.nom} : {positions_0} - {positions_1}")
                        return True, unite_0, unite_1
        return False, None, None



    def handle(self, *args, **options):

        
        changement = True
        while changement:

            changement, unite_remplacee, unite_remplacant = self.detecter_ressemblance()
            if changement:
                unites_noms = [unite_remplacee, unite_remplacant]

                new_unite = Unite.objects.create(
                    nom=unite_remplacant.nom,
                    grade=unite_remplacant.grade,
                    camp=unite_remplacant.camp
                )
                logging.info(f"\n On crée une nouvelle unité : {new_unite.nom}, pk = {new_unite.pk}")
            
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

                logging.info(f"\n On supprime l'unité {unite_remplacee.nom}, pk = {unite_remplacee.pk}")
                logging.info(f"\n On supprime l'unité {unite_remplacant.nom}, pk = {unite_remplacant.pk}")
                unite_remplacee.delete()
                unite_remplacant.delete()
                