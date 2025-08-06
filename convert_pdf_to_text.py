import os
from tqdm import tqdm



tome = 4

document = f"Weil_T{tome}.pdf"

images_dir = f"images_T{tome}"
os.makedirs(images_dir, exist_ok=True)

text_dir = "text"
os.makedirs(text_dir, exist_ok=True)

begin = 6
end = 464

for i in tqdm(range(begin, end+1)):
    commande = f"pdftoppm -f {i} -l {i} -png {document} {images_dir}/Weil"
    os.system(commande)

    nb_page = str(i)
    nb_page = "0"*(3-len(nb_page)) + nb_page

    commande = f"tesseract {images_dir}/Weil-{nb_page}.png {text_dir}/Weil_T{tome}-{nb_page} -l fra"
    os.system(commande)
