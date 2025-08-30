from django.contrib import admin
from .models import Lieu, Position, Unite, Subordonne, Commande, Arrow

admin.site.register(Lieu)
admin.site.register(Position)
admin.site.register(Arrow)



@admin.register(Unite)
class UniteAdmin(admin.ModelAdmin):
    search_fields = ('nom',)
    ordering = ('nom',)


@admin.register(Subordonne)
class SubordonneAdmin(admin.ModelAdmin):
    search_fields = ('unite_commandant__nom', 'unite_subordonnee__nom',)
    ordering = ('unite_subordonnee__nom',)


@admin.register(Commande)
class CommandeAdmin(admin.ModelAdmin):
    search_fields = ('general__nom', 'unite_commandee__nom',)
    ordering = ('general__nom',)