# coding: utf-8
from PIL import Image, ImageDraw
from math import sin, pi
from os.path import join

from constantes import CONSTANTES


def _mettre_a_lechelle(generateur, width, height, cristal, taille=50):
    height_echelle = int(height / taille) + 2
    width_echelle = int(width / taille) + 2

    for coordonnees in generateur(width_echelle, height_echelle, cristal):
        yield ([(x * taille, y * taille) for (x, y) in coordonnees[:-1]], coordonnees[-1])


def generer_unitee_hexagonal(width, height, cristal):
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


def generer_hexagones(*args, **kwargs):
    """Créer une grille hexagonale"""
    return _mettre_a_lechelle(generer_unitee_hexagonal, *args, **kwargs)


def generer_image(path, cr, n):
    flocon = Image.new('RGB', (CONSTANTES['W'], CONSTANTES['H']))
    for infos in generer_hexagones(CONSTANTES['W'], CONSTANTES['H'], taille=CONSTANTES['T_HEXAGONES'], cristal=cr):
        shape = infos[0]
        color = infos[-1]
        ImageDraw.Draw(flocon).polygon(shape, fill=color)
    flocon.save(join(path, "image" + str(n) + ".png"))
