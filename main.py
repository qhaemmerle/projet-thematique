import calculs_elo as calc
import random


# Initialisation
nombre_equipes = 30
K = 100000
elo_equipes = []
elo_equipes_a = []
elo_equipes_d = []
liste_equipes = ["ANA", "ARI", "ATL", "BAL", "BOS", "CHC", "CHW", "CIN",
                 "CLE", "COL", "DET", "FLA", "HOU", "KCR", "LAD", "MIL",
                 "MIN", "NYM", "NYY", "OAK", "PHI", "PIT", "SDP", "SEA",
                 "SFG", "STL", "TBD", "TEX", "TOR", "WSN"]
BR = 100  # bankroll totale
f = 0.1  # part max de la BR misée chaque jour
n = 13  # nombre de matchs par journée théorique


# Application

# elo_equipes = calc.calcule_elo_ligue(elo_equipes, [13052, 37685], K)
# resultats = calc.parie_ligue_seuil_variable_fermeture(
#     elo_equipes, [10584, 13051], 1000, [0.3, 0.5], 0.01, K)
# print(resultats)

# elo_equipes = []
# # elo_equipes = calc.calcule_elo_ligue(
# #     elo_equipes, [2299, 4702], K)
# print(calc.compare_resultats_variation(
#     elo_equipes, [2299, 4702], [1000, 2298], 0.3, [0, 100], 0.1))

# # print(calcule_elo_ligue(elo_equipes_a, elo_equipes_d, [2299, 4702], 16))

# print(calculs_ad.compare_resultats_variation(elo_equipes_a, elo_equipes_d,
# [2299, 4702],
#                                   [1000, 2298], 0.3, [0, 9], 0.1))

# Résultats :
# Prédiction : [2013, 2016], Paris : {2017}, K = 32 :
#   - seuil = 0.5 : Matchs joués : 2468, Perte/€ : -0.06068028149345143
#   - seuil = 0.45 : Matchs joués : 1012, Perte/€ : -0.05947472557007782
#   - seuil = 0.4 : Matchs joués : 151, Perte/€ : -0.16313221214721513

# for i in range(80):
#     print(i, 1000 * (1.015346685185123658)**i)

# 789.2061333093754
# 798.1714966054946

# K_new, V_new = calc.calcule_vraisemblance_variation(
#     elo_equipes, [25416, 27844], [22911, 25415], [0, 64], 0.1)

# K_brut = calc.compare_resultats_variation(
#   elo_equipes, [25416, 27844], [22911, 25415], 0.5, [0, 64], 0.1)

# print(K_new, V_new)
# print(K_brut)

# 4.800000000000001, -731.8658122434797, 0.5504661532225374
# 34.300000000000004, , 0.5618159708147548)

# elo_equipes = calc.calcule_elo_ligue(elo_equipes, [25416, 27844], 4.8)
# proba = calc.compare_resultats(elo_equipes, [22911, 25377], 0.5, 4.8)
# print(proba[0])

# L = calc.plot_K_dates_variables(5000, 20000, 1000, 250, [0, 10], 0.5)
# calc.plot_K_duree_variable(100, 20000, 500, [0, 500], 5)

calc.plot_bankroll([16000, 30000], BR, f, n)
