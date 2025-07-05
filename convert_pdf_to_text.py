import os
from tqdm import tqdm

document = "Weil_T1.pdf"

images_dir = "images"
os.makedirs(images_dir, exist_ok=True)

text_dir = "text"
os.makedirs(text_dir, exist_ok=True)

begin = 12
end = 547

for i in tqdm(range(begin, end+1)):
    commande = f"pdftoppm -f {i} -l {i} -png {document} {images_dir}/Weil"
    os.system(commande)

    nb_page = str(i)
    nb_page = "0"*(3-len(nb_page)) + nb_page

    commande = f"tesseract {images_dir}/Weil-{nb_page}.png {text_dir}/Weil-{nb_page} -l fra"
    os.system(commande)
