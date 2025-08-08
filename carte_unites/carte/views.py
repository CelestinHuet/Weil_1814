from django.shortcuts import render
from django.views.generic import TemplateView
from carte.models import Unite, Position
from django.http import JsonResponse
from datetime import datetime


# Create your views here.
class Carte(TemplateView):

    template_name = "index.html"

    

def liste_unites(request):
    unites = Unite.objects.all().values('id', 'nom')
    data = [{'id': u['id'], 'text': u['nom']} for u in unites]
    return JsonResponse(data, safe=False)


def positions_par_date(request):
    date = request.GET.get('date')
    if not date:
        return JsonResponse({'error': 'Date manquante'}, status=400)
    
    date = date.split("-")
    date_dt = datetime(year=int(date[0]), month=int(date[1]), day=int(date[2]))

    # Filtrage par date exacte (ou plage si besoin)
    positions = Position.objects.filter(date=date_dt)

    features = []
    for pos in positions:
        unite:Unite = pos.unites.all()[0]
        if pos.lieu is not None:
            features.append({
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [pos.lieu.longitude, pos.lieu.latitude]
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
    return JsonResponse({
        "type": "FeatureCollection",
        "features": features
    })


def positions_par_unite(request):
    unite = request.GET.get('unite')
    if not unite:
        return JsonResponse({'error': 'Unité manquante'}, status=400)
    
    unite = Unite.objects.get(id=unite)

    positions = unite.positions.all()

    features = []
    for pos in positions:
        unite:Unite = pos.unites.all()[0]
        if pos.lieu is not None:
            features.append({
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [pos.lieu.longitude, pos.lieu.latitude]
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
    return JsonResponse({
        "type": "FeatureCollection",
        "features": features
    })