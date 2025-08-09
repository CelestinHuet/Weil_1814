from django.db import models

class Lieu(models.Model):
    nom = models.CharField(max_length=100)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)

    def __str__(self):
        return self.nom


class Position(models.Model):
    lieu = models.ForeignKey(Lieu, on_delete=models.CASCADE, blank=True, null=True)
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
            unites.append(c.unite_commandee)
        commande1 = Commande.objects.filter(unite_commandee=self)
        for c in commande1:
            unites.append(c.general)
        return unites
    
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