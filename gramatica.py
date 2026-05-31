import itertools

class Gramatica:
    def __init__(self, simbols, inici, transformacions):
        """
        Inicialitza una gramàtica en Forma Normal de Chomsky (CNF).
        :param simbols: Llista de símbols no terminals i terminals.
        :param inici: Llista de símbols inicials.
        :param transformacions: Llista de produccions (tuples).
        """
        self.simbols = set(simbols)
        self.inici = inici
        self.transformacions = set(transformacions)

        try:
            self._validar_gramatica()
            if not self.es_cnf():
                self._convertir_a_cnf()
            self._validar_cnf()
        except ValueError as e:
            raise ValueError(f"Error a la gramàtica: {e}") from e

        self._crear_index() # Crea índexs per accés ràpid als símbols
        self._separar_transformacions()  # Separa produccions terminals i binàries
        self._indexar_transformacions_binaries()  # Indexa produccions binàries



    def _crear_index(self):
        """
        Crea un diccionari per accedir als símbols per índex i viceversa.
        """
        self.simbols_index = {
            s: i for i, s in enumerate(self.simbols)
        }

        self.index_simbols_inici = [
            self.simbols_index[s]
            for s in self.inici
        ]

    def _separar_transformacions(self):
        """
        Separa les produccions terminals (A -> a) i binàries (A -> B C).
        """
        self.transformacions_terminals = []
        self.transformacions_binaries = []

        for prod in self.transformacions:
            if self._es_terminal(prod):
                self.transformacions_terminals.append(prod)

            elif self._es_binaria(prod):
                self.transformacions_binaries.append(prod)

    def _indexar_transformacions_binaries(self):
        """
        Indexa les produccions binàries per treballar amb índexs en lloc de símbols.
        """
        self.transformacions_binaries_indexades = []

        for Rj, Rb, Rc in self.transformacions_binaries:
            self.transformacions_binaries_indexades.append(
                (
                    self.simbols_index[Rj],
                    self.simbols_index[Rb],
                    self.simbols_index[Rc]
                )
            )    

    def _es_terminal(self, produccio):
        """
        Comprova si una producció és terminal (A -> a).
        :param produccio: Tuple de la producció.
        :return: True si és terminal, False altrament.
        """
        return len(produccio) == 2

    def _es_binaria(self, produccio):
        """
        Comprova si una producció és binària (A -> B C).
        :param produccio: Tuple de la producció.
        :return: True si és binària, False altrament.
        """
        return len(produccio) == 3


    def es_cnf(self):
        """Comprova si la gramàtica ja està en CNF."""
        try:
            self._validar_cnf()
            return True
        except ValueError:
            return False


    def _validar_gramatica(self):
        if not self.inici:
            raise ValueError("La llista de símbols inicials és buida.")
        
        if not self.simbols:
            raise ValueError("La llista de símbols és buida.")
        
        if not self.transformacions:
            raise ValueError("La llista de transformacions és buida.")

        for s in self.inici:
            if s not in self.simbols:
                raise ValueError(f"Símbol inicial '{s}' no està a la llista de símbols.")
            

    def _validar_cnf(self):
        """Valida que la gramàtica compleixi la Forma Normal de Chomsky (CNF)."""

        if not self.inici:
            raise ValueError("La llista de símbols inicials és buida.")

        for s in self.inici:
            if s not in self.simbols:
                raise ValueError(f"Símbol inicial '{s}' no està a la llista de símbols.")

        for prod in self.transformacions:
            esquerra = prod[0]
            if esquerra not in self.simbols:
                raise ValueError(f"Símbol esquerra '{esquerra}' no està a la llista de símbols.")

            if len(prod) == 2:
                terminal = prod[1]
                if terminal == ' ' and esquerra not in self.inici:
                    raise ValueError(f"Producció epsilon '{prod}' només permesa per al símbol inicial.")
                if terminal in self.simbols:
                    raise ValueError(f"Producció unitària '{prod}' no permesa en CNF.")

            elif len(prod) == 3:
                for s in prod[1:]:
                    if s not in self.simbols:
                        raise ValueError(f"Símbol '{s}' a la producció {prod} no està a la llista de símbols.")

            else:
                raise ValueError(f"Producció no CNF (longitud invàlida): {prod}")


    def _convertir_a_cnf(self):
        self._eliminar_epsilon()
        self._eliminar_unitaries()
        self._eliminar_simbols_inutils()
        self._substituir_terminals_barrejats()
        self._binaritzar()
        return self
        

    def _eliminar_epsilon(self):
        anulables = {prod[0] for prod in self.transformacions if len(prod) == 2 and prod[1] == ' '}
        
        canvi = True
        while canvi:
            canvi = False
            for prod in self.transformacions:
                if prod[0] not in anulables:
                    dreta = prod[1:]
                    if dreta and all(s in anulables for s in dreta):
                        anulables.add(prod[0])
                        canvi = True

        noves_trans = set()
        for prod in self.transformacions:
            if len(prod) != 2 or prod[1] != ' ':
                dreta = prod[1:]
                posicions_anulables = [i for i, s in enumerate(dreta) if s in anulables]
                for mida in range(len(posicions_anulables) + 1):
                    for omesos in itertools.combinations(posicions_anulables, mida):
                        nova_dreta = tuple(s for i, s in enumerate(dreta) if i not in omesos)
                        if nova_dreta:
                            noves_trans.add((prod[0],) + nova_dreta)

        for s in self.inici:
            if s in anulables:
                noves_trans.add((s, ' '))

        self.transformacions = noves_trans

    def _eliminar_unitaries(self):
        no_terminals = self.simbols
        noves_trans = set()

        for origen in no_terminals:
            visitats = {origen}
            cua = [origen]

            while cua:
                actual = cua.pop()
                for prod in self.transformacions:
                    if prod[0] == actual:
                        if len(prod) == 2 and prod[1] in no_terminals:
                            if prod[1] not in visitats:
                                visitats.add(prod[1])
                                cua.append(prod[1])
                        else:
                            noves_trans.add((origen,) + prod[1:])

        self.transformacions = noves_trans
                

    def _eliminar_simbols_inutils(self):
        productius = set()
        canvi = True
        while canvi:
            canvi = False
            for prod in self.transformacions:
                if prod[0] not in productius:
                    dreta = prod[1:]
                    if all(s in productius or s not in self.simbols for s in dreta):
                        productius.add(prod[0])
                        canvi = True

        accessibles = set(self.inici)
        cua = list(self.inici)
        while cua:
            actual = cua.pop()
            for prod in self.transformacions:
                if prod[0] == actual:
                    for s in prod[1:]:
                        if s in self.simbols and s not in accessibles:
                            accessibles.add(s)
                            cua.append(s)

        utils = productius.intersection(accessibles)
        simbols_originals = self.simbols
        self.simbols = utils
        self.transformacions = {
            prod for prod in self.transformacions
            if prod[0] in utils and all(s in utils or s not in simbols_originals for s in prod[1:])
        }
        


    # Funció auxiliar de _substituir_terminals_barrejats i _binaritzar
    def _nou_simbol(self, prefix, comptador):
        comptador += 1
        nou_sim = f"{prefix}_{comptador}"
        while nou_sim in self.simbols:
            comptador += 1
            nou_sim = f"{prefix}_{comptador}"
        self.simbols.add(nou_sim)
        return nou_sim, comptador


    def _substituir_terminals_barrejats(self):
        noves_trans = set()
        mapa_terminals = {}  # "a" -> "T_1", per reutilitzar les noves transformacions
        comptador = 0

        for t in self.transformacions:
            if len(t) > 2:
                t = list(t)
                for i in range(1, len(t)):
                    if t[i] not in self.simbols:
                        terminal = t[i]
                        if terminal not in mapa_terminals:
                            nou_sim, comptador = self._nou_simbol("T", comptador)
                            noves_trans.add((nou_sim, terminal))
                            mapa_terminals[terminal] = nou_sim
                        t[i] = mapa_terminals[terminal]
                noves_trans.add(tuple(t))
            else:
                noves_trans.add(t)

        self.transformacions = noves_trans


    def _binaritzar(self):
        noves_trans = set()
        comptador = 0

        for t in self.transformacions:
            if len(t) > 3:
                t = list(t)
                esquerra = t[0]

                for idx in range(1, len(t) - 2):
                    nou_sim, comptador = self._nou_simbol("X", comptador)
                    noves_trans.add((esquerra, t[idx], nou_sim))
                    esquerra = nou_sim

                noves_trans.add((esquerra, t[-2], t[-1]))
            else:
                noves_trans.add(t)

        self.transformacions = noves_trans

                    
        
