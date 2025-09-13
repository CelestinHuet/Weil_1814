from django.urls import path
import carte.views as v

app_name = 'carte'
urlpatterns = [
    path('carte/', v.Carte.as_view(), name='carte'),
    path('units/', v.liste_unites, name='liste_unites'),
    path('positions_par_date/', v.positions_par_date, name='positions_par_date'),
    path('positions_par_unite/', v.positions_par_unite, name='positions_par_unite'),
    path("contact/", v.contact_view, name="contact"),
]