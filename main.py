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
parser.add_argument("-c"       , nargs=1, type=str, required=False, metavar="file.txt"   , help="Les fichier contenant les constantes, une ligne devrait être sauté entre chaque constante et de la forme KAPPA=1.2, les constantes manquantes seront mises par défaut")
parser.add_argument("-i"       , nargs=1, type=int, default=[3300], required=False, metavar="Iterations" , help="Le nombre d'itérations pour le flocon")
parser.add_argument("-p"       , nargs=1, type=str, default=["images"],required=False, metavar="photos/"    , help="Le chemin où vous voulez que les photos soient stockées")
parser.add_argument("-t"       , nargs=1, type=int, default=[1], required=False, metavar="taille"     , help="La taille des hexagones")
parser.add_argument("--rate"   , nargs=1, type=int, defautl=[25], required=False, metavar="framerate"  , help="Tout les combien de framerates vous voulez sauvegarder une image")
parser.add_argument("--width"  , nargs=1, type=int, default=[800], required=False, help="La largeur de l'image, va avec l'option -h")
parser.add_argument("--height" , nargs=1, type=int, default=[800], required=False, help="La hauteur de l'image, va avec l'option -w")
arguments = parser.parse_args()

print(arguments)

if arguments.c:
    try:
        load_constants(arguments.c[0])
    except:
        print("Erreur lors de la lecture du fichier, les variables par défaut seront prises")

if arguments.i:
    CONSTANTES["ITERATIONS"] = abs(arguments.i[0])

if arguments.p:
    chemin_image = arguments.p[0]

if arguments.t:
    CONSTANTES["T_HEXAGONES"] = abs(arguments.t[0])

if arguments.rate:
    rate = abs(arguments.rate[0])

if arguments.width:
    CONSTANTES["W"] = abs(arguments.width[0])
    CONSTANTES['W_TABLEAU'] = int(CONSTANTES['W'] / CONSTANTES['T_HEXAGONES']) + 2
    CONSTANTES['W_TABLEAU'] += CONSTANTES['W_TABLEAU'] % 2

if arguments.height:
    CONSTANTES["H"] = abs(arguments.height[0])
    CONSTANTES['H_TABLEAU'] = int(CONSTANTES['H'] / CONSTANTES['T_HEXAGONES']) + 2
    CONSTANTES['H_TABLEAU'] += CONSTANTES['H_TABLEAU'] % 2


assert False

# https://docs.python.org/3.3/library/argparse.html#argparse.ArgumentParser.add_argument
tableau_cellules = []
voisins = {}
cristal = set()
frontiere = set()

initialiser(tableau_cellules, voisins, cristal, frontiere)

chemin = create_folder(chemin_image)

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

        if i % rate == 0:
            generer_image(chemin, cristal, i // rate)

except KeyboardInterrupt:
    rep = input("Voulez vous effacer le dossier en cours ? ")
    if rep.lower() in ('o', 'oui'):
        rmtree(chemin, ignore_errors=True)
    raise KeyboardInterrupt
