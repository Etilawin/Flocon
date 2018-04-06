# coding: utf-8
""" Le fichier principal contenant l'action même de générer le flocon et de gérer le script """
## from pycallgraph import PyCallGraph
## from pycallgraph.output import GraphvizOutput
from argparse import ArgumentParser  # On implore le dieu du scripting
from copy import deepcopy as dc
from os.path import join
from shutil import rmtree

from fonctions_process import *
from graphismes import *
from constantes import CONSTANTES

parser = ArgumentParser(
    description="Parser comprenant tout les paramètres possibles et imaginables")
parser.add_argument("-c"    , nargs=1, type=str, required=False, help="Les fichier contenant les constantes, une ligne devrait être sauté entre chaque constante et de la forme KAPPA=1.2, les constantes manquantes seront mises par défaut")
parser.add_argument("-i"    , nargs=1, type=int, required=False, help="Le nombre d'itérations pour le flocon")
parser.add_argument("-p"    , nargs=1, type=str, required=False, help="Le chemin où vous voulez que les photos soient stockées")
parser.add_argument("-t"    , nargs=1, type=int, required=False, help="La taille des hexagones")
parser.add_argument("--rate", nargs=1, type=int, required=False, help="Tout les combien de framerates vous voulez sauvegarder une image")
parser.add_argument("--width"    , nargs=1, type=int, required=False, help="La largeur de l'image, va avec l'option -h")
parser.add_argument("--height"    , nargs=1, type=int, required=False, help="La hauteur de l'image, va avec l'option -w")
parser.print_help()

# https://docs.python.org/3.3/library/argparse.html#argparse.ArgumentParser.add_argument
tableau_cellules = []
voisins = {}
cristal = set()
frontiere = set()

initialiser(tableau_cellules, voisins, cristal, frontiere)

chemin = create_folder()

all_possibilities = set()
add_to_all = all_possibilities.add
for colonne in range(CONSTANTES['W_TABLEAU']):
    for ligne in range(CONSTANTES['H_TABLEAU']):
        add_to_all((colonne, ligne))

all_possibilities.difference_update(cristal)

try:
    for i in range(CONSTANTES['ITERATIONS']):
        updated_tableau = dc(tableau_cellules)
        frontiere_up = frontiere.copy()

        # Mettre la boucle à l'intérieur de la fonction augmente considérablement le temps d'execution (environ 4*)
        # https://wiki.python.org/moin/PythonSpeed/PerformanceTips#Data_Aggregation
        diffusion(tableau_cellules, updated_tableau,
                  voisins, all_possibilities)

        for (colonne, ligne) in frontiere:
            cel_up = updated_tableau[colonne][ligne]
            voisins_cel = voisins[colonne, ligne]
            gel(cel_up)
            attachement(cel_up, voisins_cel, tableau_cellules)
            if cel_up[0]:  # Si elle vient d'être rattaché au cristal
                update_frontiere(colonne, ligne, cristal,
                                 frontiere_up, voisins, all_possibilities)
            else:  # Sinon
                fonte(cel_up)
                bruit(cel_up)

        # On retire les quelques cellules du cristal ce qui permet des itérations moins longues
        all_possibilities.difference_update(cristal)
        frontiere = frontiere_up.copy()
        tableau_cellules = dc(updated_tableau)

        if i % 25 == 0:
            generer_image(chemin, cristal, i // 25)

except KeyboardInterrupt:
    rep = input("Voulez vous effacer le dossier en cours ? ")
    if rep.lower() in ('o', 'oui'):
        rmtree(chemin, ignore_errors=True)
    raise KeyboardInterrupt
