import numpy as np
from gramatica import Gramatica

class CKY:
    def __init__(self, gramatica: Gramatica):
        """
        Inicialitza l'algorisme CKY amb una gramàtica donada.
        :param gramatica: Objecte de la classe Gramatica.
        """
        self.gramatica = gramatica

    def _inicialitzar_taula(self, paraula):
        """
        Inicialitza la taula tridimensional P[n, n+1, r] per a l'algorisme CKY.
        :param paraula: Paraula d'entrada (string o llista de símbols).
        :return: Taula P de booleans, on P[i, l, j] indica si el símbol j pot generar la subcadena de longitud l que comença a i.
        """
        n = len(paraula)
        r = len(self.gramatica.simbols)
        simbols_index = self.gramatica.simbols_index
        trans_terminals = self.gramatica.transformacions_terminals
        P = np.zeros((n, n + 1, r), dtype=bool)

        # Omple la taula per produccions terminals (A -> a)
        for i in range(n):
            ai = paraula[i]
            for prod in trans_terminals:
                Rj, terminal = prod
                if terminal == ai:
                    j = simbols_index[Rj]
                    P[i, 1, j] = True  # longitud 1 (1-indexed)

        return P


    def accepta(self, paraula):
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
        n = len(paraula)
        if n == 0:
            return any((s, ' ') in self.gramatica.transformacions for s in self.gramatica.inici)
    
        P = self._inicialitzar_taula(paraula)
        index_simbols_inici = self.gramatica.index_simbols_inici
        trans_bi = self.gramatica.transformacions_binaries_indexades

        # Omple la taula per subcadenes de longitud >= 2
        for l in range(2, n + 1):
            for i in range(n - l + 1):
                for k in range(1, l):
                    for j, b, c in trans_bi:
                        if P[i, k, b] and P[i + k, l - k, c]:
                            P[i, l, j] = True

        paraula_acceptada = any(P[0, n, j] for j in index_simbols_inici)
        return paraula_acceptada
    


class ProbabilisticCKY(CKY):
    def _inicialitzar_taula_prob(self, paraula):    
        n = len(paraula)
        r = len(self.gramatica.simbols)
        simbols_index = self.gramatica.simbols_index
        trans_terminals = self.gramatica.transformacions_terminals
        P = np.zeros((n, n + 1, r), dtype=float)

        # Omple la taula per produccions terminals (A -> a) amb major probabilitat
        for i in range(n):
            ai = paraula[i]
            for prod in trans_terminals:
                Rj, terminal, prob = prod
                if terminal == ai:
                    j = simbols_index[Rj]
                    if prob > P[i, 1, j]: # si la probabilitat de la nova producció cap aquest terminal és major a la que hi ha es canvia
                        P[i, 1, j] = prob
        return P
        
    def accepta_prob(self, paraula):
        n = len(paraula)
        if n == 0:
            return any((s, ' ') in self.gramatica.transformacions for s in self.gramatica.inici)
    
        P = self._inicialitzar_taula(paraula)
        index_simbols_inici = self.gramatica.index_simbols_inici
        trans_bi = self.gramatica.transformacions_binaries_indexades # aquestes també tenen la probabilitat de cada una de les regles ( transformacions)

        # Omple la taula per subcadenes de longitud >= 2
        for l in range(2, n + 1):
            for i in range(n - l + 1):
                for k in range(1, l):
                    for j, b, c, prob_cadena in trans_bi:
                        prob = prob_cadena * P[i, k, b] * P[i + k, l - k, c] # es calcula la probabilitat de tota la regla 
                        # si A -> B C  la prob = prob(A ->BC)* prob(B)* prob(C)
                        if prob > P[i, l, j]:
                            P[i, l, j] = prob
        millor_prob = max(P[0, n, j] for j in index_simbols_inici) # de totes les solucions amb els simbols inicials possibles agafes el més probable
        return millor_prob  