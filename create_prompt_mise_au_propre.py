"""
This file is part of 1814parlescartes.

1814parlescartes is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

1814parlescartes is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with 1814parlescartes. If not, see <https://www.gnu.org/licenses/>.
"""

import os


text_dir = "text"
files = sorted(os.listdir(text_dir))

output_dir = "prompts_mise_au_propre"
os.makedirs(output_dir, exist_ok=True)

for file in files:
    with open(os.path.join(text_dir, file), "r") as f:
        texte_source = f.read()
    # Prompt combiné
    prompt = f"""
    Voici un texte historique :
    \"\"\"
    {texte_source}
    \"\"\"
    Réponds uniquement en JSON. Donne un dictionnaire avec les clés :
    - "corps". Il faut le texte historique après avoir supprimé le numéro de page qui se trouve en haut et après avoir supprimé les notes de bas de page
    - "notes". Ne mets que les notes de bas de page. S'il n'y en a pas, met une chaîne de caractères vide. Ne mets pas les références aux sources (par exemple "Piré au général de Grouchy, ct duc de Trévise au général de France. (4r-
chives de la guerre.)")
    IMPORTANT : ta réponse doit être un JSON **valide**. Pas d'explications ni de texte hors JSON.
    """

    with open(f"{output_dir}/{file}", "w") as f:
        f.write(prompt)

