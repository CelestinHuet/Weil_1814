"""
This file is part of 1814parlescartes.

1814parlescartes is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

1814parlescartes is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with 1814parlescartes. If not, see <https://www.gnu.org/licenses/>.
"""


import os
from pathlib import Path

input_dir = Path("resultats_mise_au_propre/corps")
files = sorted(os.listdir(input_dir))
output_dir = Path("paragraphes_regroupes")
os.makedirs(output_dir, exist_ok=True)

separateur1 = "\n\n"
separateur2 = ". "

def open_file(file):
    with open(file, "r") as f:
        return f.read()

done = []
current_text = open_file(input_dir/files[0])
for i in range(len(files)-1):
    file = files[i]

    termine = False
        
    file2 = open_file(input_dir/files[i+1])

    if files[i+1].split("-")[0]!=files[i].split("-")[0]:
        new_current_text = file2
        
    else:
        file2_splitted = file2.split(separateur1)
        sep = separateur1

        if len(file2_splitted)==1:
            file2_splitted = file2.split(separateur2)
            sep = separateur2
            
        current_text += file2_splitted[0]
        new_current_text = sep.join(file2_splitted[1:])
    
    with open(output_dir/files[i], "w") as f:
        f.write(current_text)
    current_text = new_current_text

