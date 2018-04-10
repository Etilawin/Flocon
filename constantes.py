# coding: utf-8
"""
Auteur : Kim Vallée
Fichier contenant toute les constantes nécessaires à la croissance d'un flocon
"""
from math import sin, pi
from os.path import join, exists

W = 2000
H = 2000

T_HEXAGONES = 5
H_TABLEAU = int( (2/3) * int(H / T_HEXAGONES) + 2)
W_TABLEAU = int( ( int(W / T_HEXAGONES) + 2 ) / ( 2 * sin(pi / 3) ) + 1)

H_TABLEAU += H_TABLEAU % 2
W_TABLEAU += W_TABLEAU % 2

ITERATIONS = 5000

KAPPA = 0.8
BETA = 1.7
ALPHA = 1.9
THETA = 0.25
RHO = 2.0
MU = 0.0005
GAMMA = 0.0005
SIGMA = 0.001
