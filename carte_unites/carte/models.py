from django.db import models

class Lieu(models.Model):
    nom = models.CharField(max_length=100)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)

    def __str__(self):
        return self.nom


class Position(models.Model):
    lieu = models.ForeignKey(Lieu, on_delete=models.CASCADE)
    date = models.DateField()
    planifie = models.BooleanField(default=False)
    justification = models.TextField(blank=True, null=True)
    effectif = models.CharField(max_length=100, blank=True, null=True)
    source = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"{self.lieu.nom} ({self.date})"


class Unite(models.Model):
    nom = models.CharField(max_length=100)
    positions = models.ManyToManyField(Position, related_name='unites')

    def __str__(self):
        return self.nom