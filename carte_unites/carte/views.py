from django.shortcuts import render
from django.views.generic import TemplateView
from carte.models import Unite, Position, Combat
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

    combats_features = []
    combats = Combat.objects.filter(date=date_dt)
    for combat in combats:
        if combat.lieu is not None:
            combats_features.append({
                    "type": "Feature",
                    "geometry": {
                        "type": "Point",
                        "coordinates": [combat.lieu.longitude, combat.lieu.latitude]
                    },
                    
                    "properties": {
                        "nom":combat.nom,
                        "date":combat.date,
                        "lieu":combat.lieu_str
                    }
                })
            
    for combat_feature in combats_features:
        popup = f"""
        <strong>{combat_feature['properties']['nom']} ({combat_feature['properties']['date']})</strong>
        """
        combat_feature["properties"]["popup"] = popup

    return JsonResponse({
            "position":{
                "type": "FeatureCollection",
                "features": features
            },
            "combats":{
                "type": "FeatureCollection",
                "features": combats_features
            },
        })


def positions_par_unite(request):
    unite_0 = request.GET.get('unite')
    if not unite_0:
        return JsonResponse({'error': 'Unité manquante'}, status=400)
    
    unite_0 = Unite.objects.get(id=unite_0)

    pas = 0.005
    positions_coords = []

    unites = unite_0.get_equivalence()
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


    #unite_0.get_ordre_de_bataille()


    return JsonResponse({
            "position":{
                "type": "FeatureCollection",
                "features": features
            },
        })