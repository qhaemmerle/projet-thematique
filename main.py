import calculs_elo as calculs


# Initialisation
nombre_equipes = 30
K = 32
elo_equipes = []
elo_equipes_a = []
elo_equipes_d = []
liste_equipes = ["ANA", "ARI", "ATL", "BAL", "BOS", "CHC", "CHW", "CIN",
                 "CLE", "COL", "DET", "FLA", "HOU", "KCR", "LAD", "MIL",
                 "MIN", "NYM", "NYY", "OAK", "PHI", "PIT", "SDP", "SEA",
                 "SFG", "STL", "TBD", "TEX", "TOR", "WSN"]


# Application

elo_equipes = calculs.calcule_elo_ligue(elo_equipes, [13052, 37685], K)
# resultats = calculs.parie_ligue_seuil_variable_fermeture(
#     elo_equipes, [10584, 13051], 1000, [0.3, 0.5], 0.01, K)
# print(resultats)

# elo_equipes = []
# # elo_equipes = calculs.calcule_elo_ligue(
# #     elo_equipes, [2299, 4702], K)
# print(calculs.compare_resultats_variation(
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
