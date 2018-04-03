# coding: utf-8
""" Fichier contenant les principales fonctions de croissance du flocon """
from random import randint
from os.path import join, exists
from os import makedirs

from constantes import *

def initialiser(tableau_cellules, voisins, cristal, frontiere):
    """
    Fonction qui initialise le script en générant tableau_cellules et voisins au fur et à mesure
    Paramètre :
        - tableau_cellules : (list) le tableau contenant les cellules / molécules que l'on va mettre à jour
        - voisins          : (dictionnaire) Le dictionnaire qui contiendra les voisins de chaque ligne / colonne
        - cristal          : (set) Le cristal c.a.d ce qui contiendra les cellules gelées et rattachées au cristal. Les valeurs sont des tuples (colonne, ligne)
        - frontiere        : (set) La frontière c.a.d toutes les (colonnes, lignes) voisines du cristal
    Retourne : None
    C.U : Aucune
    """
    tableau_cellules.extend([[] for i in range(W_TABLEAU)]) # List comprehension is faster
    for colonne in range(W_TABLEAU):
        add_ligne = tableau_cellules[colonne].append
        for ligne in range(H_TABLEAU):
            # Création de la cellule
            if ligne == H_TABLEAU / 2 and colonne == W_TABLEAU / 2:
                cellule = [True, 0, 1, 0]
                cristal.add((colonne, ligne))
            else:
                cellule = [False, 0, 0, RHO]
            add_ligne(cellule)
            # Coordonées des voisins
            # Lignes...
            # ...Pairs :
            # 1 1 0
            # 1 x 1
            # 1 1 0
            # ...Impairs :
            # 0 1 1
            # 1 x 1
            # 0 1 1
            if ligne % 2 == 0:
                voisins[colonne, ligne] = [(colonne - 1, ligne - 1),
                                           (colonne - 1, ligne),
                                           (colonne - 1, ligne + 1),
                                           (colonne, ligne - 1),
                                           (colonne, ligne + 1),
                                           (colonne + 1, ligne)]
            else:
                voisins[colonne, ligne] = [(colonne - 1, ligne),
                                           (colonne, ligne - 1),
                                           (colonne, ligne + 1),
                                           (colonne + 1, ligne - 1),
                                           (colonne + 1, ligne),
                                           (colonne + 1, ligne + 1)]

            voisins[colonne, ligne] = list(filter(lambda x: (x[0] != W_TABLEAU and
                                                             x[1] != H_TABLEAU and
                                                             x[0] != -1 and
                                                             x[1] != -1),
                                                  voisins[colonne, ligne]))
    frontiere.update(voisins[W_TABLEAU / 2, H_TABLEAU / 2])


def get_cel_voisin(tableau_cellules, cellules_voisines, n=-1):
    """
    Fonction qui renvoi les cellules associés aux voisins sous forme d'une liste
    paramètre voisin : (list) Liste comprenant des voisins
    retourn : None
    C.U : None
    """
    if 0 <= n < 5:
        return [tableau_cellules[colonne][ligne][n] for (colonne, ligne) in cellules_voisines]
    else:
        return [tableau_cellules[colonne][ligne] for (colonne, ligne) in cellules_voisines]


def diffusion(cel, cel_up, voisins_cel, tableau_cellules):
    """
    Fonction qui effectue la diffusion de la vapeur d'une cellule sur ses voisins
    paramètre ligne : (int) la ligne de la cellule concernée
    paramètre colonne : (int) la colonne de la cellule concernée
    retourne : None
    C.U : None
    """
    v = get_cel_voisin(tableau_cellules, voisins_cel)
    moyenne = cel[3]
    for cellule in v:
        if cellule[0]:
            moyenne += cel[3]
        else:
            moyenne += cellule[3]
    moyenne /= (len(v) + 1)

    cel_up[3] = moyenne


def gel(cel_up):
    """
    Fonction qui effectue le gel pour la cellule
    paramètre ligne : (int) la ligne de la cellule concernée
    paramètre colonne : (int) la colonne de la cellule concernée
    retourne : None
    C.U : None
    """
    cel_up[1] = cel_up[1] + (1 - KAPPA) * cel_up[3]
    cel_up[2] = cel_up[2] + KAPPA * cel_up[3]
    cel_up[3] = 0


def attachement(cel_up, voisins_cel, tableau_cellules):
    """
    Fonction qui décide si la cellule doit se coller ou non au cristal
    paramètre ligne : (int) la ligne de la cellule concernée
    paramètre colonne : (int) la colonne de la cellule concernée
    retourne : None
    C.U : None
    """
    voisins_du_cristal = len([x for x in get_cel_voisin(tableau_cellules, voisins_cel) if x[0]])
    in_cristal = False
    if voisins_du_cristal <= 2:
        if cel_up[1] > BETA:
            in_cristal = True
    elif voisins_du_cristal == 3:
        somme_voisins = sum(get_cel_voisin(tableau_cellules, voisins_cel, 3))
        if cel_up[1] >= 1:
            in_cristal = True
        elif somme_voisins < THETA and cel_up[1] >= ALPHA:
            in_cristal = True
    elif voisins_du_cristal >= 4:
        in_cristal = True

    if in_cristal:
        cel_up[2] = cel_up[2] + cel_up[1]
        cel_up[1] = cel_up[3] = 0
        cel_up[0] = True

def fonte(cel_up):
    """
    Fonction qui fait l'action contraire du gel sur une cellule
    paramètre ligne : (int) La ligne de la cellule concernée
    paramètre colonne : (int) La colonne de la cellule concernée
    retourne : None
    C.U : None
    """
    cel_up[3] = cel_up[3] + MU * cel_up[1] + GAMMA * cel_up[2]
    cel_up[1] = (1 - MU) * cel_up[1]
    cel_up[2] = (1 - GAMMA) * cel_up[2]


def bruit(cel_up):
    """
    Fonction qui ajoute de l'aléatoire dans la génération du flocon
    paramètre ligne : (int) La ligne de la cellule concernée
    paramètre colonne : (int) La colonne de la cellule concernée
    retourne : None
    C.U : None
    """
    i = randint(-1, 1)
    cel_up[3] *= 1 + i * SIGMA

def update_frontiere(colonne, ligne, cristal, frontiere_up, voisins):
    """ Met à jour la frontière """
    cristal.add((colonne, ligne))
    frontiere_up.remove((colonne, ligne))
    add = frontiere_up.add
    for colonne1, ligne1 in voisins[colonne, ligne]:
        if (colonne1, ligne1) not in cristal:
            add((colonne1, ligne1))

def create_folder():
    """ Fonction qui créer un dossier pour stocker les images """
    base = join("images", "images_")
    i = 0
    while exists(base + str(i)):
        i += 1
    makedirs(base + str(i))
    return base + str(i)
