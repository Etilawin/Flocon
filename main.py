import random
import copy

W = 200
H = 200

k = 0.8
beta = 1.7
alpha = 1.9
theta = 0.25
rho = 2.0
mu = 0.0048
gamma = 0.0006

tableau_cellules = []
voisins = {}


def initialiser():
    """
    Fonction qui initialise le script en générant tableau_cellules et voisins au fur et à mesure
    Paramètre : Aucun
    Retourne : Rien
    C.U : Aucune
    """

    global voisins
    for ligne in range(H):
        tableau_cellules.append([])
        for colonne in range(W):
            # Création de la cellule
            if ligne == H / 2 and colonne == W / 2:
                cellule = [True, 0, 1, 0]
            else:
                cellule = [False, 0, 0, rho]
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
            voisins[ligne, colonne] = list(filter(lambda x: (x[0] != H and
                                                             x[1] != W and
                                                             x[0] != -1 and
                                                             x[1] != -1),
                                                  voisins[ligne, colonne]))


def moyenne_d(ligne, colonne, tableau_cellules):
    """
    Fonction qui fait la moyenne des d(x) entre la cellule et les cellules données
    paramètre cellule : (tuple) La cellule contenant toute les variables dont d(x) à l'indice 0
    paramètre voisin : (int) La ligne (pour pouvoir check les voisins)
    retourne : (float) La moyenne des d(x)
    C.U : Aucune
    """
    cel = tableau_cellules[ligne][colonne]
    v = get_cel_voisin(voisins[ligne, colonne], tableau_cellules)
    if (ligne, colonne) not in frontiere:
        return (cel[3] + sum([cellule[3] for cellule in v]))/(len(v) + 1)
    else:
        moyenne = cel[3]
        for cellule in v:
            if cellule[0]:
                moyenne += cel[3]
            else:
                moyenne += cellule[3]
        return moyenne/(len(v) + 1)

def diffusion(ligne, colonne, tableau_cellules):
    """
    Fonction qui effectue la diffusion de la vapeur d'une cellule sur ses voisins
    paramètre ligne : (int) la ligne de la cellule concernée
    paramètre colonne : (int) la colonne de la cellule concernée
    retourne : None
    C.U : None
    """
    cel = tableau_cellules[ligne][colonne]
    if not cel[0]:
        cel[3] = moyenne_d(ligne, colonne, tableau_cellules)


def gel(ligne, colonne, tableau_cellules):
    """
    Fonction qui effectue le gel pour la cellule
    paramètre ligne : (int) la ligne de la cellule concernée
    paramètre colonne : (int) la colonne de la cellule concernée
    retourne : None
    C.U : None
    """
    cel = tableau_cellules[ligne][colonne]
    if (ligne, colonne) in frontiere:
        cel[1] = cel[1] + (1 - k) * cel[3]
        cel[2] = cel[2] + k * cel[3]
        cel[3] = 0

def compte_voisins(ligne, colonne):
    """
    Fonction qui compte le nombre de voisins d'une cellule qui appartiennent au cristal
    paramètre ligne : (int) la ligne de la cellule
    paramètre colonne : (int) la colonne de la cellule
    retourne : Rien
    C.U : None
    """
    return len([x for x in get_cel_voisin(voisins[ligne, colonne], tableau_cellules) if x[0]])


def get_cel_voisin(voisin, tableau_cellules):
    """
    Fonction qui renvoi les cellules associés aux voisins sous forme d'une liste
    paramètre voisin : (list) Liste comprenant des voisins
    retourn : None
    C.U : None
    """
    cels = []
    for ligne, colonne in voisin:
        cels.append(tableau_cellules[ligne][colonne])
    return cels


def attachement(ligne, colonne, tableau_cellules):
    """
    Fonction qui décide si la cellule doit se coller ou non au cristal
    paramètre ligne : (int) la ligne de la cellule concernée
    paramètre colonne : (int) la colonne de la cellule concernée
    retourne : None
    C.U : None
    """
    cel = tableau_cellules[ligne][colonne]
    if (ligne, colonne) in frontiere:
        voisins_du_cristal = compte_voisins(ligne, colonne)
        in_cristal = False
        if voisins_du_cristal <= 2:
            if cel[1] > beta:
                in_cristal = True
        elif voisins_du_cristal == 3:
            somme_voisins = sum(
                [x[3] for x in get_cel_voisin(voisins[ligne, colonne], tableau_cellules)])
            if cel[1] >= 1:
                in_cristal = True
            elif somme_voisins < theta and cel[1] >= alpha:
                in_cristal = True
        elif voisins_du_cristal >= 4:
            in_cristal = True

        if in_cristal:
            cel[2] = cel[2] + cel[1]
            cel[1] = cel[3] = 0
            cel[0] = True
            frontiere.remove((ligne, colonne))
            for ligne1, colonne1 in voisins[ligne, colonne]:
                if not tableau_cellules[ligne1][colonne1][0]:
                    frontiere.add((ligne1, colonne1))


def fonte(ligne, colonne, tableau_cellules):
    """
    Fonction qui fait l'action contraire du gel sur une cellule
    paramètre ligne : (int) La ligne de la cellule concernée
    paramètre colonne : (int) La colonne de la cellule concernée
    retourne : None
    C.U : None
    """
    cel = tableau_cellules[ligne][colonne]
    if (ligne, colonne) in frontiere:
        cel[3] = cel[3] + mu * cel[1] + gamma * cel[2]
        cel[1] = (1 - mu) * cel[1]
        cel[2] = (1 - gamma) * cel[2]


def bruit(ligne, colonne, tableau_cellules):
    """
    Fonction qui ajoute de l'aléatoire dans la génération du flocon
    paramètre ligne : (int) La ligne de la cellule concernée
    paramètre colonne : (int) La colonne de la cellule concernée
    retourne : None
    C.U : None
    """
    cel = tableau_cellules[ligne][colonne]
    if not cel[0]:
        omega = random.randint(-1,1)*gamma
        cel[3] *= 1 + omega


def update(tableau_cellules, frontiere):
    """
    Fonction qui met à jour une cellule directement
    paramètre ligne : (int) la ligne de la cellule concernée
    paramètre colonne : (int) la colonne de la cellule concernée
    retourne : None
    C.U : None
    """
    for ligne in range(H):
        for colonne in range(W):
            if not tableau_cellules[ligne][colonne][0]:
                diffusion(ligne, colonne, tableau_cellules)
                gel(ligne, colonne, tableau_cellules)
                attachement(ligne, colonne, tableau_cellules)
                fonte(ligne, colonne, tableau_cellules)
                bruit(ligne, colonne, tableau_cellules)


if __name__ == "__main__":
    from PIL import Image
    initialiser()
    flocon = Image.new('RGB', (W, H))
    px = flocon.load()
    frontiere = set(x for x in voisins[H / 2, W / 2])
    for i in range(10000):
        update(tableau_cellules, frontiere)
    for ligne in range(H):
        for col in range(W):
            if tableau_cellules[ligne][col][0]:
                px[col, ligne] = (0,0,255)
    flocon.show()
