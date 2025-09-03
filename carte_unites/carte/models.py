from django.db import models
from math import acos, cos, sin, pi

class Lieu(models.Model):
    nom = models.CharField(max_length=100)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)

    def __str__(self):
        return self.nom
    
    def distance(self, l2):
        l1_lat = self.latitude * pi / 180
        l2_lat = l2.latitude * pi / 180
        l1_lon = self.longitude * pi / 180
        l2_lon = l2.longitude * pi / 180
        sinus = sin(l1_lat) * sin(l2_lat)
        cosinus = cos(l1_lat) * cos(l2_lat) * cos(l1_lon - l2_lon)
        try:
            arccos = acos(sinus+cosinus)
        except:
            arccos = acos(1)
        return 6371 * arccos


class Position(models.Model):
    lieu = models.ForeignKey(Lieu, on_delete=models.CASCADE, blank=True, null=True, related_name="position")
    lieu_str = models.CharField(max_length=300, blank=True, null=True)
    date = models.DateField()
    planifie = models.BooleanField(default=False)
    justification = models.TextField(blank=True, null=True)
    effectif = models.CharField(max_length=100, blank=True, null=True)
    source = models.CharField(max_length=255, blank=True)

    def __str__(self):
        if self.lieu is not None:
            return f"{self.lieu.nom} ({self.date})"
        else:
            return f"{self.lieu_str} ({self.date})"


CAMP_CHOICES = [
        ('COALISES', 'Coalisés'),
        ('FRANCAIS', 'Français'),
        ('NONE', 'None')
    ]

class Unite(models.Model):
    nom = models.CharField(max_length=100)
    positions = models.ManyToManyField(Position, related_name='unites')
    camp = models.CharField(max_length=10, choices=CAMP_CHOICES, default='NONE')
    grade = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.nom
    
    def is_general(self):
        if len(list(self.dirige.all())):
            return True
        return False
    
    def get_equivalence(self):
        unites = [self]
        commande0 = Commande.objects.filter(general=self)
        for c in commande0:
            if c.unite_commandee.camp == self.camp or c.unite_commandee.camp == 'NONE':
                unites.append(c.unite_commandee)
        return set(unites)
    
#    def get_ordre_de_bataille(self):
#        print(f"self : {self}, pk : {self.pk}")
#        a_sous_ses_ordres = []
#        subordonnee = self.subordonnee_a.all()
#        print(subordonnee)
#        for s in subordonnee:
#            a_sous_ses_ordres.append(s.unite_commandant)
#            print(s.unite_commandant.pk)
#        print(a_sous_ses_ordres)
#
#        a_sous_ses_ordres_2 = []
#        subordonnee = self.commande_a.all()
#        print(subordonnee)
#        for s in subordonnee:
#            a_sous_ses_ordres_2.append(s.unite_subordonnee)
#        print(a_sous_ses_ordres_2)

    
    def nom_avec_general(self):
        generaux = list(self.est_dirigee_par.all())
        if len(generaux)>=1:
            return f"{self.nom} ({generaux[0].general.nom})"
        else:
            return self.nom

    

class Subordonne(models.Model):
    date = models.DateField()
    unite_commandant = models.ForeignKey(Unite, on_delete=models.CASCADE, related_name='commande_a')
    unite_subordonnee = models.ForeignKey(Unite, on_delete=models.CASCADE, related_name='subordonnee_a')

    def __str__(self):
        return f"{self.unite_subordonnee} est sous les ordres de {self.unite_commandant} le {self.date}"



class Commande(models.Model):
    date = models.DateField()
    general = models.ForeignKey(Unite, on_delete=models.CASCADE, related_name='dirige')
    unite_commandee = models.ForeignKey(Unite, on_delete=models.CASCADE, related_name='est_dirigee_par')

    def __str__(self):
        return f"{self.general} commande {self.unite_commandee} le {self.date}"
    

class Combat(models.Model):
    nom = models.CharField(max_length=100)
    lieu = models.ForeignKey(Lieu, on_delete=models.CASCADE, blank=True, null=True)
    lieu_str = models.CharField(max_length=300, blank=True, null=True)
    date = models.DateField()

    def __str__(self):
        return f"{self.nom} ({self.date})"





