from django.urls import path

import carte.views as v

app_name = 'carte'
urlpatterns = [
    path('carte/', v.Carte.as_view(), name='carte'),
]