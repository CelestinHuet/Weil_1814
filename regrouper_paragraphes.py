import os
import glob
import re
import argparse

def recoller_paragraphes(repertoire_cible):
    """
    Analyse les fichiers .txt d'un répertoire, détecte les paragraphes
    coupés entre les fichiers et les fusionne.

    Un paragraphe est considéré comme terminé par le marqueur '.\n\n'.
    """
    print(f"Analyse du répertoire : {repertoire_cible}\n")
    
    # Le séparateur qui marque la fin d'un paragraphe complet
    separateur = '.\n\n'

    # 1. Trouver tous les fichiers .txt dans le répertoire
    # On utilise os.path.join pour que cela fonctionne sur Windows, Mac et Linux
    chemin_recherche = os.path.join(repertoire_cible, '*.txt')
    fichiers_txt = glob.glob(chemin_recherche)

    if not fichiers_txt:
        print("Aucun fichier .txt n'a été trouvé dans ce répertoire.")
        return

    # 2. Trier les fichiers par ordre numérique pour traiter les pages correctement
    # (ex: page1.txt, page2.txt, ... page10.txt)
    def cle_de_tri_numerique(nom_fichier):
        # Extrait le premier nombre trouvé dans le nom du fichier
        nombres = re.findall(r'\d+', os.path.basename(nom_fichier))
        return int(nombres[0]) if nombres else 0

    fichiers_txt.sort(key=cle_de_tri_numerique)
    
    print("Fichiers qui seront traités (dans l'ordre) :")
    for f in fichiers_txt:
        print(f" - {os.path.basename(f)}")
    print("-" * 20)


    # 3. Parcourir les fichiers deux par deux pour trouver les coupures
    # On s'arrête à l'avant-dernier fichier, car on regarde toujours le suivant
    for i in range(len(fichiers_txt) - 1):
        fichier_actuel_path = fichiers_txt[i]
        fichier_suivant_path = fichiers_txt[i+1]

        with open(fichier_actuel_path, 'r', encoding='utf-8') as f:
            contenu_actuel = f.read()

        # 4. Vérifier si le fichier actuel se termine bien par un paragraphe complet
        # On utilise rstrip() pour ignorer d'éventuels espaces ou sauts de ligne à la toute fin
        if not contenu_actuel.rstrip().endswith('.'):
            print(f"✂️ Paragraphe coupé détecté entre '{os.path.basename(fichier_actuel_path)}' et '{os.path.basename(fichier_suivant_path)}'")

            # 5. Si le paragraphe est coupé, on lit le fichier suivant pour récupérer le morceau manquant
            with open(fichier_suivant_path, 'r+', encoding='utf-8') as f_suivant:
                contenu_suivant = f_suivant.read()

                # On cherche le premier marqueur de fin de paragraphe dans le fichier suivant
                # On utilise split() avec une limite de 1 pour ne couper que sur la première occurrence
                morceaux = contenu_suivant.split(separateur, 1)
                
                partie_a_deplacer = morceaux[0] + separateur
                contenu_restant_du_fichier_suivant = morceaux[1] if len(morceaux) > 1 else ""

                # 6. On modifie les contenus
                nouveau_contenu_actuel = contenu_actuel + partie_a_deplacer

                # 7. On réécrit les deux fichiers avec le contenu corrigé
                with open(fichier_actuel_path, 'w', encoding='utf-8') as f_actuel_maj:
                    f_actuel_maj.write(nouveau_contenu_actuel)
                
                # On réécrit le fichier suivant avec la partie déplacée en moins
                f_suivant.seek(0) # On retourne au début du fichier
                f_suivant.write(contenu_restant_du_fichier_suivant)
                f_suivant.truncate() # On supprime l'ancien contenu qui pourrait rester à la fin

                print(f"  -> ✅ Correction effectuée.")

    print("\nOpération de fusion des paragraphes terminée.")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="")
    parser.add_argument('--input', default='', help='')
    args = parser.parse_args()
    # Indiquez ici le chemin vers votre dossier contenant les fichiers txt
    # Mettez '.' pour cibler le dossier où se trouve le script
    dossier_des_pages = args.input 
    
    # LIGNE IMPORTANTE : FAITES UNE SAUVEGARDE AVANT DE LANCER !
    recoller_paragraphes(dossier_des_pages)