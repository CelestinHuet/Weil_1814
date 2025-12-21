# 1814 par les cartes

Les ouvrages présentant les opérations militaires souffrent généralement d'un même défaut : les cartes sont assez médiocres. L'échelle est absente, le réseau fluvial ou le réseau routier n'est pas représenté, le relief est illisible, tous les villages mentionnés ne sont pas visibles, les unités ne sont pas placés... L'idée de ce petit site est de présenter la campagne de France par les cartes, afin d'aider à la compréhension de cette surprenante campagne où malgré la forte infériorité numérique de son armée, Napoléon parvint à infliger de nombreux revers aux coalisés avant finalement de devoir abdiquer à Fontainebleau.

Une particularité de ce site consiste dans l'acquisition des données. En effet, la chaîne de traitement pour les récupérer est entièrement automatique grâce aux modèles de langages qui se sont fortement développés ces dernières années et permettent de nouvelles opportunités dans le traitement de gros volumes de texte.

Schématiquement, la démarche est la suivante :
* Les ouvrages sont passés du format image au format texte à l'aide de Tesseract
* Chaque page de chaque ouvrage est passée une première fois à un LLM, en l'occurence Gemini Flash 2.5, pour séparer le corps du texte et les notes de bas de page.
* Les paragraphes à cheval sur deux pages sont regroupés
* Chaque page est passé une deuxième fois à un LLM. Le LLM extrait les positions des unités, les dates, le camp des unités, les relations de commandement et de subordination entre les unités et les combats. Une unité peut être un général ou bien une entité comme un corps d'armée, une division... Une distinction est faite entre les positions qui sont des objectifs (le général donne l'ordre de se porter sur telle ville) et les positions qui sont réellement occupées par les unités
* Via Open Street Map, on récupère les coordonnées de chaque lieu
* On insère dans la base de données les unités et les lieux
* On fusionne les unités qui ont le même nom
* Chaque lieu peut posséder plusieurs homonymes : Bar peut aussi bien représenter Bar-sur-Aube que Bar-sur-Seine. Pour trouver l'homonyme le plus probable, on cherche pour chaque unité le chemin le plus court qu'elle peut parcourir dans la campagne.
* On contrôle le résultat de l'algorithme : si la moyenne journalière d'une unité est trop élevé, alors il y a une erreur de localisation.
* On détermine l'échelon des unités : armée, corps d'armée, division, brigade, régiment, bataillon, escadron...
* On essaye de déterminer le camp pour les unités dont il n'a pas été identifié par le LLM

Comme l'algorithme est automatisé, il faut être conscient qu'il n'est pas parfait et que des erreurs ont pu se glisser. Voici quelques types d'erreurs déjà identifiés :
* Tesseract n'est pas très bon pour lire les nombres donc les dates peuvent être erronées. Quelques contrôles ont été ajoutés, mais il reste des erreurs. Il n'est pas très performants non plus sur certaines polices d'écritures et pour les noms propres. Un général peut donc être écrit de plusieurs manières différentes, et ce malgré les algorithmes de fusion d'unités. De même, les citations peuvent contenir des fautes d'ortographes.
* Le numéro de page des sources peut avoir un décalage d'une page. Cela est dû au regroupement des paragraphes qui sont à cheval sur deux pages.
* Certains noms de villes ou de hameaux ont été modifiés (Sainte-Croix est actuellement Sainte-Croix-en-Plaine par exemple), voire ont complètement disparus mais d'autres localités avec le même toponyme continuent d'exister. L'unité sera alors mal placée.
* Certains lieux sont trop vagues, notamment les cours d'eau les expressions comme "rive gauche" ou les noms de région (Savoie)
* Dans les échelons, il peut y avoir confusion entre un corps d'armée et un autre échelon. En effet, l'expression "un corps" est régulièrement utilisée pour désigner tout type de formation

Les ouvrages utilisés sont les suivants :
* [Fabvier, Charles Nicolas, Journal des opérations du Sixième corps pendant la campagne de France en 1814](https://books.googleusercontent.com/books/content?req=AKW5QacNIMYWiY9mwg20HNrpeU72EG3T3qqRdIlVau3P8ntYWYvu9bJovxwa9NrujyhxGqsPmTYd28bOoyHbyUMoEBkEATI7Lu5VPGIgRvcOoxbqIHKGMa0gTqdpiy6Ksk0TjSWZkCAlKJ2CXocTTK-sG9wLLZLkezJJEIo2KqwKXrNrswMUI8vj4ykgxDX0ZQzHjSPYwBBOKhyIJOUbAFwsmZxT9K-2OnUsnj557ROtqw80yf8eeBcpZWSkXtzASEOPHQt1Wkcl8oHWbV35IfCTYHU91lx-u7zxQaa6piVIaziLWKA5lbw)
* [Grouchy (Marquis de), Mémoires du Maréchal de Grouchy, livres XII et XIII](https://gallica.bnf.fr/ark:/12148/bpt6k69568c/f477.item.r=M%C3%A9moires%20du%20mar%C3%A9chal%20de%20Grouchy)
* [Hiller, Fritz von, Geschichte des Feldzuges 1814 gegen Frankreich unter besonderer Berücksichtigung der Anteilnahme der Königlich württembergischen Truppen](https://books.googleusercontent.com/books/content?req=AKW5QafNUPwocMSEtD0WlWiLNMArJOTTE8O6vutmgFZbEI7jyJSRXsCdrBXxFe4tiAtlB8cXrXs8hTicrMnTTJ4keraziWUqsqjhC-REe_ymWPT-cLIZIPIu5Ds1cnJA3xQyyqrb41jzWBlg16UPxhqPs5Gq82bu2ZtIftAkJqLQM3M9cPlpoN5XivRdGlbrLKJdmNSKMQm0eczLcXdlvSSBYfidkGeV9Ma60_verA0qEUVceb8NVHe3EnCs_yRoJYxo8b3lrRmSoQ9sxmdl2TN4KrzQKaYs8Bfda79Rhme7eKtp7R1ezHE)
* [Koch, Frédéric, Mémoire pour servir à l'histoire de la campagne de 1814](https://gallica.bnf.fr/ark:/12148/bpt6k63657773.texteImage)
* [Marmont, Maréchal, Mémoires du duc de Raguse](https://gallica.bnf.fr/ark:/12148/bpt6k695629/f438.item.r=M%C3%A9moires%20du%20mar%C3%A9chal%20Marmont,%20duc%20de%20Raguse#)
* [Ségur, Philippe-Paul (général, comte de), La Campagne de France, du Rhin à Fontainebleau](https://gallica.bnf.fr/ark:/12148/bpt6k930585r/f574.item#)
* [Les combats de Mormant, de Villeneuve-le-Comte et de Montereau (17 et 18 février 1814)](https://gallica.bnf.fr/ark:/12148/bpt6k6562110d/f39.item#)
* [Journal historique de la division de cavalerie légère du 5e corps de cavalerie, pendant la campagne en 1814](https://gallica.bnf.fr/ark:/12148/bpt6k6369024s/f89.item.texteImage#)




# Processus

Le livre sous format pdf est découpé en page, sauvegardée chacune sous format png
```
python convert_pdf_to_image.py --input_pdf [fichier]   --begin [premiere_page]   --end [dernière page]
```

Gemini extrait les informations
```
python extract_text_information_v2.py
```

Compléter les dates manquantes et regrouper tous les éléments par livre
```
python merge_extraction.py
```

Géolocaliser les lieux
```
python merge_geolocalisation.py
python geolocalisation.py
```

Insérer les lieux dans la base de données
```
cd carte_unites
python manage.py insert_lieux --file ../coordonnees.json
```

Insérer les unités dans la base de données
```
python manage.py insert_unites --directory ../resultats_v2_merge
```

Fusionner tous les généraux qui ont le même nom
```
python manage.py fusionner_unites
```

Fusionner les généraux qui ont presque le même nom
```
python manage.py fusionner_unites_1bis
```

Fusionner toutes les unités qui sont commandées par le même général et qui ont le même nom
```
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



```
python manage.py insert_lieux --file ../coordonnees.json
python manage.py insert_unites --directory ../resultats_v2_merge
python manage.py fusionner_unites
python manage.py fusionner_unites_1bis
python manage.py fusionner_unites_etape_2
python manage.py associate_unites_lieux
python manage.py associate_combat_lieux
python manage.py controle_localisation
python manage.py associate_unite_echelon
python manage.py associate_unite_camp
```



# Pour les cartes

```
gdalwarp -t_srs EPSG:3857 page-65.tif page-65_3857.tif
gdal2tiles.py -z 5-12 --xyz -w none page-65_3857.tif tiles/
```