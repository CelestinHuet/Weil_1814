


# A faire

- [ ] Modifier les séparations de page pour qu'elles tombent à la limite des pages.
- [ ] Tester les différents LLM
- [ ] Récupérer les coordonnées lon/lat des villes et lieux-dits.
- [ ] Créer la base de données
- [ ] Afficher les données


# Modifier les séparations des pages

Le problème, ce sont les notes de bas de page. Il faudrait renvoyer le corps du texte et les notes de bas de page de manière séparée. Une fois qu'on a ça, on peut mettre dans deux répertoires différents notes de bas de page et corps du texte et appliquer ensuite le regroupement de paragraphes sur les deux répertoires.



# Processus

Le livre sous format pdf est découpé en page puis transformé en format texte avec Tesseract.

```
python convert_pdf_to_text.py
```


Il faut mettre au propre les pages : retirer les numéros de page et mettre à part les notes.

```
python create_prompt_mise_au_propre.py
```

Mettre au propre
```
python mise_au_propre.py
```

Convertir les json en txt
```
python mise_au_propre_json_to_txt.py
```


Regrouper les paragraphes qui sont séparés sur deux pages
```
python regrouper_paragraphes.py --input resultats_mise_au_propre/corps
python regrouper_paragraphes.py --input resultats_mise_au_propre/notes
```

Ecrire les prompts
```
python create_prompt.py
```

Exécuter les prompts
```
python extract_text_information.py
```

Compléter les dates manquantes 
```
python complete_dates.py
```

Géolocaliser les lieux
```
python geolocalisation.py
```


Insérer les lieux dans la base de données
```
python manage.py insert_lieux --file ../coordonnees.json
```

Insérer les unités dans la base de données
```
python manage.py insert_unites --directory ../resultats/gemini_2-5_dates_corrected
```


Fusionner les unités qui n'ont que la casse de différences dans le nom
```
python manage.py fusionner_unites
python manage.py fusionner_unites_etape_2
```



Associer les unités à des lieux et contrôler qu'il n'y a pas d'erreurs
```
python manage.py associate_unites_lieux
python manage.py controle_localisation
```


Créer les flèches de déplacement d'unités
```
python manage.py create_arrows
```

Pour réinitialiser la base de données
```
python manage.py flush
```




python manage.py insert_lieux --file ../coordonnees.json
python manage.py insert_unites --directory ../resultats/gemini_2-5_dates_corrected
python manage.py fusionner_unites
python manage.py fusionner_unites_1bis
python manage.py fusionner_unites_etape_2
python manage.py associate_unites_lieux
python manage.py controle_localisation




# Les sources possibles d'erreurs

* Mauvaise lecture des noms et des chiffres (dates notamment) par Tesseract
* Noms de villes qui ont disparu ou modifiés (Sainte-Croix : Sainte-Croix en Plaine)
* Lieu trop vague : nom d'une région (Savoie) ou d'une rivière (Meuse)