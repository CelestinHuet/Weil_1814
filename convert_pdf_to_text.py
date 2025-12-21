"""
This file is part of 1814parlescartes.

1814parlescartes is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

1814parlescartes is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with 1814parlescartes. If not, see <https://www.gnu.org/licenses/>.
"""


import os
from tqdm import tqdm
import argparse



parser = argparse.ArgumentParser(description="")
parser.add_argument('--input_pdf')
parser.add_argument('--begin', type=int)
parser.add_argument('--end', type=int)
args = parser.parse_args()

document = args.input_pdf

images_dir = os.path.basename(document).replace(".pdf", "")
os.makedirs(images_dir, exist_ok=True)

text_dir = "text"
os.makedirs(text_dir, exist_ok=True)

begin = args.begin
end = args.end

for i in tqdm(range(begin, end+1)):
    commande = f"pdftoppm -f {i} -l {i} -png {document} {images_dir}/{images_dir}"
    os.system(commande)

    nb_page = str(i)
    if end < 100:
        nb_page = "0"*(2-len(nb_page)) + nb_page
    else:
        nb_page = "0"*(3-len(nb_page)) + nb_page

    commande = f"tesseract {images_dir}/{images_dir}-{nb_page}.png {text_dir}/{images_dir}-{nb_page} -l fra"
    os.system(commande)
