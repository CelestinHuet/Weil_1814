import os


text_dir = "resultats_mise_au_propre"
files = sorted(os.listdir(os.path.join(text_dir, "corps")))

prompt_dir = "prompts"
os.makedirs(prompt_dir, exist_ok=True)

for file in files:
    with open(os.path.join(text_dir, "corps", file), "r") as f:
        texte_source = f.read()
    with open(os.path.join(text_dir, "notes", file), "r") as f:
        texte_notes = f.read()
    # Prompt combiné
    prompt = f"""
    Voici un texte historique :
    \"\"\"
    {texte_source}

    {texte_notes}
    \"\"\"
    Réponds uniquement en JSON.
    Le json doit contenir quatre champs : "positions", "date", "ordre_de_bataille" et "combat".
    Dans le champ "positions", pour chaque mouvement ou position de troupe identifié, donne un dictionnaire avec les clés :
    - "unite". Je ne veux que le nom du général de l'unité ou sinon le numéro de du corps d'armée ou de la division. Par exemple, je ne veux pas "corps de Sacken" mais "Sacken". Si le texte n'est pas en français, met la réponse en français. Par exemple, "1. leichte Divifion" devient "1ère division légère"
    - "lieu". Si l'unité se trouve entre deux villes, mets un point-virgule entre les deux noms de ville. Si l'unité se trouve dans deux villes différentes à la fois, crée deux dictionnaires. Je ne veux que des noms de localités, pas de localisation vague comme "dans ses cantonnements" ou "le long du fleuve". Je ne veux pas non plus de noms de pays, de région ou de cours d'eau, mais seulement des noms de ville, village ou hameau.
    - "details". Cite la phrase complète qui justifie ce mouvement de troupe. Je ne veux pas un extrait de phrase, mais bien la phrase complète. Si cette phrase n'est pas en français, ajoute entre parenthèses la traduction en français.
    - "date". Si la date n'est pas précisée, mets None. La date doit être de la forme jj/mm/aaaa. Si l'année n'est pas précisée, sache que les dates sont comprises entre décembre 1813 et mai 1814. 
    - "planifie". Je veux True ou False, mais rien d'autres. Ce doit être True dans le cas où c'est un mouvement planifié mais qui n'a pas été encore réalisé.
    - "effectif". Si l'effectif n'est pas précisé, mets None. Si le texte n'est pas en français, met la réponse en français
    Liste-les dans une liste JSON.

    Dans le champ "date", il peut exister en tête d'un paragraphe la mention d'une date. Indique-là sous la forme jj/mm/aaaa. Si l'année n'est pas précisée, sache que les dates sont comprises entre décembre 1813 et mai 1814. Par exemple, si en début de paragraphe il y a "11 Janvier. —", mets 11/01/1814
    
    Dans le champ "ordre_de_bataille", pour chaque général, identifie :
    - "nom_du_general"
    - "grade" : grade ou fonction (ex. général de division, maréchal, commandant en chef, etc.). Si le texte n'est pas en français, met la réponse en français
    - "commande" : ce qu’il commande (ex. 1er corps d’armée, 3e division, réserve de cavalerie, etc.). Si le texte n'est pas en français, met la réponse en français
    - "subordonne" : s’il est subordonné à un supérieur, indique le nom de ce supérieur ou l'unité commandée par ce supérieur. Si le texte n'est pas en français, met la réponse en français
    - "camp" : Répond soit par "France", soit par "Coalition", soit par "None" si tu ne sais pas. Utilise en priorité le texte. Tu as le droit d'utiliser tes connaissances sur la Campagne de France de 1814. Pour rappel, "Coalition" regroupe les forces coalisées opposées à Napoléon (russes, prussiens, autrichiens, bavarois, wurtembourgeois, saxons, suédois...) 
    IMPORTANT : ta réponse doit être un JSON **valide**. Pas d'explications ni de texte hors JSON.

    Dans le champ "combat", pour chaque combat ou bataille (je ne veux pas d'engagements mineurs comme une escarmouche, ni de terme trop générique comme invasion) entre deux armées ennemies, identifie :
    - "nom_affrontement". Si le texte n'est pas en français, met la réponse en français
    - "date". Si la date n'est pas précisée, mets None. La date doit être de la forme jj/mm/aaaa. Si l'année n'est pas précisée, sache que les dates sont comprises entre décembre 1813 et mai 1814. 
    - "lieu". Si l'affrontement se déroule dans plusieurs lieux, mets un point-virgule entre les noms de lieux. Je ne veux que des noms de localités, pas de localisation vague comme "dans ses cantonnements" ou "le long du fleuve". Je ne veux pas non plus de noms de pays, de région ou de cours d'eau, mais seulement des noms de ville, village ou hameau.
    - "details". Cite la phrase complète qui justifie ce combat ou cette bataille. Je ne veux pas un extrait de phrase, mais bien la phrase complète. Si cette phrase n'est pas en français, ajoute entre parenthèses la traduction en français.
    """

    with open(f"{prompt_dir}/{file}", "w") as f:
        f.write(prompt)

