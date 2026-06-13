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

    # ------------------------------------------------------------------
    # Anàlisi amb opció de reconstrucció de la derivació
    # ------------------------------------------------------------------

    def analitza(self, paraula, reconstruir=True):
        """
        Funció despatxadora:
        - si reconstruir=True  -> crida derivacio() i retorna (acceptada, arbre)
        - si reconstruir=False -> crida accepta() i retorna només el booleà
        """
        if reconstruir:
            return self.derivacio(paraula)
        return self.accepta(paraula)

    def derivacio(self, paraula):
        """
        Versió de accepta() que, a més d'omplir la taula P, guarda una taula
        de backpointers per poder reconstruir l'arbre de derivació.

        Esquema de programació dinàmica:
        - P[i, l, j]      -> taula principal (booleana, igual que accepta)
        - back[(i, l, j)] -> taula secundària: recorda COM s'ha obtingut
                             cada cel·la, és a dir (k, b, c).

        Retorna (acceptada, arbre):
        - arbre és None si la paraula no s'accepta.
        - altrament, arbre és una estructura niuada:
          (símbol, fill_esq, fill_dret) als nodes interns
          (símbol, terminal)            a les fulles.
        """
        n = len(paraula)
        if n == 0:
            acceptada = any((s, ' ') in self.gramatica.transformacions for s in self.gramatica.inici)
            return (acceptada, None)

        P = self._inicialitzar_taula(paraula)
        simbols = self.gramatica.simbols
        index_simbols_inici = self.gramatica.index_simbols_inici
        trans_bi = self.gramatica.transformacions_binaries_indexades

        # taula secundària: per cada cel·la marcada com a True, com s'ha aconseguit
        back = {}

        # fulles (longitud 1): recordem quin terminal genera el símbol j a la posició i
        for i in range(n):
            for j in range(len(simbols)):
                if P[i, 1, j]:
                    back[(i, 1, j)] = ('terminal', paraula[i])

        # Omple la taula per subcadenes de longitud >= 2
        for l in range(2, n + 1):
            for i in range(n - l + 1):
                for k in range(1, l):
                    for j, b, c in trans_bi:
                        if P[i, k, b] and P[i + k, l - k, c]:
                            if not P[i, l, j]:          # primera derivació trobada
                                P[i, l, j] = True
                                back[(i, l, j)] = (k, b, c)

        # mirem si algun símbol d'inici genera tota la paraula
        arrel = None
        idx = 0
        while arrel is None and idx < len(index_simbols_inici):
            j = index_simbols_inici[idx]
            if P[0, n, j]:
                arrel = j
            idx += 1

        if arrel is None:
            return (False, None)

        index_simbol = {idx: s for s, idx in self.gramatica.simbols_index.items()}
        arbre = self._reconstruir(index_simbol, back, 0, n, arrel)
        return (True, arbre)

    def _reconstruir(self, index_simbol, back, i, l, j):
        """
        Traceback recursiu (anàleg a trace() de Giving_change.py).
        Reconstrueix l'arbre a partir de la taula de backpointers.
        :param index_simbol: diccionari índex -> nom del símbol.
        """
        info = back[(i, l, j)]
        if info[0] == 'terminal':
            return (index_simbol[j], info[1])
        k, b, c = info
        fill_esq = self._reconstruir(index_simbol, back, i, k, b)
        fill_dret = self._reconstruir(index_simbol, back, i + k, l - k, c)
        return (index_simbol[j], fill_esq, fill_dret)


    @staticmethod
    def format_arbre(arbre, sagnat=0):
        """
        Converteix l'arbre (tuples niuades) en text indentat.
        - node intern: (símbol, fill_esq, fill_dret)
        - fulla:       (símbol, terminal)
        """
        if arbre is None:
            return "      (sense arbre)"

        simbol = arbre[0]
        prefix = "      " + "  " * sagnat

        # fulla: (símbol, terminal)
        if len(arbre) == 2:
            return f"{prefix}{simbol} -> '{arbre[1]}'"

        # node intern: (símbol, fill_esq, fill_dret)
        _, fill_esq, fill_dret = arbre
        linies = [f"{prefix}{simbol}"]
        linies.append(CKY.format_arbre(fill_esq, sagnat + 1))
        linies.append(CKY.format_arbre(fill_dret, sagnat + 1))
        return "\n".join(linies)


class ProbabilisticCKY(CKY):
    def _inicialitzar_taula_prob(self, paraula):
        """
        Inicialitza la taula de probabilitats per a subcadenes de longitud 1.

        Cada cel·la P[i, 1, j] guarda la millor probabilitat amb què el símbol j
        pot generar el terminal situat a la posició i.
        """
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
                    if prob > P[i, 1, j]:  # si la probabilitat de la nova producció cap aquest terminal és major a la que hi ha es canvia
                        P[i, 1, j] = prob
        return P

    def accepta_prob(self, paraula):
        """
        Calcula la probabilitat màxima amb què la gramàtica pot generar la paraula.

        Retorna 0.0 si la paraula no es pot generar i, si es pot, la millor
        probabilitat trobada per a qualsevol símbol inicial.
        """
        n = len(paraula)
        if n == 0:
            return 1.0 if any((s, ' ') in self.gramatica.transformacions for s in self.gramatica.inici) else 0.0

        P = self._inicialitzar_taula_prob(paraula)
        index_simbols_inici = self.gramatica.index_simbols_inici
        trans_bi = self.gramatica.transformacions_binaries_indexades  # aquestes també tenen la probabilitat de cada una de les regles ( transformacions)

        # Omple la taula per subcadenes de longitud >= 2
        for l in range(2, n + 1):
            for i in range(n - l + 1):
                for k in range(1, l):
                    for j, b, c, prob_cadena in trans_bi:
                        prob = prob_cadena * P[i, k, b] * P[i + k, l - k, c]  # es calcula la probabilitat de tota la regla
                        # si A -> B C  la prob = prob(A ->BC)* prob(B)* prob(C)
                        if prob > P[i, l, j]:
                            P[i, l, j] = prob
        millor_prob = max(P[0, n, j] for j in index_simbols_inici)  # de totes les solucions amb els simbols inicials possibles agafes el més probable
        return millor_prob

    # ------------------------------------------------------------------
    # Anàlisi amb opció de reconstrucció de la derivació més probable
    # ------------------------------------------------------------------

    def analitza_prob(self, paraula, reconstruir=True):
        """
        Funció despatxadora (versió probabilística):
        - si reconstruir=True  -> crida derivacio_prob() i retorna (prob, arbre)
        - si reconstruir=False -> crida accepta_prob() i retorna només la probabilitat
        """
        if reconstruir:
            return self.derivacio_prob(paraula)
        return self.accepta_prob(paraula)

    def derivacio_prob(self, paraula):
        """
        Versió de accepta_prob() que guarda backpointers per reconstruir
        l'arbre de derivació MÉS PROBABLE (algorisme de Viterbi sobre CKY).

        - P[i, l, j]      -> taula principal (millor probabilitat)
        - back[(i, l, j)] -> taula secundària amb la decisió (k, b, c) que
                             ha donat aquesta millor probabilitat.

        Retorna (prob, arbre):
        - arbre és None si la probabilitat és 0 (paraula no generable).
        - altrament, arbre és l'estructura niuada de l'arbre més probable.
        """
        n = len(paraula)
        if n == 0:
            prob = 1.0 if any((s, ' ') in self.gramatica.transformacions for s in self.gramatica.inici) else 0.0
            return (prob, None)

        P = self._inicialitzar_taula_prob(paraula)
        simbols = self.gramatica.simbols
        index_simbols_inici = self.gramatica.index_simbols_inici
        trans_bi = self.gramatica.transformacions_binaries_indexades

        back = {}

        # fulles: recordem el terminal que ha donat la millor probabilitat a (i, 1, j)
        for i in range(n):
            for j in range(len(simbols)):
                if P[i, 1, j] > 0:
                    back[(i, 1, j)] = ('terminal', paraula[i])

        # Omple la taula per subcadenes de longitud >= 2
        for l in range(2, n + 1):
            for i in range(n - l + 1):
                for k in range(1, l):
                    for j, b, c, prob_cadena in trans_bi:
                        prob = prob_cadena * P[i, k, b] * P[i + k, l - k, c]
                        if prob > P[i, l, j]:
                            P[i, l, j] = prob
                            back[(i, l, j)] = (k, b, c)  # recordem la millor decisió

        # símbol d'inici amb millor probabilitat
        arrel = None
        millor_prob = 0.0
        for j in index_simbols_inici:
            if P[0, n, j] > millor_prob:
                millor_prob = P[0, n, j]
                arrel = j

        if arrel is None or millor_prob == 0.0:
            return (millor_prob, None)

        index_simbol = {idx: s for s, idx in self.gramatica.simbols_index.items()}
        arbre = self._reconstruir(index_simbol, back, 0, n, arrel)
        return (millor_prob, arbre)