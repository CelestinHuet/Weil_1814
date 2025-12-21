"""
This file is part of 1814parlescartes.

1814parlescartes is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

1814parlescartes is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with 1814parlescartes. If not, see <https://www.gnu.org/licenses/>.
"""


from django.core.management.base import BaseCommand
from carte.models import Unite, Arrow, Lieu
from tqdm import tqdm

class Command(BaseCommand):

    def handle(self, *args, **options):
        done = []

        # Delete all arrows
        arrows = Arrow.objects.all()
        for a in arrows:
            a.delete()
        
        # For each unite
        for unite in tqdm(Unite.objects.all()):
            
            if unite in done:
                continue

            # Get all Unite objects matching
            unites = unite.get_equivalence()

            # Get all positions from all Unite
            positions_per_date = {}
            for u in unites:
                for p in u.positions.all():
                    if not p.planifie:
                        if p.date not in list(positions_per_date.keys()):
                            positions_per_date[p.date] = [p]
                        else:
                            positions_per_date[p.date].append(p)

            # Compute barycenters for each day
            date_keys = sorted(list(positions_per_date.keys()))
            barycentres = {}
            for i in range(len(date_keys)):
                date_i = date_keys[i]
                lon = []
                lat = []
                for d0 in positions_per_date[date_i]:
                    if d0.lieu is None:
                        continue
                    lon.append(d0.lieu.longitude)
                    lat.append(d0.lieu.latitude)
                if len(lat)>0:
                    barycentres[date_i] = Lieu.objects.create(nom="", latitude=sum(lat)/len(lat), longitude=sum(lon)/len(lon))
            
            # Create Arrow object
            date_keys = sorted(list(barycentres.keys()))
            for i in range(len(date_keys)-1):
                date_i = date_keys[i]
                date_i1 = date_keys[i+1]
                
                Arrow.objects.create(
                    date = date_i1,
                    lieu_depart=barycentres[date_i],
                    lieu_arrivee=barycentres[date_i1],
                    unite=unite
                )
            done += unites
