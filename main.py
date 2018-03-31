import random
import copy
import os

W = 400
H = 400

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
    Retourne : Rien
    C.U : Aucune
    """
    for colonne in range(W):
        tableau_cellules.append([])
        for ligne in range(H):
            # Création de la cellule
            if ligne == H / 2 and colonne == W / 2:
                cellule = [True, 0, 1, 0]
                cristal.add((colonne, ligne))
            else:
                cellule = [False, 0, 0, RHO]
            tableau_cellules[colonne].append(cellule)
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

            voisins[colonne, ligne] = list(filter(lambda x: (x[0] != W and
                                                             x[1] != H and
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
        for colonne1, ligne1 in voisins[colonne, ligne]:
            if (colonne1, ligne1) not in cristal:
                frontiere_up.add((colonne1, ligne1))


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
    i=0
    while os.path.exists(base + str(i)):
        i += 1
    os.makedirs(base + str(i))
    return base + str(i)


if __name__ == "__main__":
    from PIL import Image

    initialiser()

    flocon = Image.new('RGB', (W, H))

    px = flocon.load()
    frontiere = set(x for x in voisins[W / 2, H / 2])

    chemin = create_folder()

    for i in range(3300):
        updated_tableau = copy.deepcopy(tableau_cellules)
        frontiere_up = frontiere.copy()
        for colonne in range(W):
            for ligne in range(H):
                cel = tableau_cellules[colonne][ligne]
                cel_up = updated_tableau[colonne][ligne]
                voisins_cel = voisins[colonne, ligne]
                if not cel[0]:
                    diffusion(cel, cel_up, voisins_cel)

        for (colonne, ligne) in frontiere:
            cel_up = updated_tableau[colonne][ligne]
            voisins_cel = voisins[colonne, ligne]
            gel(cel_up)
            attachement(cel_up, voisins_cel)
            if not cel_up[0]:
                fonte(cel_up)
                bruit(cel_up)
            px[colonne, ligne] = (i % 256, (i * i) % 256, (255 - i) % 256)

        frontiere = frontiere_up.copy()
        tableau_cellules = copy.deepcopy(updated_tableau)

        if i % 25 == 0:
            flocon.save(os.path.join(chemin, "image" + str(i//25) + ".jpg"))
