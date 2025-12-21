"""
This file is part of 1814parlescartes.

1814parlescartes is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

1814parlescartes is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with 1814parlescartes. If not, see <https://www.gnu.org/licenses/>.
"""


from django.contrib import admin
from .models import Lieu, Position, Unite, Subordonne, Commande, Combat

admin.site.register(Lieu)
admin.site.register(Position)
admin.site.register(Combat)



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