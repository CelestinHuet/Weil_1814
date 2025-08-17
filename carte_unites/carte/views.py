from django.shortcuts import render
from django.views.generic import TemplateView
from carte.models import Unite, Position, Arrow
from django.http import JsonResponse
from datetime import datetime


# Create your views here.
class Carte(TemplateView):

    template_name = "index.html"

    

def liste_unites(request):
    unites = Unite.objects.all()
    data = [{'id': u.id, 'text': u.nom_avec_general()} for u in unites]
    return JsonResponse(data, safe=False)


def positions_par_date(request):
    date = request.GET.get('date')
    if not date:
        return JsonResponse({'error': 'Date manquante'}, status=400)
    
    date = date.split("-")
    date_dt = datetime(year=int(date[0]), month=int(date[1]), day=int(date[2]))

    # Filtrage par date exacte (ou plage si besoin)
    positions = Position.objects.filter(date=date_dt)

    pas = 0.005
    positions_coords = []

    features = []
    for pos in positions:
        if len(pos.unites.all())==0:
            continue
        unite:Unite = pos.unites.all()[0]
        if pos.lieu is not None:
            position = [pos.lieu.longitude, pos.lieu.latitude]
            while position in positions_coords:
                position[0] += pas
            features.append({
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": position
                },
                
                "properties": {
                    "unite":unite.nom,
                    "date":pos.date,
                    "lieu":pos.lieu.nom,
                    "planifie":pos.planifie,
                    "justification":pos.justification,
                    "effectif":pos.effectif,
                    "source":pos.source,
                    "camp":unite.camp
                }
            })
            positions_coords.append(position)
    
    
    arrows = Arrow.objects.filter(date=date_dt)
    features_arrows = []
    for arrow in arrows:
        features_arrows.append({
                "type": "Feature",
                "geometry": {
                    "type": "LineString",
                    "coordinates": [[arrow.lieu_depart.longitude, arrow.lieu_depart.latitude],[arrow.lieu_arrivee.longitude, arrow.lieu_arrivee.latitude]]
                },
                
                "properties": {
                    "camp":arrow.unite.camp
                }
            })


    return JsonResponse({
            "position":{
                "type": "FeatureCollection",
                "features": features
            },
            "arrows":{
                "type": "FeatureCollection",
                "features": features_arrows
            }
        })


def positions_par_unite(request):
    unite = request.GET.get('unite')
    if not unite:
        return JsonResponse({'error': 'Unité manquante'}, status=400)
    
    unite = Unite.objects.get(id=unite)

    pas = 0.005
    positions_coords = []

    unites = unite.get_equivalence()
    positions = []
    for u in unites:
        positions += u.positions.all()

    features = []
    for pos in positions:
        if len(pos.unites.all())==0:
            continue
        unite:Unite = pos.unites.all()[0]
        if pos.lieu is not None:
            position = [pos.lieu.longitude, pos.lieu.latitude]
            while position in positions_coords:
                position[0] += pas
            features.append({
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": position
                },
                
                "properties": {
                    "unite":unite.nom,
                    "date":pos.date,
                    "lieu":pos.lieu.nom,
                    "planifie":pos.planifie,
                    "justification":pos.justification,
                    "effectif":pos.effectif,
                    "source":pos.source,
                    "camp":unite.camp
                }
            })

    arrows = []
    for unite in unites:
        arrows += list(Arrow.objects.filter(unite=unite))
    arrows = set(arrows)
    features_arrows = []
    for arrow in arrows:
        features_arrows.append({
                "type": "Feature",
                "geometry": {
                    "type": "LineString",
                    "coordinates": [[arrow.lieu_depart.longitude, arrow.lieu_depart.latitude],[arrow.lieu_arrivee.longitude, arrow.lieu_arrivee.latitude]]
                },
                
                "properties": {
                    "camp":arrow.unite.camp
                }
            })


    return JsonResponse({
            "position":{
                "type": "FeatureCollection",
                "features": features
            },
            "arrows":{
                "type": "FeatureCollection",
                "features": features_arrows
            }
        })