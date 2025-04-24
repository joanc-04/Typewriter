# -*- coding: utf-8 -*-
import time


def get_words(filename="recherche_p1.txt"):
    text = ""
    try:
        with open(filename) as file:

            for line in file:
                text += line
    except Exception as e:
        print(e)
    return text


def get_error(T, L):
    return sum([(L - sum([len(word) + 1 for word in line]) + 1) ** 2 for line in T])


def write_log(message="", filename="log.txt"):
    with open(filename, "a") as file:
        file.write(message + "\n")


def evaluation(liste, L):
    S = 0
    for i in range(len(liste)):
        S += (L - len(liste[i])) ** 2
        if L < len(liste[i]):
            print(f"Erreur, ligne {i} est trop longue {len(liste[i])} > {L}")
            S = float('inf')
            break
    return S


def conversion(liste, L):
    text = ""
    for ligne in liste:
        x = L - len(ligne)
        text = text + ligne + " " * x + "\n"
    return text


def mise_en_page_glouton(text, L):
    """
    Mise en page via un algorithme glouton.

    Parameters
    ----------
    text : str
        texte à mettre en page.
    L : int
        Longueur d'une ligne.

    Returns
    -------
    (str, int)
        Tuple contenant le texte mis en page, et le score associé.

    """
    mots = text.split()
    start = time.time()
    liste = [mots[0]]
    for i in range(1, len(mots)):
        if len(liste[-1]) + len(mots[i]) + 1 <= L:
            liste[-1] = liste[-1] + " " + mots[i]
        else:
            liste.append(mots[i])
    S = evaluation(liste, L)

    end = time.time()
    write_log(
        f"Le texte de {len(text)} caractères a été mis en page en : {end - start} s. Avec un score de {S}. (glouton)")

    if S != float('inf'):
        return (conversion(liste, L), S)


def mise_en_page_recursif(text, L):
    """
    Mise en page via un algorithme de recherche éxhaustive récursif.

    Parameters
    ----------
    text : str
        texte à mettre en page.
    L : int
        Longueur d'une ligne.

    Returns
    -------
    (str, int)
        Tuple contenant le texte mis en page, et le score associé.

    """
    mots = text.split()
    # On stocke la taille des mots pour éviter d'appeler len n*2**n fois de plus
    # car bien que O(1) cela représente un temps supplémentaire,
    # Et car cela permet de calculer via sum(ligne)+len(ligne)-1 le nombre de 
    # caractères de la ligne "ligne"
    taille_mots = [len(mots[i]) for i in range(len(mots))]

    start = time.time()

    t0 = taille_mots.pop()
    S, taille = rec(taille_mots, L, [[t0]])
    # On reforme la mise en page à l'aide de taille
    txt = ""
    i = 0
    while taille != []:  # On reforme le texte
        t = taille.pop()
        s = L - (sum(t) + len(t) - 1)
        t.pop()
        txt += mots[i]
        i += 1
        while t != []:  # On reforme la ligne
            t.pop()
            txt = txt + " " + mots[i]
            i += 1
        txt = txt + s * " " + "\n"

    end = time.time()
    write_log(
        f"Le texte de {len(text)} caractères a été mis en page en : {end - start} s. Avec un score de {S}. (récursif)")

    return txt, S


def rec(t, L, current=[[]]):
    """
    Fonction auxiliaire de mise_en_page_recursif qui effectue le traitement
    récursif.

    Parameters
    ----------
    t : list
        Liste contenant la taille de tous les mots du text dans l'ordre original
    L : int
        Taille maximale des lignes
    current : list, optional
        Branche de l'arbre en cours de création. The default is [[]].

    Returns
    -------
    list = [int,list]
        Liste contenant le score et la liste inversée des tailles des mots
        mis en page
    """
    if len(t) != 0:
        # On prend le dernier mot du texte pour éviter de faire pop(0)
        # qui demanderai de modifier l'entièreté de la liste p
        m = t.pop()

        # Création d'une nouvelle ligne
        rec1 = rec(t, L, current + [[m]])

        # Ajout sur la même ligne (si possible)
        rec2 = (float('inf'), [])  # Si impossible, n'est pas une mise en page
        if sum(current[-1]) + m + len(current[-1]) <= L:
            current[-1] = current[-1] + [m]
            rec2 = rec(t, L, current)
        # On rajoute le dernier mot pour les autres branches
        t.append(m)
        # On remonte la meilleur mise en page
        return [rec1, rec2][int(rec1[0] > rec2[0])]

    else:  # len(t) == 0 donc il n'y a plus de mots à ajouter
        # On calcule le score de cette mise en page
        S = 0
        for row in current:
            l = len(row) - 1 + sum(row)
            S += (L - l) ** 2
        return S, current


def mise_en_page_memoisation(text, L):
    """
    Mise en page via un algorithme de recherche éxhaustive récursif utilisant 
    de la mémoïsation.

    Parameters
    ----------
    text : str
        texte à mettre en page.
    L : int
        Longueur d'une ligne.

    Returns
    -------
    (str, int)
        Tuple contenant le texte mis en page, et le score associé.

    """
    global chiffres
    global d
    mots = text.split(" ")
    chiffres = [len(mots[i]) for i in range(len(mots))]

    # On utilise un dictionnaire pour la mémoisation. La valeur associée à la 
    # clée (i, j) correspond à la somme des espaces au carré si on commence par
    # le i-ème mot à l'indice j dans la ligne. 
    d = {}

    def aux(i, j, L):
        """
        Fonction auxiliaire de mise_en_page_memoisation,
        Utilise d comme stockage pour la mémoïsation.

        Parameters
        ----------
        i : int
            Indice du mot dans le texte.
        j : int
            Position du mot dans la ligne.

        Returns
        -------
        int
            Renvoie le score associé à la mise en page optimale

        """

        global chiffres
        global d

        if (i, j) in d:
            return d[(i, j)]

        mot = chiffres[i]

        assert mot <= L, "Un mot est de longueur " + str(
            mot) + ", ce qui est plus grand que la longueur L de la ligne (" + str(L) + ")"

        # Si le mot considéré n'est pas au début de la ligne (ie j = 0), il 
        # faut prendre en compte le fait qu'on rajoutera un espace avant
        espace = 1
        if j == 0:
            espace = 0

        # Cas de base : si le mot considéré est le dernier mot d texte
        if i == len(chiffres) - 1:
            d[(i, j)] = (L - j - mot - espace) ** 2
            return d[(i, j)]

        prochain_mot = chiffres[i + 1]

        # Dans tous les cas, on peut mettre le prochain mot à la ligne d'après (j=0)
        d[(i + 1, 0)] = aux(i + 1, 0, L)

        if j + mot + 1 + prochain_mot + 1 > L:
            # Si on ne peut pas caser le prochain mot dans la ligne actuelle,
            # la somme des carrés correspondant au mot actuel est nécessairement
            # égale à la somme des carré du mot d'après (dans une nouvelle ligne)
            # plus le carré des espaces de la ligne actuelle
            d[(i, j)] = d[(i + 1, 0)] + (L - j - mot - espace) ** 2
        else:
            # Si on peut caser le prochain mot dans la ligne actuelle, il faut
            # prendre l'option qui engendre le moins de somme des carrés entre
            # avoir le prochain mot dans une nouvelle ligne ou dans la ligne actuelle
            d[(i + 1, j + mot + espace)] = aux(i + 1, j + mot + espace, L)
            d[(i, j)] = min(d[(i + 1, 0)] + (L - j - mot - espace) ** 2, d[(i + 1, j + mot + espace)])

        return d[(i, j)]

    start = time.time()

    S = aux(0, 0, L)

    # On construit liste des mots (pour la mise en forme) en s'aidant du 
    # dictionnaire construit au cours de la mémoisation
    liste = [mots[0]]
    i, j = 1, chiffres[0]
    while i < len(chiffres):
        if (i, j) not in d:
            # Si le mot considéré ne peut pas être à l'indice de ligne j, il 
            # est forcément dans une nouvelle ligne
            liste.append(mots[i])
            j = chiffres[i]
        elif d[(i, j)] > d[(i, 0)] + (L - j) ** 2:
            # On ajoute le mot considéré dans une nouvelle ligne si ca coute moins cher...
            liste.append(mots[i])
            j = chiffres[i]
        else:
            # ...sinon on le met à la fin de la ligne
            liste[-1] += " " + mots[i]
            j += chiffres[i] + 1
        i += 1

    end = time.time()
    write_log(
        f"Le texte de {len(text)} caractères a été mis en page en : {end - start} s. Avec un score de {S}. (récursif+mémoïsation)")

    return (conversion(liste, L), S)


def mise_en_page_dynamique(text, L, quiet=False):
    """
    Mise en page via un algorithme de programation dynamique.

    Parameters
    ----------
    text : str
        texte à mettre en page.
    L : int
        Longueur d'une ligne.

    Returns
    -------
    (str, int)
        Tuple contenant le texte mis en page, et le score associé.

    """

    mots = text.split()
    n = len(mots)

    memo = [float("inf")] * n + [0]
    cuts = [None] * n

    start = time.time()

    for i in range(n - 1, -1, -1): # Pour chaque mot de départ i
        curr_line_length = 0 # Longueur de la ligne en cours
        for j in range(i, n): # Pour chaque mot de coupure possible j
            word_len = len(mots[j])
            curr_line_length += word_len

            if curr_line_length > L: # Si le mot ne rentre pas dans la ligne
                break

            if j != i: curr_line_length += 1 # On ajoute un espace entre chaque mot

            cost = (L - curr_line_length) ** 2 + memo[j + 1] # On calcul le cout de la ligne
            if cost < memo[i]: # On calcul avec la relation de récurrence si le nouvel indice de coupure est plus optimal
                memo[i] = cost # On enregistre le cout optimal obtenu
                cuts[i] = j + 1 # On enregistre l'indice de coupure j optimal

    T = []
    i = 0
    while i < n: # On reconstruit le chemin optimal en partant du début
        j = cuts[i]
        T.append(mots[i:j]) # La nouvelle ligne contient les mots commençant par le mot i et se terminant par le mot avant le mot j-1.
        i = j

    S = get_error(T, L)

    end = time.time()
    if not quiet: write_log(
        f"Le texte de {len(text)} caractères a été mis en page en : {end - start} s. Avec un score de {S}. (dynamique)")

    return T, S, end - start


"""""""""""""""""""""""""""""""""""""""""""""""""""
                       TESTS
"""""""""""""""""""""""""""""""""""""""""""""""""""

"""
Vous pouvez visualiser les tests suivant dans le fichier log.txt
"""


if __name__ == "__main__":
    open("log.txt", "w").close() # Efface le fichier log.txt

    text = get_words('recherche_p1.txt')[:-1]  # On retire le \n en trop à la fin
    text_c = get_words('recherche_complet.txt')

    L = 80
    print(f"Test glouton (L={L})")
    mise_en_page_glouton(text, L)
    # mise_en_page_glouton(text_c, 80) # Long (environ 100s)
    write_log()

    L = 20
    print(f"Test récursif (L={L})")
    mise_en_page_recursif(text[:129], L)  # Car très lent
    write_log()

    L = 80
    print(f"Test récursif avec mémoïsation (L={L})")
    mise_en_page_memoisation(text, L)
    # mise_en_page_memoisation(text_c, L) # Récursion depth error
    write_log()

    L = 80
    print(f"Test dynamique (L={L})")
    mise_en_page_dynamique(text, L)
    mise_en_page_dynamique(text_c, L)
    write_log()

    # Etude de l'influence de L
    write_log()
    write_log("Influence du paramètre L :")

    smallL = []
    bigL = []
    N = 100
    for _ in range(N):
        smallL.append(mise_en_page_dynamique(text, 50, True)[2])
        bigL.append(mise_en_page_dynamique(text, 1e9, True)[2])

    write_log(f"Sur {N} itérations, la durée moyenne sur 'recherche_p1.txt' avec L={50} est de {sum(smallL) / N}.")
    write_log(f"Sur {N} itérations, la durée moyenne sur 'recherche_p1.txt' avec L={int(1e9)} est de {sum(bigL) / N}.")

    # Pas besoin d'exécuter les deux lignes ci-dessous.
    # Utile pour l'exemple explicatif du déroulement (on a utilisé le débugger pour nous aider à bien voir les étapes).

    # text_test = "Bonjour, je m'appelle Joan."
    # mise_en_page_dynamique(text_test, 15, True)