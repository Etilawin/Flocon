# coding: utf-8
from math import sin, pi

W = 2000
H = 2000

T_HEXAGONES = 5
H_TABLEAU = int(H / (T_HEXAGONES * (1 + sin(pi / 3)))) + 2
W_TABLEAU = int(W / (2 * T_HEXAGONES)) + 2

H_TABLEAU += H_TABLEAU % 2
W_TABLEAU += W_TABLEAU % 2

ITERATIONS = 100

KAPPA = 0.8
BETA  = 1.7
ALPHA = 1.9
THETA = 0.25
RHO   = 2.0
MU    = 0.0005
GAMMA = 0.0005

SIGMA = 0.000
