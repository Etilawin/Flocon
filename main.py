# coding: utf-8
## from pycallgraph import PyCallGraph
## from pycallgraph.output import GraphvizOutput
from argparse import ArgumentParser # On implore le dieu du scripting
from copy import deepcopy as dc
from os.path import join
from shutil import rmtree

from fonctions_process import *
from graphismes import *
from constantes import CONSTANTES

parser = ArgumentParser(description="Parser comprenant tout les paramètres possibles et imaginables")
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
        diffusion(tableau_cellules, updated_tableau, voisins, all_possibilities)

        for (colonne, ligne) in frontiere:
            cel_up = updated_tableau[colonne][ligne]
            voisins_cel = voisins[colonne, ligne]
            gel(cel_up)
            attachement(cel_up, voisins_cel, tableau_cellules)
            if cel_up[0]: # Si elle vient d'être rattaché au cristal
                update_frontiere(colonne, ligne, cristal, frontiere_up, voisins, all_possibilities)
            else: # Sinon
                fonte(cel_up)
                bruit(cel_up)

        frontiere = frontiere_up.copy()
        tableau_cellules = dc(updated_tableau)
        if i % 25 == 0:
            generer_image(chemin, cristal, i//25)

except KeyboardInterrupt:
    rep = input("Voulez vous effacer le dossier en cours ? ")
    if rep.lower() in ('o', 'oui'):
        rmtree(chemin, ignore_errors=True)
    raise KeyboardInterrupt
