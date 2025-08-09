from django.contrib import admin
from .models import Lieu, Position, Unite, Subordonne, Commande

admin.site.register(Lieu)
admin.site.register(Position)
admin.site.register(Unite)
admin.site.register(Subordonne)
admin.site.register(Commande)