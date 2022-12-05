import math
import json
from matplotlib import pyplot as plt


# 1) Importation des BDD
# a) BDD des matchs
tableau_bdd = open('bdd_matchs.json', 'r')
bdd = json.load(tableau_bdd)

# b) Table de conversion des numéros de matchs en clés de la bdd
tableau_conversion = open('conversion_matchs_cles.json', 'r')
cles_matchs = json.load(tableau_conversion)


# 2) Données et outils
nombre_equipes = 30
K = 32  # Régule le nombre de points ELO échangés par match.
elo_equipes = []
tags_equipes = ["ANA", "ARI", "ATL", "BAL", "BOS", "CHC",
                "CHW", "CIN", "CLE", "COL", "DET", "FLA",
                "HOU", "KCR", "LAD", "MIL", "MIN", "NYM",
                "NYY", "OAK", "PHI", "PIT", "SDP", "SEA",
                "SFG", "STL", "TBD", "TEX", "TOR", "WSN"]


def donne_num_equipe(tag_equipe):
    """Donne le numéro d'une équipe à partir de son tag."""

    return tags_equipes.index(tag_equipe)


def donne_tag_equipe(num_equipe):
    """Donne le tag d'une équipe à partir de son numéro."""

    return tags_equipes[num_equipe]


def recupere_parametre_bdd(num_match, parametre):
    """Récupère la valeur d'un paramètre dans le fichier de base de données."""

    cle = cles_matchs[str(num_match)]["cle"]
    return bdd[cle][parametre]


def recupere_match_bdd(num_match):
    """Récupère les équipes et résultat d'un match dans le fichier de bdd."""

    equipe1 = recupere_parametre_bdd(num_match, "equipe1")
    equipe2 = recupere_parametre_bdd(num_match, "equipe2")
    resultat = recupere_parametre_bdd(num_match, "resultat")
    return equipe1, equipe2, resultat


def recupere_cotes_ouverture_bdd(num_match):
    """Récupère les cotes à l'ouverture d'un match dans le fichier de bdd."""

    cote_americaine1 = recupere_parametre_bdd(num_match, "coteOpen1")
    cote_americaine2 = recupere_parametre_bdd(num_match, "coteOpen2")
    cotes_americaines = [cote_americaine1, cote_americaine2]
    cotes = []
    for cote_str in cotes_americaines:
        cote = int(cote_str)
        if cote > 0:
            cotes.append(cote / 100 + 1)
        else:
            cotes.append(1 - 100 / cote)
    return cotes


def recupere_cotes_fermeture_bdd(num_match):
    """Récupère les cotes à la fermeture d'un match dans le fichier de bdd."""

    cote_americaine1 = recupere_parametre_bdd(num_match, "coteClose1")
    cote_americaine2 = recupere_parametre_bdd(num_match, "coteClose2")
    cotes_americaines = [cote_americaine1, cote_americaine2]
    cotes = []
    for cote_str in cotes_americaines:
        cote = int(cote_str)
        if cote > 0:
            cotes.append(cote / 100 + 1)
        else:
            cotes.append(1 - 100 / cote)
    return cotes


def initialise_elo_equipes(elo_equipes):
    """Initialise les elos à 1500 si elo_equipes est vide."""

    if elo_equipes == []:
        for equipe in range(nombre_equipes):
            elo_equipes += [1500]
    return elo_equipes


def inverse_intervalle(intervalle):
    """Transforme l'intervalle en son parcours à l'envers pour boucler."""

    return range(intervalle[1], intervalle[0] - 1, -1)


# 3) Prédictions
def calcule_match(elo_equipes, equipe1, equipe2, resultat, K):
    """Modifie le tableau des elos en fonction du résultat d'un match."""

    initialise_elo_equipes(elo_equipes)
    elo1 = elo_equipes[equipe1]
    elo2 = elo_equipes[equipe2]
    attendu1 = 1 / (1 + 10**((elo2 - elo1) / 400))
    attendu2 = 1 / (1 + 10**((elo1 - elo2) / 400))
    nouvel_elo1 = elo1 + K * (resultat - attendu1)
    nouvel_elo2 = elo2 + K * ((1 - resultat) - attendu2)
    elo_equipes[equipe1] = nouvel_elo1
    elo_equipes[equipe2] = nouvel_elo2
    return elo_equipes


def calcule_elo_ligue(elo_equipes, intervalle_matchs, K):
    """Modifie le tableau des elos en fonction d'une série de matchs."""

    initialise_elo_equipes(elo_equipes)
    serie_matchs = inverse_intervalle(intervalle_matchs)
    y = []
    x = []
    xi = 0
    for num_match in serie_matchs:
        equipe1, equipe2, resultat = recupere_match_bdd(num_match)
        elo_equipes = calcule_match(elo_equipes, equipe1, equipe2, resultat, K)
        if equipe1 == 28 or equipe2 == 28:
            print(elo_equipes[28])
            y.append(elo_equipes[28])
            xi += 1
            x.append(xi)
    plt.plot(x, y)
    length = len(x)
    length_i = length / 10
    for i in range(10):
        plt.plot(x == i * length_i)
    plt.show()

    return elo_equipes


def calcule_probabilite_victoire(elo_equipes, equipe1, equipe2):
    """Calcule à partir de leurs elos la probabilité de victoire de equipe1."""

    initialise_elo_equipes(elo_equipes)
    elo1 = elo_equipes[equipe1]
    elo2 = elo_equipes[equipe2]
    ecart = elo1 - elo2
    probabilite_de_victoire1 = 1 - 1 / (1 + math.exp(0.00583 * ecart - 0.0505))
    return probabilite_de_victoire1


# 4) Application
# a) Comparaison de nos prédictions aux résultats réels.
def compare_resultats(elo_equipes, intervalle_matchs, seuil_bas, K):
    """Compare les résultats réels aux résultats prédits."""

    initialise_elo_equipes(elo_equipes)
    nombre_matchs = 0
    succes = 0
    seuil_haut = 1 - seuil_bas
    serie_matchs = inverse_intervalle(intervalle_matchs)
    for num_match in serie_matchs:
        equipe1, equipe2, resultat = recupere_match_bdd(num_match)
        proba = calcule_probabilite_victoire(elo_equipes, equipe1, equipe2)
        if proba < seuil_haut and proba > seuil_bas:
            continue
        nombre_matchs += 1
        prediction = 0
        if proba > 0.5:
            prediction = 1
        if prediction == resultat:
            succes += 1
        elo_equipes = calcule_match(elo_equipes, equipe1, equipe2, resultat, K)
    if nombre_matchs == 0:
        nombre_matchs = 1
    taux_reussite = succes / nombre_matchs
    return taux_reussite, elo_equipes


def compare_resultats_variation(elo_equipes, interv_matchs_simule,
                                interv_matchs_compare, seuil_bas, intervK, pas
                                ):
    """compare_resultats, pour K variant dans un intervalle."""

    initialise_elo_equipes(elo_equipes)
    K_taux_max = 0
    taux_max = 0
    Kmin, Kmax = intervK
    for Ki in range(int(Kmin / pas), int(Kmax / pas)):
        K = Ki * pas
        print(K)
        elo_equipes = calcule_elo_ligue(elo_equipes, interv_matchs_simule, K)
        taux = compare_resultats(
            elo_equipes, interv_matchs_compare, seuil_bas, K)
        if taux[0] > taux_max:
            taux_max = taux[0]
            K_taux_max = K
    return K_taux_max, taux_max


# b) Paris naïfs
def parie_ligue_naif(elo_equipes, intervalle_matchs, mise, seuil_bas, K):
    """Parie une somme identique sur tous les matchs d'un intervalle."""

    initialise_elo_equipes(elo_equipes)
    perte_totale = 0
    gain_total = 0
    seuil_haut = 1 - seuil_bas
    serie_matchs = inverse_intervalle(intervalle_matchs)
    for num_match in serie_matchs:
        cotes = recupere_cotes_ouverture_bdd(num_match)
        equipe1, equipe2, resultat = recupere_match_bdd(num_match)
        proba = calcule_probabilite_victoire(elo_equipes, equipe1, equipe2)
        if proba < seuil_haut and proba > seuil_bas:
            continue
        prediction = 0
        if proba > 0.5:
            prediction = 1
        cote = cotes[prediction - 1]
        perte_totale += mise
        if resultat == prediction:
            gain_total += mise * cote
        elo_equipes = calcule_match(elo_equipes, equipe1, equipe2, resultat, K)
        benefices = gain_total - perte_totale
    return benefices, perte_totale


def parie_ligue_naif_seuil_variable(elo_equipes, intervalle_matchs, mise,
                                    intervalle_seuil, pas, K):
    """parie_ligue_naif, pour seuil_bas variant dans un intervalle."""

    initialise_elo_equipes(elo_equipes)
    benef_max_u = 0
    seuilb_min, seuilb_max = intervalle_seuil
    for seuil_bas_i in range(int(seuilb_min / pas), int(seuilb_max / pas)):
        seuil_bas = seuil_bas_i * pas
        print(seuil_bas)
        print(elo_equipes)
        benefs, perte_totale = parie_ligue_naif(
            elo_equipes, intervalle_matchs, mise, seuil_bas, K)
        benefs_u = benefs / perte_totale
        if benefs_u > benef_max_u:
            benef_max_u = benefs_u
            seuil_benef_max = seuil_bas
            nbmatchs_benef_max = perte_totale / 10
    return seuil_benef_max, benef_max_u, nbmatchs_benef_max


# c) Paris avec gestion de bankroll
def parie_ligue(elo_equipes, intervalle_matchs, bankroll, seuil_bas, K):
    """Parie 3% de la bankroll sur tous les matchs d'un intervalle."""

    initialise_elo_equipes(elo_equipes)
    seuil_haut = 1 - seuil_bas
    serie_matchs = inverse_intervalle(intervalle_matchs)
    for num_match in serie_matchs:
        cotes = recupere_cotes_ouverture_bdd(num_match)
        equipe1, equipe2, resultat = recupere_match_bdd(num_match)
        proba = calcule_probabilite_victoire(elo_equipes, equipe1, equipe2)
        if proba < seuil_haut and proba > seuil_bas:
            continue
        prediction = 0
        if proba > 0.5:
            prediction = 1
        cote = cotes[prediction - 1]
        mise = 0.03 * bankroll
        bankroll = bankroll - mise
        if resultat == prediction:
            bankroll += mise * cote
        elo_equipes = calcule_match(elo_equipes, equipe1, equipe2, resultat, K)
    return bankroll


def parie_ligue_seuil_variable(elo_equipes, intervalle_matchs, bankroll,
                               intervalle_seuil, pas, K):
    """parie_ligue, pour seuil_bas variant dans un intervalle."""

    initialise_elo_equipes(elo_equipes)
    bankroll_max = 0
    seuilb_min, seuilb_max = intervalle_seuil
    for seuil_bas_i in range(int(seuilb_min / pas), int(seuilb_max / pas)):
        seuil_bas = seuil_bas_i * pas
        print(seuil_bas)
        print(elo_equipes[0])
        elos_temp = []
        for elo in elo_equipes:
            elos_temp.append(elo)
        print(elos_temp[0])
        bankroll_finale = parie_ligue(
            elos_temp, intervalle_matchs, bankroll, seuil_bas, K)
        if bankroll_finale > bankroll_max:
            bankroll_max = bankroll_finale
            seuil_benef_max = seuil_bas
    return seuil_benef_max, bankroll_max


def parie_ligue_fermeture(
        elo_equipes, intervalle_matchs, bankroll, seuil_bas, K):
    """Parie 3% de la bankroll sur tous les matchs d'un intervalle."""

    initialise_elo_equipes(elo_equipes)
    seuil_haut = 1 - seuil_bas
    serie_matchs = inverse_intervalle(intervalle_matchs)
    for num_match in serie_matchs:
        cotes = recupere_cotes_fermeture_bdd(num_match)
        equipe1, equipe2, resultat = recupere_match_bdd(num_match)
        proba = calcule_probabilite_victoire(elo_equipes, equipe1, equipe2)
        if proba < seuil_haut and proba > seuil_bas:
            continue
        prediction = 0
        if proba > 0.5:
            prediction = 1
        cote = cotes[prediction - 1]
        mise = 0.03 * bankroll
        bankroll = bankroll - mise
        if resultat == prediction:
            bankroll += mise * cote
        elo_equipes = calcule_match(elo_equipes, equipe1, equipe2, resultat, K)
    return bankroll


def parie_ligue_seuil_variable_fermeture(elo_equipes, intervalle_matchs,
                                         bankroll, intervalle_seuil, pas, K):
    """parie_ligue, pour seuil_bas variant dans un intervalle."""

    initialise_elo_equipes(elo_equipes)
    bankroll_max = 0
    seuilb_min, seuilb_max = intervalle_seuil
    for seuil_bas_i in range(int(seuilb_min / pas), int(seuilb_max / pas)):
        seuil_bas = seuil_bas_i * pas
        print(seuil_bas)
        print(elo_equipes[0])
        elos_temp = []
        for elo in elo_equipes:
            elos_temp.append(elo)
        print(elos_temp[0])
        bankroll_finale = parie_ligue_fermeture(
            elos_temp, intervalle_matchs, bankroll, seuil_bas, K)
        if bankroll_finale > bankroll_max:
            bankroll_max = bankroll_finale
            seuil_benef_max = seuil_bas
    return seuil_benef_max, bankroll_max
