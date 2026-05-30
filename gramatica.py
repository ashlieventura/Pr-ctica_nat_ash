class Gramatica:
    def __init__(self, simbols, inici, transformacions):
        self.simbols = simbols
        self.inici = inici
        self.transformacions = transformacions

        self._validar_cnf()

        self._crear_index()
        self._separar_transformacions()
        self._indexar_transformacions_binaries()

    def _crear_index(self):
        self.simbols_index = {
            s: i for i, s in enumerate(self.simbols)
        }

        self.index_simbols_inici = [
            self.simbols_index[s]
            for s in self.inici
        ]

    def _separar_transformacions(self):
        self.transformacions_terminals = []
        self.transformacions_binaries = []

        for prod in self.transformacions:
            if self.es_terminal(prod):
                self.transformacions_terminals.append(prod)

            elif self.es_binaria(prod):
                self.transformacions_binaries.append(prod)

    def _indexar_transformacions_binaries(self):
        self.transformacions_binaries_indexades = []

        for Rj, Rb, Rc in self.transformacions_binaries:
            self.transformacions_binaries_indexades.append(
                (
                    self.simbols_index[Rj],
                    self.simbols_index[Rb],
                    self.simbols_index[Rc]
                )
            )    

    def es_terminal(self, produccio):
        return len(produccio) == 2

    def es_binaria(self, produccio):
        return len(produccio) == 3
        
    def _validar_cnf(self):

        simbols_set = set(self.simbols)

        for s in self.inici:
            if s not in simbols_set:
                raise ValueError(
                    f"Símbol inicial invàlid: {s}"
                )

        for prod in self.transformacions:

            if len(prod) == 2:
                esquerra, terminal = prod

                if esquerra not in simbols_set:
                    raise ValueError(
                        f"Símbol desconegut: {esquerra}"
                    )

            elif len(prod) == 3:
                esquerra, b, c = prod

                for s in (esquerra, b, c):
                    if s not in simbols_set:
                        raise ValueError(
                            f"Símbol desconegut: {s}"
                        )

            else:
                raise ValueError(
                    f"Producció no CNF: {prod}"
                )