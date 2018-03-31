import random
import copy

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
    for ligne in range(H):
        tableau_cellules.append([])
        for colonne in range(W):
            # Création de la cellule
            if ligne == H / 2 and colonne == W / 2:
                cellule = [True, 0, 1, 0]
                cristal.add((ligne, colonne))
            else:
                cellule = [False, 0, 0, RHO]
            tableau_cellules[ligne].append(cellule)
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
                voisins[ligne, colonne] = [(ligne - 1, colonne - 1),
                                           (ligne - 1, colonne),
                                           (ligne, colonne - 1),
                                           (ligne, colonne + 1),
                                           (ligne + 1, colonne - 1),
                                           (ligne + 1, colonne)]
            else:
                voisins[ligne, colonne] = [(ligne - 1, colonne),
                                           (ligne - 1, colonne + 1),
                                           (ligne, colonne - 1),
                                           (ligne, colonne + 1),
                                           (ligne + 1, colonne),
                                           (ligne + 1, colonne + 1)]

            voisins[ligne, colonne] = list(filter(lambda x: (x[1] != W and
                                               x[0] != H and
                                               x[0] != -1 and
                                               x[1] != -1),
                                    voisins[ligne, colonne]))


def get_cel_voisin(cellules_voisines, n=-1):
    """
    Fonction qui renvoi les cellules associés aux voisins sous forme d'une liste
    paramètre voisin : (list) Liste comprenant des voisins
    retourn : None
    C.U : None
    """
    if 0 <= n < 5:
        return [tableau_cellules[ligne][colonne][n] for (ligne, colonne) in cellules_voisines]
    else:
        return [tableau_cellules[ligne][colonne] for (ligne, colonne) in cellules_voisines]


def diffusion(cel_up, voisins_cel):
    """
    Fonction qui effectue la diffusion de la vapeur d'une cellule sur ses voisins
    paramètre ligne : (int) la ligne de la cellule concernée
    paramètre colonne : (int) la colonne de la cellule concernée
    retourne : None
    C.U : None
    """
    if (ligne, colonne) not in frontiere:
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
    voisins_du_cristal = len([x for x in voisins_cel if x in cristal])
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
        cristal.add((ligne, colonne))
        frontiere_up.remove((ligne, colonne))
        for ligne1, colonne1 in voisins[ligne, colonne]:
            if (ligne1, colonne1) not in cristal:
                frontiere_up.add((ligne1, colonne1))


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


if __name__ == "__main__":
    from PIL import Image

    initialiser()

    flocon = Image.new('RGB', (W, H))

    px = flocon.load()
    frontiere = set(x for x in voisins[H / 2, W / 2])

    for i in range(3300):
        updated_tableau = copy.deepcopy(tableau_cellules)
        frontiere_up = frontiere.copy()
        for ligne in range(H):
            for colonne in range(W):
                cel = tableau_cellules[ligne][colonne]
                cel_up = updated_tableau[ligne][colonne]
                voisins_cel = voisins[ligne, colonne]
                diffusion(cel_up, voisins_cel)

        for (ligne, colonne) in frontiere:
            cel_up = updated_tableau[ligne][colonne]
            voisins_cel = voisins[ligne, colonne]
            gel(cel_up)
            attachement(cel_up, voisins_cel)
            if not cel_up[0]:
                fonte(cel_up)
                bruit(cel_up)

        frontiere = frontiere_up.copy()
        tableau_cellules = copy.deepcopy(updated_tableau)

        for (ligne, colonne) in frontiere:
            px[colonne, ligne] = (i % 256, (i * i) % 256, (255 - i) % 256)

        if i % 25 == 0:
            flocon.show()
