from django.shortcuts import render
from django.views.generic import TemplateView
from carte.models import Unite, Position, Combat
from django.http import JsonResponse
from datetime import datetime
import logging
from django.shortcuts import render, redirect
from django.core.mail import send_mail
from .forms import ContactForm

logger = logging.getLogger("campagne_France_view")


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



def write_popup(props):


    popup = f"""
    <div class="map-popup" role="dialog" aria-label="Détails de l'unité">
        <div class="map-popup__header">
            <div class="map-popup__title">{props["unite"]}</div>
            <div class="map-popup__meta">
            <time class="map-popup__date" datetime="2025-09-15">{props["date"]}</time>
            <span class="map-popup__location">{props["lieu"]}</span>
            </div>
        </div>


        <blockquote class="map-popup__quote map-popup__quote--collapsed" id="quote1">
        """
    
    for i in range(len(props["justification"])):
        popup += f"""
            <p>
            {props["justification"][i]} - ({props["source"][i]}).

            """
        if props["planifie"][i]:
            popup += "<strong> (Objectif)</strong>"
            
        popup += """
        </p>
        """
    popup += """
        </blockquote>

        <button class="map-popup__toggle" aria-expanded="false" aria-controls="quote1">Lire la suite</button>


        </div>

    """
    return popup


def positions_par_date(request):
    date = request.GET.get('date')
    if not date:
        return JsonResponse({'error': 'Date manquante'}, status=400)
    
    logger.info(f"Requête par date : {date}")
    
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
                        "camp":unite.camp,
                        "echelon":unite.echelon
                    }
                })
                positions_coords.append(position)
    

    for feature in features:
        props = feature["properties"]
        feature["properties"]["popup"] = write_popup(props)
        feature["properties"]["planifie"] = all(feature["properties"]["planifie"])

    combats_features = []
    combats = Combat.objects.filter(date=date_dt)
    for combat in combats:
        if combat.lieu is not None:
            combats_features.append({
                    "type": "Feature",
                    "geometry": {
                        "type": "Point",
                        "coordinates": [combat.lieu.longitude, combat.lieu.latitude - pas]
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
            "est_commande_par":[],
            "a_sous_ses_ordres":[]
        })


def positions_par_unite(request):
    unite_0_id = request.GET.get('unite')
    if not unite_0_id:
        return JsonResponse({'error': 'Unité manquante'}, status=400)
    
    unite_0 = Unite.objects.get(id=unite_0_id)

    logger.info(f"Requête par unité : {unite_0.nom} {unite_0_id}")

    pas = 0.005
    positions_coords = []

    unites = unite_0.get_equivalence()
    positions = []
    for u in unites:
        positions += u.positions.all()

    features = []
    combats_features = []
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
                        "camp":unite.camp,
                        "echelon":unite.echelon
                    }
                })
                positions_coords.append(position)

            combats = pos.lieu.lieu_combat.all()
            for combat in combats:
                if combat.date==pos.date:
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


    for feature in features:
        props = feature["properties"]
        feature["properties"]["popup"] = write_popup(props)
        feature["properties"]["planifie"] = all(feature["properties"]["planifie"])


    for combat_feature in combats_features:
        popup = f"""
        <strong>{combat_feature['properties']['nom']} ({combat_feature['properties']['date']})</strong>
        """
        combat_feature["properties"]["popup"] = popup
    odb = unite_0.get_ordre_de_bataille()

    return JsonResponse({
            "position":{
                "type": "FeatureCollection",
                "features": features
            },
            "combats":{
                "type": "FeatureCollection",
                "features": combats_features
            },
            "est_commande_par":odb["est_commande_par"],
            "a_sous_ses_ordres":odb["a_sous_ses_ordres"]

        })


def contact_view(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            nom = form.cleaned_data["nom"]
            email = form.cleaned_data["email"]
            message = form.cleaned_data["message"]

            # Envoi de l'email
            send_mail(
                subject=f"Message de {nom}",
                message=message,
                from_email=email,
                recipient_list=["ton_adresse@mail.com"],  # à remplacer par ton email
            )

            return redirect("carte:carte")  # redirection après envoi
    else:
        form = ContactForm()

    return render(request, "contact.html", {"form": form})


def faq_view(request):
    return render(request, "FAQ.html")