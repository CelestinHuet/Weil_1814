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
    Le json doit contenir deux champs : "positions" et "date".
    Dans le champ "position", pour chaque mouvement ou position de troupe identifié, donne un dictionnaire avec les clés :
    - "unite". Je ne veux que le nom du général de l'unité ou sinon le numéro de du corps d'armée ou de la division. Par exemple, je ne veux pas "corps de Sacken" mais "Sacken" 
    - "lieu". Si l'unité se trouve entre deux villes, mets un point-virgule entre les deux noms de ville. Si l'unité se trouve dans deux villes différentes à la fois, crée deux dictionnaires. Je ne veux que des noms de localités, pas de localisation vague comme "dans ses cantonnements" ou "le long du fleuve".
    - "details". Cite la phrase complète qui justifie ce mouvement de troupe.
    - "date". Si la date n'est pas précisée, mets None. La date doit être de la forme jj/mm/aaaa. Si l'année n'est pas précisée, sache que les dates sont comprises entre décembre 1813 et mai 1814. 
    - "planifié". Je veux True ou False, mais rien d'autres. Ce doit être True dans le cas où c'est un mouvement planifié mais qui n'a pas été encore réalisé.
    - "effectif". Si l'effectif n'est pas précisé, mets None
    Liste-les dans une liste JSON.

    Dans le champ "date", il peut exister en tête d'un paragraphe la mention d'une date. Indique-là sous la forme jj/mm/aaaa. Si l'année n'est pas précisée, sache que les dates sont comprises entre décembre 1813 et mai 1814. Par exemple, si en début de paragraphe il y a "11 Janvier. —", mets 11/01/1814
    IMPORTANT : ta réponse doit être un JSON **valide**. Pas d'explications ni de texte hors JSON.
    """

    with open(f"{prompt_dir}/{file}", "w") as f:
        f.write(prompt)

