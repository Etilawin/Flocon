import random
import copy
import os
import shutil
# from pycallgraph import PyCallGraph
# from pycallgraph.output import GraphvizOutput
from math import pi, sin
from PIL import Image, ImageDraw

W = 2000
H = 2000

T_HEXAGONES = 5
H_TABLEAU = int(H / (T_HEXAGONES * (1 + sin(pi / 3)))) + 2
W_TABLEAU = int(W / (2 * T_HEXAGONES)) + 2

H_TABLEAU = H_TABLEAU if H_TABLEAU % 2 == 0 else H_TABLEAU + 1
W_TABLEAU = W_TABLEAU if W_TABLEAU % 2 == 0 else W_TABLEAU + 1

KAPPA = 0.6
BETA = 0.65
ALPHA = 0.7
THETA = 0.7
RHO = 1.1
MU = 0.5
GAMMA = 0.5

SIGMA = 0.000

tableau_cellules = []
voisins = {}
cristal = set()


def initialiser():
    """
    Fonction qui initialise le script en générant tableau_cellules et voisins au fur et à mesure
    Paramètre : Aucun
    Retourne : None
    C.U : Aucune
    """
    append = tableau_cellules.append
    for colonne in range(W_TABLEAU):
        append([])
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


def get_cel_voisin(cellules_voisines, n=-1):
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


def diffusion(cel, cel_up, voisins_cel):
    """
    Fonction qui effectue la diffusion de la vapeur d'une cellule sur ses voisins
    paramètre ligne : (int) la ligne de la cellule concernée
    paramètre colonne : (int) la colonne de la cellule concernée
    retourne : None
    C.U : None
    """
    if (colonne, ligne) not in frontiere:
        v = get_cel_voisin(voisins_cel, 3)
        moyenne = (cel[3] + sum(v)) / (len(v) + 1)
    else:
        v = get_cel_voisin(voisins_cel)
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


def attachement(cel_up, voisins_cel):
    """
    Fonction qui décide si la cellule doit se coller ou non au cristal
    paramètre ligne : (int) la ligne de la cellule concernée
    paramètre colonne : (int) la colonne de la cellule concernée
    retourne : None
    C.U : None
    """
    voisins_du_cristal = len([x for x in get_cel_voisin(voisins_cel) if x[0]])
    in_cristal = False
    if voisins_du_cristal <= 2:
        if cel_up[1] > BETA:
            in_cristal = True
    elif voisins_du_cristal == 3:
        somme_voisins = sum(get_cel_voisin(voisins_cel, 3))
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
        cristal.add((colonne, ligne))
        frontiere_up.remove((colonne, ligne))
        add = frontiere_up.add
        for colonne1, ligne1 in voisins[colonne, ligne]:
            if (colonne1, ligne1) not in cristal:
                add((colonne1, ligne1))


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
    i = random.randint(-1, 1)
    cel_up[3] *= 1 + i * SIGMA


def create_folder():
    """ Fonction qui créer un dossier pour stocker les images """
    base = "images_"
    i = 0
    while os.path.exists(base + str(i)):
        i += 1
    os.makedirs(base + str(i))
    return base + str(i)


def _mettre_a_lechelle(generateur, width, height, taille=50):
    height_echelle = int(height / taille) + 2
    width_echelle = int(width / taille) + 2

    for coordonnees in generateur(width_echelle, height_echelle):
        yield ([(x * taille, y * taille) for (x, y) in coordonnees[:-1]], coordonnees[-1])


def generer_unitee_hexagonal(width, height):
    """
    Créer les coordinnées d'un hexagones pour ensuite le passer à _mettre_a_lechelle puis à draw.polygon
    """
    # Moitié de la taille de l'hexagone
    l = sin(pi / 3)
    colonne = 0
    for x in range(-1, int(width / l) + 1):
        ligne = 0 if (x % 2 == 1) else 1
        for y in range(-1, height, 3):

            y_ = y if (x % 2 == 1) else y + 1.5

            color = (255,255,255)
            if (colonne,ligne) in cristal:
                color = (0,0,255)

            ligne += 2

            yield [
                (x * l,          y_),
                (x * l,          y_ + 1),
                ((x + 1) * l,    y_ + 1.5),
                ((x + 2) * l,    y_ + 1),
                ((x + 2) * l,    y_),
                ((x + 1) * l,    y_ - 0.5),
                color,
            ]
        if x % 2 == 0:
            colonne += 1


def generer_hexagones(*args, **kwargs):
    """Créer une grille hexagonale"""
    return _mettre_a_lechelle(generer_unitee_hexagonal, *args, **kwargs)


if __name__ == '__main__':

    initialiser()

    flocon = Image.new('RGB', (W, H))

    px = flocon.load()
    frontiere = set(x for x in voisins[W_TABLEAU / 2, H_TABLEAU / 2])

    chemin = create_folder()
    try:
        # Augmente la vitesse d'execution (https://wiki.python.org/moin/PythonSpeed/PerformanceTips)
        dc = copy.deepcopy
        join = os.path.join

        all_possibilities = []
        add_to_all = all_possibilities.append
        for colonne in range(W_TABLEAU):
            for ligne in range(H_TABLEAU):
                add_to_all((colonne, ligne))

        for i in range(3300):
            updated_tableau = dc(tableau_cellules)
            frontiere_up = frontiere.copy()

            for (colonne, ligne) in all_possibilities:  # Évite de recréer à chaque fois un range
                cel = tableau_cellules[colonne][ligne]
                if not cel[0]:
                    cel_up = updated_tableau[colonne][ligne]
                    voisins_cel = voisins[colonne, ligne]
                    diffusion(cel, cel_up, voisins_cel)

            for (colonne, ligne) in frontiere:
                cel_up = updated_tableau[colonne][ligne]
                voisins_cel = voisins[colonne, ligne]
                gel(cel_up)
                attachement(cel_up, voisins_cel)
                if not cel_up[0]:
                    fonte(cel_up)
                    bruit(cel_up)
                # px[colonne, ligne] = (i % 256, (i * i) % 256, (255 - i) % 256)

            frontiere = frontiere_up.copy()
            tableau_cellules = dc(updated_tableau)
            print(cristal)
            if i % 4 == 0:
                print("stop")
                for infos in generer_hexagones(W, H, taille=T_HEXAGONES):
                    shape = infos[0]
                    color = infos[-1]
                    ImageDraw.Draw(flocon).polygon(shape, fill=color)
                flocon.save(join(chemin, "image" + str(i // 4) + ".png"))
    except KeyboardInterrupt:
        rep = input("Voulez vous effacer le dossier en cours ? ")
        if rep.lower() in ('o', 'oui'):
            shutil.rmtree(chemin, ignore_errors=True)
        raise KeyboardInterrupt
