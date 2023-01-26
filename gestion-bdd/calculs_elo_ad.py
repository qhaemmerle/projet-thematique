import math
import json


# Importation de la BDD json
tableau = open('bdd_matchs2.json', 'r')
bdd = json.load(tableau)
print("Tableau lu")


# Données et outils
nombre_equipes = 30
K = 32  # Régule le nombre de points ELO échangés par match.
elo_equipes = []
elo_equipes_a = []
elo_equipes_d = []
liste_equipes = ["ANA", "ARI", "ATL", "BAL", "BOS", "CHC", "CHW", "CIN",
                 "CLE", "COL", "DET", "FLA", "HOU", "KCR", "LAD", "MIL",
                 "MIN", "NYM", "NYY", "OAK", "PHI", "PIT", "SDP", "SEA",
                 "SFG", "STL", "TBD", "TEX", "TOR", "WSN"]


def donne_num_equipe(tag_equipe):
    """Donne le numéro d'une équipe à partir de son tag."""

    return liste_equipes.index(tag_equipe)


def donne_tag_equipe(num_equipe):
    """Donne le tag d'une équipe à partir de son numéro."""

    return liste_equipes[num_equipe]


def recupere_parametre_bdd(num_match, parametre):
    """Récupère la valeur d'un paramètre dans le fichier de base de données."""

    return bdd[str(num_match)][parametre]


def recupere_match_bdd(num_match):
    """Récupère tous les paramètres d'un match dans le fichier de bdd."""

    equipe1 = recupere_parametre_bdd(num_match, "equipe1")
    equipe2 = recupere_parametre_bdd(num_match, "equipe2")
    score1 = recupere_parametre_bdd(num_match, "score1")
    score2 = recupere_parametre_bdd(num_match, "score2")
    resultat = recupere_parametre_bdd(num_match, "resultat")
    return equipe1, equipe2, score1, score2, resultat


def initialise_elo_equipes(elo_equipes):
    """Initialise les elos à 1500 si elo_equipes est vide."""

    if elo_equipes == []:
        for equipe in range(nombre_equipes):
            elo_equipes += [5000]
    return elo_equipes


def inverse_intervalle(intervalle):
    """Transforme l'intervalle en son parcours à l'envers pour boucler."""

    return range(intervalle[1], intervalle[0] - 1, -1)


# Prédictions
def calcule_match(elo_equipes_a, elo_equipes_d, equipe_a, equipe_d,
                  score_a, score_d, K):
    """Modifie le tableau des elos en fonction du résultat d'un match."""

    initialise_elo_equipes(elo_equipes_a)
    initialise_elo_equipes(elo_equipes_d)
    elo_a = elo_equipes_a[equipe_a]
    elo_d = elo_equipes_d[equipe_d]
    attendu_a = 1 / (1 + 10**((elo_a - elo_d) / 400))
    attendu_d = 1 / (1 + 10**((elo_d - elo_a) / 400))
    resultat = score_a / (score_a + score_d)
    nouvel_elo_a = elo_a + K * (resultat - attendu_a)
    nouvel_elo_d = elo_d + K * ((1 - resultat) - attendu_d)
    elo_equipes_a[equipe_a] = nouvel_elo_a
    elo_equipes_d[equipe_d] = nouvel_elo_d
    return elo_equipes_a, elo_equipes_d


def calcule_elo_ligue(elo_equipes_a, elo_equipes_d, intervalle_matchs, K):
    """Modifie le tableau des elos en fonction d'une série de matchs."""

    initialise_elo_equipes(elo_equipes_a)
    initialise_elo_equipes(elo_equipes_d)
    serie_matchs = inverse_intervalle(intervalle_matchs)
    for num_match in serie_matchs:
        equipe1, equipe2, score1, score2, resultat = recupere_match_bdd(
            num_match)
        elo_equipes_a, elo_equipes_d = calcule_match(
            elo_equipes_a, elo_equipes_d, equipe1, equipe2, score1, score2, K)
        elo_equipes_a, elo_equipes_d = calcule_match(
            elo_equipes_a, elo_equipes_d, equipe2, equipe1, score2, score1, K)
    return elo_equipes_a, elo_equipes_d


def calcule_probabilite_victoire(elo_equipes_a, elo_equipes_d,
                                 equipe1, equipe2):
    """Calcule à partir de leurs elos la probabilité de victoire de equipe1."""

    initialise_elo_equipes(elo_equipes_a)
    initialise_elo_equipes(elo_equipes_d)
    elo1_a = elo_equipes_a[equipe1]
    elo1_d = elo_equipes_d[equipe1]
    elo2_a = elo_equipes_a[equipe2]
    elo2_d = elo_equipes_d[equipe2]
    elo1 = (elo1_a + elo1_d)
    elo2 = (elo2_a + elo2_d)
    ecart = elo1 - elo2
    probabilite_de_victoire1 = 1 - 1 / (1 + math.exp(0.00583 * ecart - 0.0505))
    return probabilite_de_victoire1


# Application
def compare_resultats(elo_equipes_a, elo_equipes_d,
                      intervalle_matchs, seuil, K):
    """Compare les résultats réels aux résultats prédits."""

    initialise_elo_equipes(elo_equipes_a)
    initialise_elo_equipes(elo_equipes_d)
    nombre_matchs = 0
    succes = 0
    seuil_haut = 1 - seuil
    serie_matchs = inverse_intervalle(intervalle_matchs)
    for num_match in serie_matchs:
        equipe1, equipe2, score1, score2, resultat = recupere_match_bdd(
            num_match)
        proba = calcule_probabilite_victoire(
            elo_equipes_a, elo_equipes_d, equipe1, equipe2)
        if proba < seuil_haut and proba > seuil:
            continue
        nombre_matchs += 1
        prediction = 0
        if proba > 0.5:
            prediction = 1
        if prediction == resultat:
            succes += 1
        elo_equipes_a, elo_equipes_d = calcule_match(
            elo_equipes_a, elo_equipes_d, equipe1, equipe2, score1, score2, K)
        elo_equipes_a, elo_equipes_d = calcule_match(
            elo_equipes_a, elo_equipes_d, equipe2, equipe1, score2, score1, K)
    if nombre_matchs == 0:
        nombre_matchs = 1
    taux_reussite = succes / nombre_matchs
    return taux_reussite, elo_equipes_a, elo_equipes_d


def parie_ligue_naif(elo_equipes, intervalle_matchs, cotes_paris, mise, K):
    """Parie une somme identique sur tous les matchs d'un intervalle."""

    initialise_elo_equipes(elo_equipes)
    perte_totale = 0
    gain_total = 0
    serie_matchs = inverse_intervalle(intervalle_matchs)
    for num_match in serie_matchs:
        num_cote = num_match - intervalle_matchs[0]
        equipe1, equipe2, resultat = recupere_match_bdd(num_match)
        proba = calcule_probabilite_victoire(elo_equipes, equipe1, equipe2)
        prediction = 0
        if proba > 0.5:
            prediction = 1
        cote = cotes_paris[num_cote][1 - prediction]
        perte_totale += mise
        if resultat == prediction:
            gain_total += mise * cote
        elo_equipes = calcule_match(elo_equipes, equipe1, equipe2, resultat, K)
        benefices = gain_total - perte_totale
    return benefices


def compare_resultats_variation(elo_equipes_a, elo_equipes_d,
                                interv_matchs_simule, interv_matchs_compare,
                                seuil, intervK, pas):
    """Compare les résultats réel et prédits, par rapport à  un K variable."""

    initialise_elo_equipes(elo_equipes_a)
    initialise_elo_equipes(elo_equipes_d)
    K_taux_max = 0
    taux_max = 0
    Kmin, Kmax = intervK
    for Ki in range(int(Kmin / pas), int(Kmax / pas)):
        K = Ki * pas
        print(K)
        elo_equipes_a, elo_equipes_d = calcule_elo_ligue(
            elo_equipes_a, elo_equipes_d, interv_matchs_simule, K)
        taux = compare_resultats(
            elo_equipes_a, elo_equipes_d, interv_matchs_compare, seuil, K)
        if taux[0] > taux_max:
            taux_max = taux[0]
            K_taux_max = K
    return K_taux_max, taux_max


# print(calcule_elo_ligue(elo_equipes_a, elo_equipes_d, [2299, 4702], 16))


print(compare_resultats_variation(elo_equipes_a, elo_equipes_d, [2299, 4702],
                                  [1000, 2298], 0.3, [0, 9], 0.1))
