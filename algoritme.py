import numpy as np

def inicialitzacio(paraula, gramatica):
    """
    La funció inicialitza la taula P[n, n+1, r] per a l'algorisme CYK a partir
    de una paraula (en format string) i una gramatica en aquest format:
        {'simbols': ['S', 'A', 'B', ...], 
        'inici': ['S'],                                    
        'tranformacions': [('S', 'A', 'B'), ('A', 'a') ...]}
    Retorna:
    - P: llista de booleans de forma [n, n+1, r]
        on index 0 (i) representa la posició d'inici de la subcadena
        index 1 (l) representa la longitud de la subcadena (1-indexed)
        index 2 (j) representa el símbol Rj de la gramàtica

        P[i, l, j] = True  -->  el símbol Rj pot generar 
                                la subcadena de longitud l 
                                que comença a la posició i

    - simbols: llista de símbols (per mapear índex <-> nom)
    - simbols_index: diccionari símbol -> índex
    - index_simbols_inici: llista d'índexs dels símbols d'inici
    """
    n = len(paraula)
    simbols = gramatica['simbols']
    r = len(simbols)
    
    # Mapa de símbol -> índex
    simbols_index = {s: i for i, s in enumerate(simbols)}
    
    # Índexs dels símbols d'inici
    index_simbols_inici = [simbols_index[s] for s in gramatica['inici']]

    # Inicialitzem P[n, n+1, r] (n+1 per poder indexar longituds 1..n)
    P = np.zeros((n, n + 1, r), dtype=bool)

    # Omplim les tranformacions unitàries: Rj -> ai
    for i in range(n):
        ai = paraula[i]
        for prod in gramatica['tranformacions']:
            if len(prod) == 2:  # producció unitària: (Rj, terminal)
                Rj, terminal = prod
                if terminal == ai:
                    j = simbols_index[Rj]
                    P[i, 1, j] = True  # longitud 1 (1-indexed)

    return P, simbols_index, index_simbols_inici


def cyk_algoritme(paraula, gramatica):

    """
    La funció s'ajuda d'inicialitzacio() per obtenir:
    - La taula tridimensional P (ja omplerta per subcadenes de longitud 1)
    - Els símbols de la gramàtica (indexats -> volem els números per poder treballar amb els indexos)
    - Els índexs dels símbols d'inici

    L'algoritme omple la taula P per subcadenes de longitud creixent
    mitjançant tres índexs:
    - l (longitud): va de 2 fins a n, ja que les subcadenes de longitud 1
      ja s'han omplert a inicialitzacio()
    - i (posició d'inici): indica on comença la subcadena dins la paraula
    - k (punt de tall): divideix la subcadena [i, i+l] en dues parts:
        · part esquerra: [i, i+k]      de longitud k
        · part dreta:    [i+k, i+l]    de longitud l-k

    Finalment, comprova si algun símbol d'inici pot generar tota la paraula,
    és a dir, si P[0, n, j] és True per algun símbol d'inici j.

    Retorna True si la paraula és acceptada, False altrament.
    """

    P, simbols_index, index_simbols_inici = inicialitzacio(paraula, gramatica)
    n = len(paraula)

    # Subcadenes de longitud l (de 2 fins a n -> la longitud 1 s'han inicialitzat a l'anterior funció)
    for l in range(2, n + 1):
        for i in range(n - l + 1):     # posició d'inici (ON ESTEM)
            for k in range(1, l):      # punt de tall
                for prod in gramatica['tranformacions']:
                    if len(prod) == 3:  # producció binària: Rj -> Rb Rc
                        Rj, Rb, Rc = prod
                        j = simbols_index[Rj]
                        b = simbols_index[Rb]
                        c = simbols_index[Rc]
                        if P[i, k, b] and P[i + k, l - k, c]:
                            P[i, l, j] = True

    paraula_acceptada = any(P[0, n, j] for j in index_simbols_inici)
    return paraula_acceptada