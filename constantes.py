# coding: utf-8
""" Fichier contenant toute les constantes nécessaires à la croissance d'un flocon """
from math import sin, pi
from os.path import join, exists

CONSTANTES = {}

CONSTANTES['W'] = 1800
CONSTANTES['H'] = 1800

CONSTANTES['T_HEXAGONES'] = 2
CONSTANTES['H_TABLEAU'] = int(CONSTANTES['H'] / (CONSTANTES['T_HEXAGONES'] * (1 + sin(pi / 3)))) + 2
CONSTANTES['W_TABLEAU'] = int(CONSTANTES['W'] / (2 * CONSTANTES['T_HEXAGONES'])) + 2

CONSTANTES['H_TABLEAU'] += CONSTANTES['H_TABLEAU'] % 2
CONSTANTES['W_TABLEAU'] += CONSTANTES['W_TABLEAU'] % 2

CONSTANTES['ITERATIONS'] = 5000

CONSTANTES['KAPPA']   = 0.5
CONSTANTES['BETA']    = 1.5
CONSTANTES['ALPHA']   = 0.9
CONSTANTES['THETA']   = 0.4
CONSTANTES['RHO']     = 1.5
CONSTANTES['MU']      = 0.00015
CONSTANTES['GAMMA']   = 0.00001
CONSTANTES['SIGMA']   = 0.001
