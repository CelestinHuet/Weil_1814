# A faire

[ ] Ajouter la description du site
[ ] gérer le cas où le nom d'un général est inclus dans le nom d'une unité
[ ] Pour la localisation des unités isolées, utiliser le lieu le plus fréquent lors des dates à proximité
[ ] Retirer les lieux null, Italie, France, rive gauche et autres fleuves



# Modifier les séparations des pages

Le problème, ce sont les notes de bas de page. Il faudrait renvoyer le corps du texte et les notes de bas de page de manière séparée. Une fois qu'on a ça, on peut mettre dans deux répertoires différents notes de bas de page et corps du texte et appliquer ensuite le regroupement de paragraphes sur les deux répertoires.



# Processus

Le livre sous format pdf est découpé en page puis transformé en format texte avec Tesseract.

```
python convert_pdf_to_text.py --input_pdf    --begin    --end
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
python manage.py fusionner_unites_1bis
python manage.py fusionner_unites_etape_2
```



Associer les unités à des lieux et contrôler qu'il n'y a pas d'erreurs
```
python manage.py associate_unites_lieux
python manage.py controle_localisation
```


Associe à chaque unité un échelon (armée, corps, division, brigade...)
```
python manage.py associate_unite_echelon
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
python manage.py associate_combat_lieux
python manage.py controle_localisation
python manage.py associate_unite_echelon




# Les sources possibles d'erreurs

* Mauvaise lecture des noms et des chiffres (dates notamment) par Tesseract
* Noms de villes qui ont disparu ou modifiés (Sainte-Croix : Sainte-Croix en Plaine)
* Lieu trop vague : nom d'une région (Savoie) ou d'une rivière (Meuse)



# A ajouter

* Fabvier, Charles Nicolas, Journal des opérations du Sixième corps pendant la campagne de France en 1814 (https://books.googleusercontent.com/books/content?req=AKW5QacNIMYWiY9mwg20HNrpeU72EG3T3qqRdIlVau3P8ntYWYvu9bJovxwa9NrujyhxGqsPmTYd28bOoyHbyUMoEBkEATI7Lu5VPGIgRvcOoxbqIHKGMa0gTqdpiy6Ksk0TjSWZkCAlKJ2CXocTTK-sG9wLLZLkezJJEIo2KqwKXrNrswMUI8vj4ykgxDX0ZQzHjSPYwBBOKhyIJOUbAFwsmZxT9K-2OnUsnj557ROtqw80yf8eeBcpZWSkXtzASEOPHQt1Wkcl8oHWbV35IfCTYHU91lx-u7zxQaa6piVIaziLWKA5lbw)
* Grouchy (Marquis de), Mémoires du Maréchal de Grouchy, livres XII et XIII (https://gallica.bnf.fr/ark:/12148/bpt6k69568c/f477.item.r=M%C3%A9moires%20du%20mar%C3%A9chal%20de%20Grouchy)
* Hiller, Fritz von, Geschichte des Feldzuges 1814 gegen Frankreich unter besonderer Berücksichtigung der Anteilnahme der Königlich württembergischen Truppen (https://books.googleusercontent.com/books/content?req=AKW5QafNUPwocMSEtD0WlWiLNMArJOTTE8O6vutmgFZbEI7jyJSRXsCdrBXxFe4tiAtlB8cXrXs8hTicrMnTTJ4keraziWUqsqjhC-REe_ymWPT-cLIZIPIu5Ds1cnJA3xQyyqrb41jzWBlg16UPxhqPs5Gq82bu2ZtIftAkJqLQM3M9cPlpoN5XivRdGlbrLKJdmNSKMQm0eczLcXdlvSSBYfidkGeV9Ma60_verA0qEUVceb8NVHe3EnCs_yRoJYxo8b3lrRmSoQ9sxmdl2TN4KrzQKaYs8Bfda79Rhme7eKtp7R1ezHE)
* Koch, Frédéric, Mémoire pour servir à l'histoire de la campagne de 1814
* Marmont, Maréchal, Mémoires du duc de Raguse (https://gallica.bnf.fr/ark:/12148/bpt6k695629/f438.item.r=M%C3%A9moires%20du%20mar%C3%A9chal%20Marmont,%20duc%20de%20Raguse#)
* Ségur, Philippe-Paul (général, comte de), La Campagne de France, du Rhin à Fontainebleau (https://gallica.bnf.fr/ark:/12148/bpt6k930585r/f574.item#)
* Les combats de Mormant, de Villeneuve-le-Comte et de Montereau (17 et 18 février 1814) (https://gallica.bnf.fr/ark:/12148/bpt6k6562110d/f39.item#)
* Journal historique de la division de cavalerie légère du 5e corps de cavalerie, pendant la campagne en 1814 (https://gallica.bnf.fr/ark:/12148/bpt6k6369024s/f89.item.texteImage#)




# Descriptif

Les ouvrages présentant les opérations militaires souffrent généralement d'un même défaut : les cartes sont assez médiocres. L'échelle est absente, le réseau fluvial ou le réseau routier n'est pas représenté, le relief est illisible, tous les villages mentionnés ne sont pas visibles, les unités ne sont pas placés... L'idée de ce petit site est de présenter la campagne de France par les cartes, afin d'aider à la compréhension de cette surprenante campagne où malgré la forte infériorité numérique de son armée, Napoléon parvint à infliger de nombreux revers aux coalisés avant finalement de devoir abdiquer à Fontainebleau.

Une particularité de ce site consiste dans l'acquisition des données. En effet, la chaîne de traitement pour les récupérer est entièrement automatique grâce aux modèles de langages qui se sont fortement développés ces dernières années et permettent de nouvelles opportunités dans le traitement de gros volumes de texte.