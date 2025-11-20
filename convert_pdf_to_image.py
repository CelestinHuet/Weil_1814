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
