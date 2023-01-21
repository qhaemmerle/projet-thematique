#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jan 21 11:16:01 2023

@author: jules
"""

import math
import json

from math import floor
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt


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
    for num_match in serie_matchs:
        equipe1, equipe2, resultat = recupere_match_bdd(num_match)
        elo_equipes = calcule_match(elo_equipes, equipe1, equipe2, resultat, K)
    return elo_equipes


def calcule_probabilite_victoire(elo_equipes, equipe1, equipe2):
    """Calcule à partir de leurs elos la probabilité de victoire de equipe1."""

    initialise_elo_equipes(elo_equipes)
    elo1 = elo_equipes[equipe1]
    elo2 = elo_equipes[equipe2]
    ecart = elo2 - elo1
    probabilite_de_victoire1 = 1 / (1 + 10**(ecart / 400))
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
        elo_equipes = calcule_elo_ligue(elo_equipes, interv_matchs_simule, K)
        taux = compare_resultats(
            elo_equipes, interv_matchs_compare, seuil_bas, K)
        print(taux[0])
        if taux[0] > taux_max:
            taux_max = taux[0]
            K_taux_max = K
        elo_equipes = []
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


# c) Paris avec gestion de bankroll naïve
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


# d) Calculs de vraisemblance et plot du meilleur K
def calcule_vraisemblance(elo_equipes, intervalle_matchs, K):
    """Calcule la vraisemblance sur un intervalle de matchs donné."""

    initialise_elo_equipes(elo_equipes)
    serie_matchs = inverse_intervalle(intervalle_matchs)
    log_vraisemblance = 0
    for num_match in serie_matchs:
        equipe1, equipe2, resultat = recupere_match_bdd(num_match)
        equipes = equipe2, equipe1
        equipeG, equipeP = equipes[resultat], equipes[1 - resultat]
        proba = calcule_probabilite_victoire(elo_equipes, equipeG, equipeP)
        log_proba = math.log(proba, 10)
        log_vraisemblance += log_proba
        elo_equipes = calcule_match(elo_equipes, equipe1, equipe2, resultat, K)
    return log_vraisemblance


def calcule_vraisemblance_variation(elo_equipes, interv_matchs_simule,
                                    interv_matchs_compare, intervK, pas):
    """calcule_vraisemblance, pour K variant dans un intervalle."""

    K_vraisemblance_max = 0
    log_vraisemblance_max = -100000000000000
    Kmin, Kmax = intervK
    for Ki in range(int(Kmin / pas), int(Kmax / pas)):
        K = Ki * pas
        elo_equipes = calcule_elo_ligue(elo_equipes, interv_matchs_simule, K)
        # print(elo_equipes)
        log_vraisemblance = calcule_vraisemblance(
            elo_equipes, interv_matchs_compare, K)
        print(log_vraisemblance)
        if log_vraisemblance > log_vraisemblance_max:
            log_vraisemblance_max = log_vraisemblance
            K_vraisemblance_max = K
        elo_equipes = []
    return K_vraisemblance_max, log_vraisemblance_max


def calcule_v1500_variation(interv_matchs_compare, intervK, pas):
    """calcule_vraisemblance, pour K variant dans un intervalle."""

    K_vraisemblance_max = 0
    log_vraisemblance_max = -100000000000000
    Kmin, Kmax = intervK
    x = interv_matchs_compare[0]
    for Ki in range(int(Kmin / pas), int(Kmax / pas)):
        K = Ki * pas
        elo_equipes = calcule_elo_ligue([], [x + 1, x + 1000], K)
        log_vraisemblance = calcule_vraisemblance(
            elo_equipes, interv_matchs_compare, K)
        if log_vraisemblance > log_vraisemblance_max:
            log_vraisemblance_max = log_vraisemblance
            K_vraisemblance_max = K
    return K_vraisemblance_max


def plot_K_dates_variables(date_min, date_max, nbmin, pmatch, intervK, pasK):
    X = []
    Y = []
    Z = []
    for x in range(date_min, date_max + 1 - nbmin, pmatch):
        for y in range(x + nbmin, date_max + 1, pmatch):
            print(x, y)
            K = calcule_v1500_variation([x, y], intervK, pasK)
            X.append(x)
            Y.append(y)
            Z.append(K)
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.scatter(X, Y, Z, c='r')
    ax.set_xlabel('Num Match Début')
    ax.set_ylabel('Num Match Fin')
    ax.set_zlabel('Meilleur K')
    plt.show()


def plot_K_duree_variable(date_min, date_max, pmatch, intervK, pasK):
    X = []
    Y = []
    for x_fin in range(date_min + 1, date_max, pmatch):
        print(x_fin)
        K = calcule_v1500_variation([date_min, x_fin], intervK, pasK)
        X.append(x_fin - date_min)
        Y.append(K)
    plt.plot(X, Y)
    plt.show()


# p --> probabilité de gagné (ELO)
# b est le multiplicateur de gain net
# (exemple mise 100€ je gagne net 60€ --> b = 0.6)
# Pourcentage de la BR que 'lon souhaite risqué'


def critere_kelly(b, p, f):
    q = 1 - p
    return ((b * p - q) / b) * f


elo_equipes = calcule_elo_ligue([], [27845, 54919], K)
# calcul des elo à l'issu de 2000 à fin 2010
f = 0.1
BR = 10000


def mise(num_match, BR, f, elo_equipes):
    equipe1, equipe2, resultat = recupere_match_bdd(num_match)
    c1, c2 = recupere_cotes_fermeture_bdd(num_match)  # (eq1,eq2)
    b1, b2 = c1 / c2, c2 / c1
    p1 = calcule_probabilite_victoire(elo_equipes, equipe1, equipe2)
    p2 = calcule_probabilite_victoire(elo_equipes, equipe2, equipe1)
    critere_kelly1 = critere_kelly(b1, p1, f)
    if critere_kelly1 > 0:
        return (1, critere_kelly1 * BR)  # mise sur lequipe 1
    else:
        critere_kelly2 = critere_kelly(b2, p2, f)
        return (2, critere_kelly2 * BR)


n = 13  # nombre de matchs pour parier


def benefice(num_match, BR, f, elo_equipes):
    m = mise(num_match, BR, f, elo_equipes)
    c1, c2 = recupere_cotes_fermeture_bdd(num_match)  # (eq1,eq2)
    if m[0] == 1:
        return [1, m[1] * (c1 - 1)]
    else:
        return [2, m[1] * (c2 - 1)]


def esperance_de_benefice(num_match, BR, f, elo_equipes):
    equipe1, equipe2, resultat = recupere_match_bdd(num_match)
    proba_victoirede1 = calcule_probabilite_victoire(
        elo_equipes, equipe1, equipe2)
    proba_victoirede2 = calcule_probabilite_victoire(
        elo_equipes, equipe2, equipe1)
    ben = benefice(num_match, BR, f, elo_equipes)
    if ben[0] == 1:
        return [1, proba_victoirede1 * ben[1]]
    else:
        return [2, proba_victoirede2 * ben[1]]


def liste_esperance(num_match, BR, f, elo_equipes, n):
    liste_esperance = []
    for i in range(0, n):
        esp_benef = esperance_de_benefice(num_match - i, BR, f, elo_equipes)
        liste_esperance.append([esp_benef[1], num_match - i, esp_benef[0]])
        # (espérance de gain, num match, eq sur laquelle on mise)
    liste_esperance.sort()
    # print(liste_esperance)
    reversed(liste_esperance)
    return liste_esperance


def choix_matchs(num_match, BR, f, elo_equipes, n):
    critere = 0
    matchs = []
    listesperance = liste_esperance(num_match, BR, f, elo_equipes, n)
    for i in range(len(listesperance)):
        prop = mise(listesperance[i][1], BR, f, elo_equipes)[1] / BR
        if (critere + prop) <= 0.1:
            critere += prop
            matchs.append([listesperance[i][1], prop, listesperance[i][2]])
            # (num match, PROP DE MISE, eq sur laquelle on mise)
    return matchs, critere
    # renvoie num match [[num_match, proportion de BR à miser ]], critere


num_match = 26700
matchs, critere = choix_matchs(num_match, BR, f, elo_equipes, n)


# bankroll est dependante de la fonction choix match

def bankroll(matchs, BR, f, elo_equipes, critere):
    BR2 = BR * (1 - critere)  # BR moins nos mises
    for i in range(len(matchs)):
        num_match = matchs[i][0]
        ind = recupere_parametre_bdd(num_match, "resultat")
        # donne 1 si lequipe 1 gagne, 0 sinon
        c1, c2 = recupere_cotes_fermeture_bdd(num_match)  # (eq1,eq2)
        if ind == 1:
            if matchs[i][2] == 1:
                BR2 += benefice(num_match, BR, f, elo_equipes)[1]
        else:
            if matchs[i][2] == 2:
                BR2 += benefice(num_match, BR, f, elo_equipes)[1]
    return BR2


# interv match permet de base à savoir sur quelle duree calculé la BR

def mise_ligue(elo_equipes, interv_matchs, BR, f, n):
    # n=13#intermatches doit etre un multiple de 13
    quotient = floor((interv_matchs[1] - interv_matchs[0]) / n)
    liste_br = []
    # print(quotient)
    for i in range(quotient):
        num_match = interv_matchs[1] - i * n
        if num_match >= interv_matchs[0]:
            # print(num_match)
            # listeesp=liste_esperance(num_match, BR, f, elo_equipes, n)
            # prend le premier num match et fait une liste de taille n des
            # n num match suivant : (espereance de gain, num match, eq sur
            # laquelle on mise)
            matchs, critere = choix_matchs(num_match, BR, f, elo_equipes, n)
            BR = bankroll(matchs, BR, f, elo_equipes, critere)
            liste_br.append(BR)
            # ideal on recupere la date egalement :
            # recupere_parametre_bdd(num_match, "date") #date a confirmer
    return liste_br  # , date


# quotient = floor((interv_matchs[1]-interv_matchs[0])/n)
# liste_br=mise_ligue (elo_equipes, interv_matchs, BR, f,n)
# date = date.linespace( i for i in range(quotient)

# plt.plot(date, liste_br)
# plt.show()