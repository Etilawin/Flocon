# coding: utf-8
""" Fichier contenant toute les constantes nécessaires à la croissance d'un flocon """
from math import sin, pi
from os.path import join, exists

CONSTANTES = {}

CONSTANTES['W'] = 2500
CONSTANTES['H'] = 2500

CONSTANTES['T_HEXAGONES'] = 5
CONSTANTES['H_TABLEAU'] = int(H / (T_HEXAGONES * (1 + sin(pi / 3)))) + 2
CONSTANTES['W_TABLEAU'] = int(W / (2 * T_HEXAGONES)) + 2

CONSTANTES['H_TABLEAU'] += CONSTANTES['H_TABLEAU'] % 2
CONSTANTES['W_TABLEAU'] += CONSTANTES['W_TABLEAU'] % 2

CONSTANTES['ITERATIONS'] = 5000

CONSTANTES['KAPPA']   = 0.8
CONSTANTES['BETA']    = 1.01
CONSTANTES['ALPHA']   = 0.9
CONSTANTES['THETA']   = 0.5
CONSTANTES['RHO']     = 1.9
CONSTANTES['MU']      = 0.0048
CONSTANTES['GAMMA']   = 0.0006
CONSTANTES['SIGMA']   = 0.000
