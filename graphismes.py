# coding: utf-8
""" Fichier contenant toutes les fonctions lié au graphisme """
from PIL import Image, ImageDraw
from math import sin, pi
from os.path import join

from constantes import CONSTANTES


def _mettre_a_lechelle(generateur, width, height, cristal, taille=5):
    """
    Générateur qui génère les coordinnées mise à l'échelle de chaque hexagone
    Paramètres :
        - generateur : (generator) Le générateur de coordinées unitaires
        - width      : (int) La largeur de l'image
        - height     : (int) La hauteur de l'image
        - cristal    : (set) Le cristal c.a.d ce qui contiendra les cellules gelées et rattachées au cristal. Les valeurs sont des tuples (colonne, ligne)
        - taille     : (int) La taille de chaque hexagone
    Génère : (tuple) Un tuple contenant les coordinées mise à l'échelle et la couleur de l'hexagone
    C.U : None

    Exemple :

    >>> list(_mettre_a_lechelle(generer_unitee_hexagonal, 2, 2, {(1,2), (1,1)}, 1))
    [([(-0.8660254037844386, -1), (-0.8660254037844386, 0), (0.0, 0.5), (0.8660254037844386, 0), (0.8660254037844386, -1), (0.0, -1.5)], (0, 0, 0)),
    ...
    ([(3.4641016151377544, 3.5), (3.4641016151377544, 4.5), (4.330127018922193, 5.0), (5.196152422706632, 4.5), (5.196152422706632, 3.5), (4.330127018922193, 3.0)], (0, 0, 0))]
    """
    # On divise la hauteur et la largeur par la taille
    # Et on ajoute 2 pour être sûr de remplir
    height_echelle = int(height / taille) + 2
    width_echelle = int(width / taille) + 2

    for coordonnees in generateur(width_echelle, height_echelle, cristal):
        yield ([(x * taille, y * taille) for (x, y) in coordonnees[:-1]], coordonnees[-1])


def generer_unitee_hexagonal(width, height, cristal):
    """
    Créer les coordinnées d'un hexagones pour ensuite le passer à _mettre_a_lechelle puis à draw.polygon
    Paramètres :
        - width      : (int) La largeur de l'image
        - height     : (int) La hauteur de l'image
        - cristal    : (set) Le cristal c.a.d ce qui contiendra les cellules gelées et rattachées au cristal. Les valeurs sont des tuples (colonne, ligne)
    Génère : (list) Liste contenant les coordinées unitaires
    C.U : None

    Exemple :

    >>> list(generer_unitee_hexagonal(2, 2, {(1,2), (1,1)}))
    [[(-0.8660254037844386, -1), (-0.8660254037844386, 0), (0.0, 0.5), (0.8660254037844386, 0), (0.8660254037844386, -1), (0.0, -1.5), (0, 0, 0)],
    ...
     [(1.7320508075688772, 0.5), (1.7320508075688772, 1.5), (2.598076211353316, 2.0), (3.4641016151377544, 1.5), (3.4641016151377544, 0.5), (2.598076211353316, 0.0), (89, 133, 111)]]
    """
    # On génère colonne par colonne
    # La première colonne on commence par le premier et on en fait une ligne sur 2
    # La deuxième colonne est en fait toujours la première
    # Et on fait une ligne sur 2 encore une fois
    # Pour mieux comprendre : https://www.redblobgames.com/grids/hexagons/#coordinates-offset


    # Moitié de la taille de l'hexagone (SOHCAHTOA)
    l = sin(pi / 3)
    colonne = 0
    for x in range(-1, int(width / l) + 1):
        ligne = 0 if (x % 2 == 1) else 1
        for y in range(-1, height, 3):

            y_ = y if (x % 2 == 1) else y + 1.5

            color = (0, 0, 0)
            if (colonne, ligne) in cristal:
                dx = abs(CONSTANTES['W_TABLEAU'] - colonne) % 256
                dy = abs(CONSTANTES['H_TABLEAU'] - ligne) % 256
                color = (dx, dy, (dx + dy) // 2)

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
        colonne = (colonne + 1) if (x % 2 == 0) else colonne


def generer_hexagones(*args, **kwargs):
    """
    Créer une grille hexagonale
    Paramètres :
        - args    : (list) Les arguments
        - kwargs  : (dict) Les arguments nommés
    C.U : args doit au minimum contenir 2 valeurs (width et height) et kwargs doit contenir au minimum le cristal donnée comme cristal=...

    Exemple :

    >>> list(generer_hexagones(5, 5, taille=2, cristal={(1,1), (1,2)}))
    [([(-1.7320508075688772, -2), (-1.7320508075688772, 0), (0.0, 1.0), (1.7320508075688772, 0), (1.7320508075688772, -2), (0.0, -3.0)], (0, 0, 0)),
    ...
     ([(6.928203230275509, 7.0), (6.928203230275509, 9.0), (8.660254037844386, 10.0), (10.392304845413264, 9.0), (10.392304845413264, 7.0), (8.660254037844386, 6.0)], (0, 0, 0))]
    """
    return _mettre_a_lechelle(generer_unitee_hexagonal, *args, **kwargs)


def generer_image(path, cr, n):
    """
    Fonction qui génère une image dans un chemin donnée avec le cristal et n le numéro que l'on veut donner à l'image
    Paramètres :
        - path : (str) Chaîne de caractères contenant le chemin d'accès au fichier
        - cr   : (set) Le cristal c.a.d ce qui contiendra les cellules gelées et rattachées au cristal. Les valeurs sont des tuples (colonne, ligne)
        - n    : (int) Le numéro de l'image
    """
    flocon = Image.new('RGB', (CONSTANTES['W'], CONSTANTES['H']))
    for infos in generer_hexagones(CONSTANTES['W'], CONSTANTES['H'], taille=CONSTANTES['T_HEXAGONES'], cristal=cr):
        shape = infos[0]
        color = infos[-1]
        ImageDraw.Draw(flocon).polygon(shape, fill=color)
    flocon.save(join(path, "image" + str(n) + ".png"))
