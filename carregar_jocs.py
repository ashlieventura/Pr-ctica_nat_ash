import ast

from gramatica import Gramatica, GramaticaProbabilistica
from CKY import CKY, ProbabilisticCKY


class TestRunner:
    """
    Classe per carregar i executar jocs/proves de gramàtiques amb CKY.
    Detecta automàticament si cada problema és probabilístic o booleà.
    """

    def __init__(self):
        self.problemes = []

    # ------------------------------------------------------------------
    # Mètodes privats compartits
    # ------------------------------------------------------------------

    def _parsejar_bloc(self, bloc):
        """
        Parseja un bloc de text i retorna un diccionari amb els camps del problema.
        Retorna None si el bloc és buit.
        """
        bloc = bloc.strip()
        if not bloc:
            return None

        lineas = [linea.strip() for linea in bloc.splitlines() if linea.strip()]
        numero_problema = int(lineas[0])
        paraula = ast.literal_eval(lineas[1].split(":", 1)[1].strip())
        simbols = ast.literal_eval(lineas[2].split(":", 1)[1].strip())
        inici = ast.literal_eval(lineas[3].split(":", 1)[1].strip())

        # -------- llegir transformacions multilínia --------
        idx = 4
        transformacions_text = lineas[idx].split(":", 1)[1].strip()
        idx += 1

        while "]" not in transformacions_text:
            transformacions_text += ("\n" + lineas[idx])
            idx += 1

        transformacions = ast.literal_eval(transformacions_text)

        # -------- resposta correcta i descripció opcional --------
        resposta_correcta = None
        descripcio = None

        if idx < len(lineas) and lineas[idx].startswith("descripcio:"):
            descripcio = lineas[idx].split(":", 1)[1].strip()
            idx += 1

        if idx < len(lineas) and lineas[idx].startswith("resposta correcta:"):
            resposta_correcta = ast.literal_eval(lineas[idx].split(":", 1)[1].strip())

        return {
            "numero": numero_problema,
            "paraula": paraula,
            "simbols": simbols,
            "inici": inici,
            "transformacions": transformacions,
            "resposta_correcta": resposta_correcta,
            "descripcio": descripcio,
        }

    def _detectar_classe(self, transformacions):
        """
        Retorna GramaticaProbabilistica si alguna producció acaba amb float,
        Gramatica altrament.
        """
        if any(isinstance(prod[-1], float) for prod in transformacions):
            return GramaticaProbabilistica
        return Gramatica

    # ------------------------------------------------------------------
    # Càrrega i execució
    # ------------------------------------------------------------------

    def carregar(self, fitxer):
        """
        Carrega els problemes des d'un fitxer de text.
        Detecta automàticament si cada problema és probabilístic o booleà.
        :param fitxer: Ruta al fitxer de problemes.
        """
        self.problemes = []
        with open(fitxer, "r", encoding="utf-8") as f:
            contingut = f.read()

        for bloc in contingut.split("Problema "):
            camps = self._parsejar_bloc(bloc)
            if camps is not None:
                classe = self._detectar_classe(camps["transformacions"])
                try:
                    gramatica = classe(
                        simbols=camps["simbols"],
                        inici=camps["inici"],
                        transformacions=camps["transformacions"]
                    )
                    self.problemes.append({
                        "numero": camps["numero"],
                        "paraula": camps["paraula"],
                        "gramatica": gramatica,
                        "resposta_correcta": camps["resposta_correcta"],
                        "descripcio": camps["descripcio"],
                        "error": None
                    })
                except ValueError as e:
                    self.problemes.append({
                        "numero": camps["numero"],
                        "paraula": camps["paraula"],
                        "gramatica": None,
                        "resposta_correcta": camps["resposta_correcta"],
                        "descripcio": camps["descripcio"],
                        "error": str(e)
                    })

    def executar(self, tolerancia=1e-6):
        """
        Executa tots els problemes carregats.
        Els problemes probabilístics es comparen amb tolerància;
        els booleans amb igualtat exacta.
        :param tolerancia: Diferència màxima permesa per als probabilístics.
        """
        if not self.problemes:
            print("No hi ha problemes.")
            return

        for problema in self.problemes:
            num = problema["numero"]
            desc_str = f" | {problema['descripcio']}" if problema["descripcio"] else ""

            if problema["error"]:
                print(f"Problema {num}{desc_str}\n      ERROR DE GRAMÀTICA: {problema['error']}\n")
            else:
                gramatica = problema["gramatica"]
                print(f"Problema {num}{desc_str}")
                if gramatica.convertida:
                    print("[GRAMÀTICA CONVERTIDA A CNF]")
                print(gramatica)
                print(f"  Paraula: '{problema['paraula']}'")

                if isinstance(gramatica, GramaticaProbabilistica):
                    cky = ProbabilisticCKY(gramatica)
                    resultat = cky.accepta_prob(problema["paraula"])
                    esperat = problema["resposta_correcta"]
                    if esperat is not None:
                        estat = "OK" if abs(resultat - esperat) <= tolerancia else "ERROR"
                        print(f"  Resultat: {resultat:.6f} | Resposta correcta: {esperat:.6f} | {estat}\n")
                    else:
                        print(f"  Resultat: {resultat:.6f}\n")
                else:
                    cky = CKY(gramatica)
                    resultat = cky.accepta(problema["paraula"])
                    esperat = problema["resposta_correcta"]
                    if esperat is not None:
                        estat = "OK" if resultat == esperat else "ERROR"
                        print(f"  Resultat: {resultat} | Resposta correcta: {esperat} | {estat}\n")
                    else:
                        print(f"  Resultat: {resultat}\n")