# coding: utf-8
"""
Auteur : Kim Vallée
Le fichier principal contenant l'action même de générer le flocon et de gérer le script
"""
if __name__ == "__main__":
    ## from pycallgraph import PyCallGraph
    ## from pycallgraph.output import GraphvizOutput
    from argparse import ArgumentParser  # On invoque le dieu du scripting
    from copy import deepcopy as dc
    from os.path import join
    from shutil import rmtree

    from fonctions_process import *
    from graphismes import *
    import constantes

    parser = ArgumentParser(
        description="Parser comprenant tout les paramètres possibles et imaginables")
    parser.add_argument("-c", nargs=1, type=str,
                        required=False, default=None, metavar="file.txt",
                        help="Les fichier contenant les constantes, une ligne devrait être sauté entre chaque constante et de la forme KAPPA=1.2, les constantes manquantes seront mises par défaut")
    parser.add_argument("-i", nargs=1, type=int,
                        required=False, default=5000, metavar="Iterations",
                        help="Le nombre d'itérations pour le flocon")
    parser.add_argument("-p", nargs=1, type=str,
                        required=False, default="images", metavar="photos",
                        help="Le chemin où vous voulez que les photos soient stockées")
    parser.add_argument("-t", nargs=1, type=int,
                        required=False, default=5, metavar="taille",
                        help="La taille des hexagones")
    parser.add_argument("--rate", nargs=1, type=int,
                        required=False, default=25, metavar="framerate",
                        help="Tout les combien de framerates vous voulez sauvegarder une image")
    parser.add_argument("--width", nargs=1, type=int,
                        required=False, default=2000, metavar="W",
                        help="La largeur de l'image, va avec l'option --height")
    parser.add_argument("--height", nargs=1, type=int,
                        required=False, default=2000, metavar="H",
                        help="La hauteur de l'image, va avec l'option --width")
    parser.add_argument("--test", action="store_true", required=False,
                        help="Lance une vérification du programme, tout les autres paramètres sont ignorés")
    arguments = vars(parser.parse_args())

    if arguments['test']:
        constantes.ITERATIONS = 26
    else:
        if arguments['c']:
            try:
                load_constants(arguments['c'])
            except:
                print(
                    "Erreur lors de la lecture du fichier, les variables par défaut seront prises")

        constantes.ITERATIONS = abs(arguments['i'])

        constantes.T_HEXAGONES = abs(arguments['t'])

        if arguments['width'] != 2000:
            constantes.W = abs(arguments['width'])
            constantes.W_TABLEAU = int( ( int(constantes.W / constantes.T_HEXAGONES) + 2 ) / ( 2 * sin(pi / 3) ) + 1)
            constantes.W_TABLEAU += constantes.W_TABLEAU % 2

        if arguments['height']:
            constantes.H = abs(arguments['height'])
            constantes.H_TABLEAU = int( (2/3) * int(constantes.H / constantes.T_HEXAGONES) + 2)
            constantes.H_TABLEAU += constantes.H_TABLEAU % 2
    chemin_image = arguments['p']
    rate = abs(arguments['rate'])

    # https://docs.python.org/3.3/library/argparse.html#argparse.ArgumentParser.add_argument
    tableau_cellules = []
    voisins = {}
    cristal = set()
    frontiere = set()

    initialiser(tableau_cellules, voisins, cristal, frontiere)

    chemin = create_folder(chemin_image)

    all_possibilities = set()
    add_to_all = all_possibilities.add
    for colonne in range(constantes.W_TABLEAU):
        for ligne in range(constantes.H_TABLEAU):
            add_to_all((colonne, ligne))

    all_possibilities.difference_update(cristal)

    try:
        for i in range(constantes.ITERATIONS):
            updated_tableau = dc(tableau_cellules)
            frontiere_up = frontiere.copy()

            # Mettre la boucle à l'intérieur de la fonction augmente considérablement le temps d'execution (environ 4*)
            # https://wiki.python.org/moin/PythonSpeed/PerformanceTips#Data_Aggregation
            diffusion(tableau_cellules, updated_tableau,
                      voisins, all_possibilities)

            for (colonne, ligne) in frontiere:
                cel_up = updated_tableau[colonne][ligne]
                voisins_cel = voisins[colonne, ligne]
                gel(cel_up)
                attachement(cel_up, voisins_cel, tableau_cellules)
                if cel_up[0]:  # Si elle vient d'être rattaché au cristal
                    update_frontiere(colonne, ligne, cristal,
                                     frontiere_up, voisins, all_possibilities)
                else:  # Sinon
                    fonte(cel_up)
                    bruit(cel_up)

            # On retire les quelques cellules du cristal ce qui permet des itérations moins longues
            all_possibilities.difference_update(cristal)
            frontiere = frontiere_up.copy()
            tableau_cellules = dc(updated_tableau)

            if i % rate == 0:
                generer_image(chemin, cristal, i // rate)

    except KeyboardInterrupt:
        rep = input("Voulez vous effacer le dossier en cours ? ")
        if rep.lower() in ('o', 'oui'):
            rmtree(chemin, ignore_errors=True)
        raise KeyboardInterrupt

    if arguments['test']:
        rmtree(chemin, ignore_errors=True)
        print("Tout s'est déroulé correctement, le programme marche")
