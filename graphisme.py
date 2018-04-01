from math import pi, sin
from PIL import Image, ImageDraw


def _mettre_a_lechelle(generateur, width, height, taille=50):
    height_echelle = int(height / taille) + 2
    width_echelle = int(width / taille) + 2

    for coordonnees in generateur(width_echelle, height_echelle):
        yield [(x * taille, y * taille) for (x, y) in coordonnees]


def generer_unitee_hexagonal(width, height):
    """
    Créer les coordinnées d'un hexagones pour ensuite le passer à _mettre_a_lechelle puis à draw.polygon
    """
    # Let s be the length of one side of the hexagon, and h the height
    # of the entire hexagon if one side lies parallel to the x-axis.
    #
    # The for loops (x, y) give the coordinate of one coordinate of the
    # hexagon, and the remaining coordinates fall out as follows:
    #
    #                     (x, y) +-----+ (x + 1, y)
    #                           /       \
    #                          /         \
    #        (x - 1/2, y + h) +           + (x + 3/2, y + h)
    #                          \         /
    #                           \       /
    #                (x, y + 2h) +-----+ (x + 1, y + 2h)
    #
    # In each row we generate hexagons in the following pattern
    #
    #         /‾‾‾\   /‾‾‾\   /‾‾‾\
    #         \___/   \___/   \___/
    #
    # and the next row is offset to fill in the gaps. So after two rows,
    # we'd have the following pattern:
    #
    #         /‾‾‾\   /‾‾‾\   /‾‾‾\
    #         \___/‾‾‾\___/‾‾‾\___/‾‾‾\
    #             \___/   \___/   \___/
    #
    # There are offsets to ensure we fill the entire canvas.

    # Moitié de la taille de l'hexagone
    l = sin(pi / 3)
    colonne = 0
    for x in range(-1, int(width / l) + 1):
        ligne = 0 if (x % 2 == 1) else 1
        for y in range(-1, height, 3):

            y_ = y if (x % 2 == 0) else y + 1.5

            color = (0,0,0)
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
            ]
        colonne = colonne + 1 if (x % 2 == 0) else colonne

    # for x in range(-1, width, 3):
    #     for y in range(-1, int(height / h) + 1):
    #
    #         # On shift 1 ligne sur 2 pour obtenir quelque chose comme :
    #         #
    #         #         /‾‾‾\   /‾‾‾\   /‾‾‾\
    #         #         \___/‾‾‾\___/‾‾‾\___/‾‾‾\
    #         #             \___/   \___/   \___/
    #         #
    #         x_ = x if (y % 2 == 0) else x + 1.5
    #
    #         yield [
    #             (x_,        y * h),
    #             (x_ + 1,    y * h),
    #             (x_ + 1.5, (y + 1) * h),
    #             (x_ + 1,   (y + 2) * h),
    #             (x_,       (y + 2) * h),
    #             (x_ - 0.5, (y + 1) * h)
    #         ]


def generer_hexagones(*args, **kwargs):
    """Créer une grille hexagonale"""
    return _mettre_a_lechelle(generer_unitee_hexagonal, *args, **kwargs)


if __name__ == "__main__":
    im = Image.new(mode="RGB", size=(800, 800), color=0)
    for coords in generer_hexagones(800, 800, taille=50):
        ImageDraw.Draw(im).polygon(coords, outline="black", fill="white")
    im.show()
