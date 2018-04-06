# coding: utf-8
""" Fichier contenant les principales fonctions de croissance du flocon """
from random import randint
from os.path import join, exists
from os import makedirs

import constantes

def initialiser(tableau_cellules, voisins, cristal, frontiere):
    """
    Fonction qui initialise le script en générant tableau_cellules et voisins au fur et à mesure
    Paramètres :
        - tableau_cellules : (list) le tableau contenant les cellules / molécules que l'on va mettre à jour
        - voisins          : (dict) Le dictionnaire qui contiendra les voisins de chaque ligne / colonne
        - cristal          : (set) Le cristal c.a.d ce qui contiendra les cellules gelées et rattachées au cristal. Les valeurs sont des tuples (colonne, ligne)
        - frontiere        : (set) La frontière c.a.d toutes les (colonnes, lignes) voisines du cristal
    Retourne : None
    C.U : Aucune
    """
    tableau_cellules.extend([[] for i in range(constantes.W_TABLEAU)])  # List comprehension is faster
    for colonne in range(constantes.W_TABLEAU):
        add_ligne = tableau_cellules[colonne].append
        for ligne in range(constantes.H_TABLEAU):
            # Création de la cellule
            if ligne == constantes.H_TABLEAU / 2 and colonne == constantes.W_TABLEAU / 2:
                cellule = [True, 0, 1, 0]
                cristal.add((colonne, ligne))
            else:
                cellule = [False, 0, 0, constantes.RHO]
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
            if ligne % 2 == 0:  # On ajoute les voisins pour éviter de les recalculer à chaque fois
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

            voisins[colonne, ligne] = list(filter(lambda x: (x[0] != constantes.W_TABLEAU and
                                                             x[1] != constantes.H_TABLEAU and
                                                             x[0] != -1 and
                                                             x[1] != -1),
                                                  voisins[colonne, ligne]))
    frontiere.update(voisins[constantes.W_TABLEAU / 2, constantes.H_TABLEAU / 2])


def get_cel_voisin(tableau_cellules, cellules_voisines, n=-1):
    """
    Fonction qui renvoi les cellules associés aux voisins sous forme d'une liste
    Paramètres :
        - tableau_cellules  : (list) le tableau contenant les cellules / molécules que l'on va mettre à jour
        - cellules_voisines : (list) Liste contenant les coordonées des cellules voisines pour lesquelles on veut les valeurs de n
        - n                 : (int)  Le paramètre que l'on veut récupérer. Si la valeur appartient à [[0;5]] Alors on renvoi cette valeur des cellules sinon on renvoi les cellules en elles même
    Retourne : (list) La liste contenant les valeurs de n des cellules voisines ou à défaut les cellules elles-même
    C.U : n doit être un entier (Mais nous sommes entre adultes consentants... N'est-ce pas ?)

    Exemple :
    >>> tableau_cellules = [[[0,1,0,2], [0,5,0,7]],
                            [[0,2,0,1], [0,3,0,2]]]
    >>> cellules_voisines = [(0,1), (1,0)]
    >>> get_cel_voisin(tableau_cellules, cellules_voisines, n=1)
    [5, 2]
    >>> get_cel_voisin(tableau_cellules, cellules_voisines, n=1)
    [[0,5,0,7], [0,2,0,1]]
    """
    if 0 <= n < 5:  # Si on donne un n valable on l'utilise ...
        return [tableau_cellules[colonne][ligne][n] for (colonne, ligne) in cellules_voisines]
    else:  # Sinon on renvoi les cellules en entier
        return [tableau_cellules[colonne][ligne] for (colonne, ligne) in cellules_voisines]


def diffusion(tableau_cellules, updated_tableau, voisins, all_possibilities):
    """
    Fonction qui effectue la diffusion de la vapeur d'une cellule sur ses voisins
    Paramètres :
        - tableau_cellules  : (list) Le tableau contenant les cellules / molécules que l'on va mettre à jour
        - updated_tableau   : (list) Une copie de tableau_cellules pour tout mettre à jour d'un seul coup
        - voisins           : (dict) Le dictionnaire qui contiendra les voisins de chaque ligne / colonne
        - all_possibilities : (list) Liste contenant toute les possibilités d'associations de liste / colonne
    Retourne : None
    C.U : None
    """
    for (colonne, ligne) in all_possibilities:
        cel = tableau_cellules[colonne][ligne]
        cel_up = updated_tableau[colonne][ligne]
        voisins_de_cellule = voisins[colonne, ligne]
        cellules_voisines = get_cel_voisin(tableau_cellules, voisins_de_cellule)

        moyenne = cel[3]
        for cellule_voisine in cellules_voisines:
            # Si la cellule voisine est dans le cristal on ajoute seulement la
            # valeur de la cellule actuelle sinon on ajoute la veleur d(x) des
            # cellules voisines
            if cellule_voisine[0]:
                moyenne += cel[3]
            else:
                moyenne += cellule_voisine[3]
        moyenne /= (len(voisins_de_cellule) + 1)

        cel_up[3] = moyenne


def gel(cel_up):
    """
    Fonction qui effectue le gel pour la cellule
    Paramètres :
        - cel_up : (list) La cellule concernée que l'on veut mettre à jour à la frontiere
    Retourne : None
    C.U : None
    """
    # Voir sujet ... Rien de plus à expliqer !
    cel_up[1] = cel_up[1] + (1 - constantes.KAPPA) * cel_up[3]
    cel_up[2] = cel_up[2] + constantes.KAPPA * cel_up[3]
    cel_up[3] = 0


def attachement(cel_up, voisins_cel, tableau_cellules):
    """
    Fonction qui décide si la cellule doit se coller ou non au cristal
    Paramètres :
        - cel_up            : (list) La cellule concernée que l'on veut mettre à jour à la frontiere
        - voisins_cel       : (list) Liste contenant tout les voisins de la cellule cel_up sous forme (colonne, ligne)
        - tableau_cellules  : (list) Le tableau contenant les cellules / molécules que l'on va mettre à jour
    Retourne : None
    C.U : None
    """
    # Une petite explication quand même :
    # on fait la somme des True et False dans la liste des voisins
    # Sachant que True = 1 et False = 0 la somme sera égale au nombre de voisins
    voisins_du_cristal = sum(get_cel_voisin(tableau_cellules, voisins_cel, 0))
    in_cristal = False
    if voisins_du_cristal <= 2:
        if cel_up[1] > constantes.BETA:
            in_cristal = True

    elif voisins_du_cristal == 3:
        # La somme des d(x) voisins
        somme_voisins = sum(get_cel_voisin(tableau_cellules, voisins_cel, 3))
        if cel_up[1] >= 1:
            in_cristal = True
        elif somme_voisins < constantes.THETA and cel_up[1] >= constantes.ALPHA:
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
    Paramètres :
        - cel_up : (list) La cellule concernée que l'on veut mettre à jour à la frontiere
    Retourne : None
    C.U : None
    """
    cel_up[3] = cel_up[3] + constantes.MU * cel_up[1] + constantes.GAMMA * cel_up[2]
    cel_up[1] = (1 - constantes.MU) * cel_up[1]
    cel_up[2] = (1 - constantes.GAMMA) * cel_up[2]


def bruit(cel_up):
    """
    Fonction qui ajoute de l'aléatoire dans la génération du flocon
    Paramètres :
        - cel_up : (list) La cellule concernée que l'on veut mettre à jour à la frontiere
    Retourne : None
    C.U : None
    """
    i = randint(-1, 1)  # On additionne ou on soustrait ?
    cel_up[3] *= 1 + i * constantes.SIGMA


def update_frontiere(colonne, ligne, cristal, frontiere_up, voisins, all_possibilities):
    """
    Fonction qui met à jour la frontière
    Paramètres :
        - colonne           : (int) La colonne correspondant à la cellule
        - ligne             : (int) La ligne correspondant à la cellule
        - cristal           : (set) Le cristal c.a.d ce qui contiendra les cellules gelées et rattachées au cristal. Les valeurs sont des tuples (colonne, ligne)
        - frontiere_up      : (set) La frontière mis à jour
        - voisins           : (dict) Le dictionnaire qui contiendra les voisins de chaque ligne / colonne
        - all_possibilities : (list) Liste contenant toute les possibilités d'associations de liste / colonne
    Retourne : None
    C.U : None (adultes consentants tout ça)
    """
    # Si on est ici c'est qu'il y a eu attachement au cristal
    # donc on ajoute au cristal
    cristal.add((colonne, ligne))
    frontiere_up.remove((colonne, ligne))
    add = frontiere_up.add
    for colonne1, ligne1 in voisins[colonne, ligne]:
        if (colonne1, ligne1) not in cristal:
            add((colonne1, ligne1))


def create_folder(chemin):
    """
    Fonction qui créer un dossier pour stocker les images
    Paramètres :
        - chemin : (str) le chemin où seront stockées les images
    Retourne : None
    C.U : None
    """
    try:
        makedirs(chemin)
    except FileExistsError:
        pass # Le dossier existe déjà pas besoin de le recréer
    base = join(chemin, "images_")
    i = 0
    while exists(base + str(i)):
        i += 1
    makedirs(base + str(i))
    return base + str(i)

def load_constants(path):
    """
    Fonction qui charge les constantes d'un dossier
    Paramètres :
        - path : (str) le chemin où se trouvent les constantes
    Retourne : None
    C.U : None
    """
    consts = [("kappa", constantes.KAPPA),
              ("beta", constantes.BETA),
              ("alpha", constantes.ALPHA),
              ("theta", constantes.THETA),
              ("rho", constantes.RHO),
              ("mu", constantes.MU),
              ("gamma", constantes.GAMMA),
              ("sigma", constantes.SIGMA)]


    with open(path, "rt") as f:
        contenu = f.read()

    contenu = contenu.lower().split("\n")
    for line in contenu:
        for name, value in consts:
            try :
                line.index(name)
                egal = line.index('=')
                value = float(line[egal + 1:])
            except ValueError:
                pass
