# coding: utf-8
# from pycallgraph import PyCallGraph
# from pycallgraph.output import GraphvizOutput
from copy import deepcopy as dc
from os.path import join

from fonctions_process import *
from graphismes import *

tableau_cellules = []
voisins = {}
cristal = set()
frontiere = set()

if __name__ == '__main__':

    initialiser(tableau_cellules, voisins, cristal, frontiere)

    chemin = create_folder()

    all_possibilities = []
    add_to_all = all_possibilities.append
    for colonne in range(W_TABLEAU):
        for ligne in range(H_TABLEAU):
            add_to_all((colonne, ligne))

    try:
        for i in range(ITERATIONS):
            updated_tableau = dc(tableau_cellules)
            frontiere_up = frontiere.copy()

            for (colonne, ligne) in all_possibilities:  # Évite de recréer à chaque fois un range
                cel = tableau_cellules[colonne][ligne]
                if not cel[0]:
                    cel_up = updated_tableau[colonne][ligne]
                    voisins_cel = voisins[colonne, ligne]
                    diffusion(cel, cel_up, voisins_cel, tableau_cellules)

            for (colonne, ligne) in frontiere:
                cel_up = updated_tableau[colonne][ligne]
                voisins_cel = voisins[colonne, ligne]
                gel(cel_up)
                attachement(cel_up, voisins_cel, tableau_cellules)
                if not cel_up[0]:
                    fonte(cel_up)
                    bruit(cel_up)

            frontiere = frontiere_up.copy()
            tableau_cellules = dc(updated_tableau)
            if i % 25 == 0:
                generer_image(cristal)

    except KeyboardInterrupt:
        rep = input("Voulez vous effacer le dossier en cours ? ")
        if rep.lower() in ('o', 'oui'):
            rmtree(chemin, ignore_errors=True)
        raise KeyboardInterrupt
