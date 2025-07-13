


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
TODO
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
TODO
```


Insérer les lieux dans la base de données
```
python manage.py insert_lieux --file lieux.json
```