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

        self.convertida = False

        try:
            self._validar_gramatica()
            if not self._es_cnf():
                self._convertir_a_cnf()
                self.convertida = True
            self._validar_cnf()
        except ValueError as e:
            raise ValueError(f"Error a la gramàtica: {e}") from e

        self._crear_index() # Crea índexs per accés ràpid als símbols
        self._separar_transformacions()  # Separa produccions terminals i binàries
        self._indexar_transformacions_binaries()  # Indexa produccions binàries



    @property
    def transformacions(self):
        return self._transformacions

    @transformacions.setter
    def transformacions(self, valor):
        self._transformacions = valor
        self._trans_per_esquerra = {}
        for prod in valor:
            self._trans_per_esquerra.setdefault(prod[0], []).append(prod)

    def _crear_index(self):
        """
        Crea un diccionari per accedir als símbols per índex i viceversa.
        """
        self.simbols_index = {s: i for i, s in enumerate(self.simbols)}
        self.index_simbols_inici = [self.simbols_index[s] for s in self.inici]

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
            self.transformacions_binaries_indexades.append((self.simbols_index[Rj], self.simbols_index[Rb], self.simbols_index[Rc]))    

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


    def _es_cnf(self):
        """Retorna True si la gramàtica compleix CNF, False altrament."""
        if not self.inici:
            return False
        for s in self.inici:
            if s not in self.simbols:
                return False
        for prod in self.transformacions:
            if prod[0] not in self.simbols:
                return False
            if len(prod) == 2:
                terminal = prod[1]
                if terminal == ' ' and prod[0] not in self.inici:
                    return False
                if terminal in self.simbols:
                    return False
            elif len(prod) == 3:
                if any(s not in self.simbols for s in prod[1:]):
                    return False
            else:
                return False
        return True


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
                for prod in self._trans_per_esquerra.get(actual, []):
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
            for prod in self._trans_per_esquerra.get(actual, []):
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

    def __str__(self):
            """
            Retorna una representació llegible de la gramàtica en CNF.
            Les produccions s'agrupen per símbol esquerra i s'ordenen:
            primer els símbols inicials, després la resta alfabèticament.
            """
            # Agrupa produccions per símbol esquerra
            grups = {}
            for prod in self.transformacions:
                esquerra = prod[0]
                dreta = " ".join(
                    f"'{s}'" if s == ' ' else s
                    for s in prod[1:]
                )
                grups.setdefault(esquerra, []).append(dreta)
    
            # Ordena: símbols inicials primer, després la resta
            ordre = self.inici + sorted(grups.keys() - set(self.inici))
    
            lines = [f"Gramàtica CNF  (inici: {self.inici})"]
            lines.append("-" * 40)
            for simbol in ordre:
                if simbol in grups:
                    for dreta in sorted(grups[simbol]):
                        lines.append(f"  {simbol} -> {dreta}")
            return "\n".join(lines)
                     
        

class GramaticaProbabilistica(Gramatica):
    """
    Subclasse de Gramatica que admet probabilitats a les produccions.
    Format de les transformacions:
      - Terminal:  ('A', 'a', prob)       p.ex. ('A', 'a', 0.6)
      - Binaria:   ('S', 'A', 'B', prob)  p.ex. ('S', 'A', 'B', 0.9)
    Les probabilitats de totes les produccions d'un mateix no-terminal
    han de sumar 1.0 (es comprova amb una tolerancia de 1e-6).
    La conversio a CNF propaga les probabilitats correctament.
    """
 
    def __init__(self, simbols, inici, transformacions):
        # Separem la probabilitat de cada produccio ABANS de qualsevol conversio.
        # _prob_map: (esquerra, *dreta) -> prob  i s'actualitza a cada pas.
        self._prob_map = {}
        trans_sense_prob = []

        for prod in transformacions:
            if isinstance(prod[-1], float):
                prob = prod[-1]
                prod_sense = prod[:-1]
            else:
                raise ValueError(f"La produccio {prod} no te probabilitat. Totes les produccions d'una GramaticaProbabilistica han d'acabar amb un float.")
            trans_sense_prob.append(prod_sense)
            self._prob_map[prod_sense] = prob
 
        # Inicialitzem els atributs basics del pare SENSE cridar la seva
        # pipeline de conversio: ho fem nosaltres amb propagacio de probs.
        self.simbols = set(simbols)
        self.inici = inici
        self.transformacions = set(trans_sense_prob)
        self.convertida = False
 
        try:
            self._validar_gramatica()
            self._validar_probabilitats()
            if not self._es_cnf():
                self._convertir_a_cnf_prob()
                self.convertida = True
            self._validar_cnf()
        except ValueError as e:
            raise ValueError(f"Error a la gramatica: {e}") from e
 
        self._crear_index()
        self._separar_transformacions()
        self._indexar_transformacions_binaries_prob()
        self._preparar_terminals_prob()
 
    # ------------------------------------------------------------------
    # Validacio
    # ------------------------------------------------------------------
 
    def _validar_probabilitats(self):
        """
        Comprova que les probabilitats de cada no-terminal sumin 1.0.
        Nomes es validen les produccions originals del _prob_map.
        """
        sumes = {}
        for prod, prob in self._prob_map.items():
            if not (0.0 <= prob <= 1.0):
                raise ValueError(f"La probabilitat {prob} de la produccio {prod} ha de ser entre 0 i 1.")
            esquerra = prod[0]
            sumes[esquerra] = sumes.get(esquerra, 0.0) + prob
 
        for simbol, suma in sumes.items():
            if abs(suma - 1.0) > 1e-6:
                raise ValueError(f"Les probabilitats del simbol '{simbol}' sumen {suma:.6f}, han de sumar 1.0.")
 
    # ------------------------------------------------------------------
    # Conversio a CNF amb propagacio de probabilitats
    # ------------------------------------------------------------------
 
    def _convertir_a_cnf_prob(self):
        self._eliminar_epsilon_prob()
        self._eliminar_unitaries_prob()
        self._eliminar_simbols_inutils()
        self._prob_map = {p: v for p, v in self._prob_map.items() if p in self.transformacions}
        self._substituir_terminals_barrejats_prob()
        self._binaritzar_prob()
 
    def _eliminar_epsilon_prob(self):
        """
        Elimina les produccions epsilon propagant les probabilitats.
        Per a cada simbol anulable, calcula la seva probabilitat d'epsilon
        (prob_eps[A] = prob que A generi la cadena buida).
        Per a cada produccio A -> X1 X2 ... Xn, genera totes les combinacions
        d'omissio dels simbols anulables, multiplicant la prob de la produccio
        per la prob d'epsilon de cada simbol omes i per (1 - prob_eps) dels
        que no s'ometen (per evitar doble comptatge).
        """
        # --- Calcul de prob_eps[A]: prob que A derives epsilon ---
        # Inicialitzem amb les epsilon directes
        prob_eps = {}
        for prod, prob in list(self._prob_map.items()):
            if len(prod) == 2 and prod[1] == ' ':
                prob_eps[prod[0]] = prob_eps.get(prod[0], 0.0) + prob
 
        # Propagacio: A -> B C ... on tots els simbols de la dreta son anulables.
        # Iterem fins a convergencia RECALCULANT prob_eps des de zero a cada
        # iteracio (acumular sobre el valor anterior faria créixer la prob
        # sense limit quan una produccio té tota la dreta anulable).
        canvi = True
        while canvi:
            canvi = False
            nou_prob_eps = {}
            for prod, prob in self._prob_map.items():
                esquerra = prod[0]
                dreta = prod[1:]
                if len(prod) == 2 and prod[1] == ' ':
                    # epsilon directa
                    nou_prob_eps[esquerra] = nou_prob_eps.get(esquerra, 0.0) + prob
                elif dreta and all(s in prob_eps for s in dreta):
                    # prob que tots els simbols de la dreta generin epsilon
                    contribucio = prob
                    for s in dreta:
                        contribucio *= prob_eps[s]
                    nou_prob_eps[esquerra] = nou_prob_eps.get(esquerra, 0.0) + contribucio

            # Comprovem convergencia comparant amb la iteracio anterior
            claus = set(prob_eps) | set(nou_prob_eps)
            for k in claus:
                if abs(nou_prob_eps.get(k, 0.0) - prob_eps.get(k, 0.0)) > 1e-12:
                    canvi = True
                    break
            prob_eps = nou_prob_eps
 
        anulables = set(prob_eps.keys())
 
        # --- Generacio de noves produccions ---
        noves_trans  = set()
        nou_prob_map = {}
 
        for prod, prob_prod in self._prob_map.items():
            if len(prod) == 2 and prod[1] == ' ':
                continue  # les epsilon originals les tractem al final
 
            dreta = prod[1:]
            posicions_anulables = [i for i, s in enumerate(dreta) if s in anulables]
 
            # Per a cada subconjunt de simbols anulables que s'ometen
            for mida in range(len(posicions_anulables) + 1):
                for omesos in itertools.combinations(posicions_anulables, mida):
                    nova_dreta = tuple(s for i, s in enumerate(dreta) if i not in omesos)
                    if not nova_dreta:
                        continue  # seria epsilon, la tractem al final
 
                    # Probabilitat de la nova produccio:
                    # prob_prod * prod(prob_eps[s] per s omes)
                    #           * prod((1-prob_eps[s]) per s anulable no omes)
                    p = prob_prod
                    for i, s in enumerate(dreta):
                        if s in anulables:
                            if i in omesos:
                                p *= prob_eps[s]
                            else:
                                p *= (1.0 - prob_eps[s])
 
                    nova_prod = (prod[0],) + nova_dreta
                    noves_trans.add(nova_prod)
                    # Si la mateixa produccio apareix per camins diferents, sumem
                    nou_prob_map[nova_prod] = nou_prob_map.get(nova_prod, 0.0) + p
 
        # Afegim epsilon per als simbols inicials que eren anulables
        for s in self.inici:
            if s in anulables:
                prod_eps = (s, ' ')
                noves_trans.add(prod_eps)
                nou_prob_map[prod_eps] = prob_eps[s]
 
        self.transformacions = noves_trans
        self._prob_map = nou_prob_map
 
        # Renormalitzem: despres deliminar epsilons, les probs de cada
        # no-terminal han de tornar a sumar 1.0
        sumes = {}
        for prod in self._prob_map:
            sumes[prod[0]] = sumes.get(prod[0], 0.0) + self._prob_map[prod]
        self._prob_map = {prod: prob / sumes[prod[0]] for prod, prob in self._prob_map.items() if sumes[prod[0]] > 0}
 
    def _eliminar_unitaries_prob(self):
        """
        Elimina les produccions unitaries A -> B propagant probabilitats.
        Si hi ha el cami A ->p1 B ->p2 C ->p3 a, genera A -> a [p1*p2*p3].
        Implementat com BFS/DFS sobre el graf de produccions unitaries,
        acumulant el producte de probabilitats al llarg del cami.
        """
        no_terminals = self.simbols
        noves_trans  = set()
        nou_prob_map = {}
 
        for origen in no_terminals:
            # cua: (simbol_actual, prob_acumulada)
            visitats = {origen: 1.0}
            cua = [(origen, 1.0)]
 
            while cua:
                actual, prob_acum = cua.pop()
                for prod, prob in self._prob_map.items():
                    if prod[0] != actual:
                        continue
                    if len(prod) == 2 and prod[1] in no_terminals:
                        # Produccio unitaria: continuem el cami
                        dest = prod[1]
                        nova_prob = prob_acum * prob
                        if dest not in visitats or visitats[dest] < nova_prob:
                            visitats[dest] = nova_prob
                            cua.append((dest, nova_prob))
                    else:
                        # Produccio no unitaria: generem la nova regla
                        nova_prod = (origen,) + prod[1:]
                        p = prob_acum * prob
                        noves_trans.add(nova_prod)
                        nou_prob_map[nova_prod] = nou_prob_map.get(nova_prod, 0.0) + p
 
        self.transformacions = noves_trans
        self._prob_map = nou_prob_map
 
    def _substituir_terminals_barrejats_prob(self):
        """
        Substitueix terminals dins de produccions llargues per simbols auxiliars T_x.
        Les regles auxiliars T_x -> terminal tenen prob 1.0 (nomes una alternativa).
        La prob de la regla original es conserva intacta a la nova regla binaria.
        """
        noves_trans  = set()
        nou_prob_map = {}
        mapa_terminals = {}
        comptador = 0
 
        for prod, prob in self._prob_map.items():
            if len(prod) > 2:
                prod_llista = list(prod)
                for i in range(1, len(prod_llista)):
                    if prod_llista[i] not in self.simbols:
                        terminal = prod_llista[i]
                        if terminal not in mapa_terminals:
                            nou_sim, comptador = self._nou_simbol("T", comptador)
                            prod_aux = (nou_sim, terminal)
                            noves_trans.add(prod_aux)
                            nou_prob_map[prod_aux] = 1.0
                            mapa_terminals[terminal] = nou_sim
                        prod_llista[i] = mapa_terminals[terminal]
                nova_prod = tuple(prod_llista)
                noves_trans.add(nova_prod)
                nou_prob_map[nova_prod] = prob
            else:
                noves_trans.add(prod)
                nou_prob_map[prod] = prob
 
        self.transformacions = noves_trans
        self._prob_map = nou_prob_map
 
    def _binaritzar_prob(self):
        """
        Binaritza produccions de longitud > 3 introduint simbols auxiliars X_x.
        La prob de la regla original va a la primera regla binaria generada.
        Les regles auxiliars X_x -> B C tenen prob 1.0 (nomes una alternativa).
        """
        noves_trans  = set()
        nou_prob_map = {}
        comptador = 0
 
        for prod, prob in self._prob_map.items():
            if len(prod) > 3:
                prod_llista = list(prod)
                esquerra    = prod_llista[0]
                prob_actual = prob  # la prob original va a la primera regla
 
                for idx in range(1, len(prod_llista) - 2):
                    nou_sim, comptador = self._nou_simbol("X", comptador)
                    nova_prod = (esquerra, prod_llista[idx], nou_sim)
                    noves_trans.add(nova_prod)
                    nou_prob_map[nova_prod] = prob_actual
                    prob_actual = 1.0  # les regles auxiliars sempre tenen prob 1.0
                    esquerra    = nou_sim
 
                ultima_prod = (esquerra, prod_llista[-2], prod_llista[-1])
                noves_trans.add(ultima_prod)
                nou_prob_map[ultima_prod] = prob_actual
            else:
                noves_trans.add(prod)
                nou_prob_map[prod] = prob
 
        self.transformacions = noves_trans
        self._prob_map = nou_prob_map
 
    # ------------------------------------------------------------------
    # Indexacio amb probabilitat
    # ------------------------------------------------------------------
 
    def _indexar_transformacions_binaries_prob(self):
        """
        Indexa les produccions binaries afegint la probabilitat com a 4t element:
        (index_j, index_b, index_c, prob)
        """
        self.transformacions_binaries_indexades = []
 
        for Rj, Rb, Rc in self.transformacions_binaries:
            prob = self._prob_map.get((Rj, Rb, Rc), 1.0)
            self.transformacions_binaries_indexades.append(
                (self.simbols_index[Rj], self.simbols_index[Rb], self.simbols_index[Rc], prob)
            )
 
    def _preparar_terminals_prob(self):
        """
        Reescriu la llista de terminals incloent la probabilitat:
        (simbol, terminal, prob)
        """
        terminals_amb_prob = []
        for prod in self.transformacions_terminals:
            Rj, terminal = prod
            prob = self._prob_map.get((Rj, terminal), 1.0)
            terminals_amb_prob.append((Rj, terminal, prob))
        self.transformacions_terminals = terminals_amb_prob
 
    def __str__(self):
        """
        Estén el __str__ del pare afegint la probabilitat a cada produccio.
        """
        grups = {}
        for prod in self.transformacions:
            esquerra = prod[0]
            prob = self._prob_map.get(prod, 1.0)
            dreta = " ".join(f"'{s}'" if s == ' ' else s for s in prod[1:])
            grups.setdefault(esquerra, []).append((dreta, prob))
 
        ordre = self.inici + sorted(grups.keys() - set(self.inici))
 
        lines = [f"Gramatica Probabilistica CNF  (inici: {self.inici})"]
        lines.append("-" * 40)
        for simbol in ordre:
            if simbol in grups:
                for dreta, prob in sorted(grups[simbol]):
                    lines.append(f"  {simbol} -> {dreta:10s} [{prob:.4f}]")
        return "\n".join(lines)