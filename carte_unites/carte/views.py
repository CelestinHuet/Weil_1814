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
    data = [{'id': u.id, 'text': u.nom_avec_general()} for u in unites if u.is_general()]
    return JsonResponse(data, safe=False)



def position_in_list(list, position, unite):
    for feature in list:
        if feature["properties"]["unite"] == unite.nom and feature["properties"]["lieu"] == position.lieu.nom and feature["properties"]["date"] == position.date:
            return feature
    return None


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

            feature = position_in_list(features, pos, unite)
            if feature is not None:
                feature["properties"]["planifie"].append(pos.planifie)
                feature["properties"]["justification"].append(pos.justification)
                feature["properties"]["effectif"].append(pos.effectif)
                feature["properties"]["source"].append(pos.source)
            else:
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
                        "planifie":[pos.planifie],
                        "justification":[pos.justification],
                        "effectif":[pos.effectif],
                        "source":[pos.source],
                        "camp":unite.camp
                    }
                })
                positions_coords.append(position)
    

    for feature in features:
        props = feature["properties"]
        popup = f"""
        <strong>{props["unite"]}</strong>
        <br>{props["date"]}<br>
        <br>{props["lieu"]}<br>
        Extraits :
        """

        for i in range(len(props["justification"])):
            popup += f"""
            <ul> - {props["justification"][i]} ({props["source"][i]}).
            """
            if props["planifie"][i]:
                popup += "<strong> Objectif</strong>"
            popup += "</ul>"
        feature["properties"]["popup"] = popup
        feature["properties"]["planifie"] = all(feature["properties"]["planifie"])


    return JsonResponse({
            "position":{
                "type": "FeatureCollection",
                "features": features
            },
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
    positions = sorted(positions, key=lambda x : x.date)
    for pos in positions:
        if len(pos.unites.all())==0:
            continue
        unite:Unite = pos.unites.all()[0]
        if pos.lieu is not None:
            
            feature = position_in_list(features, pos, unite)
            if feature is not None:
                feature["properties"]["planifie"].append(pos.planifie)
                feature["properties"]["justification"].append(pos.justification)
                feature["properties"]["effectif"].append(pos.effectif)
                feature["properties"]["source"].append(pos.source)
            else:
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
                        "planifie":[pos.planifie],
                        "justification":[pos.justification],
                        "effectif":[pos.effectif],
                        "source":[pos.source],
                        "camp":unite.camp
                    }
                })
                positions_coords.append(position)
    

    for feature in features:
        props = feature["properties"]
        popup = f"""
        <strong>{props["unite"]}</strong>
        <br>{props["date"]}<br>
        <br>{props["lieu"]}<br>
        Extraits :
        """

        for i in range(len(props["justification"])):
            popup += f"""
            <ul>{props["justification"][i]} ({props["source"][i]})</ul>
            """
            if props["planifie"][i]:
                popup += "<b> Objectif</b>"
            popup += "</ul>"
        feature["properties"]["popup"] = popup
        feature["properties"]["planifie"] = all(feature["properties"]["planifie"])


    return JsonResponse({
            "position":{
                "type": "FeatureCollection",
                "features": features
            },
        })