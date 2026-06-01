import ast

from gramatica import Gramatica
from CKY import CKY


class TestRunner:
    """
    Classe per carregar i executar jocs/proves de gramàtiques amb CKY.
    """

    def __init__(self):
        """
        Inicialitza el TestRunner amb una llista buida de problemes.
        """
        self.problemes = []

    def carregar(self, fitxer):
        """
        Carrega els problemes des d'un fitxer de text.
        :param fitxer: Ruta al fitxer de problemes.
        """
        self.problemes = []
        with open(fitxer, "r", encoding="utf-8") as f:
            contingut = f.read()

        blocs = contingut.split("Problema ")

        for bloc in blocs:
            bloc = bloc.strip()

            if bloc:

                lineas = [linea.strip() for linea in bloc.splitlines() if linea.strip()]
                numero_problema = int(lineas[0])
                paraula = ast.literal_eval(lineas[1].split(":", 1)[1].strip())
                simbols = ast.literal_eval(lineas[2].split(":", 1)[1].strip())
                inici = ast.literal_eval(lineas[3].split(":", 1)[1].strip())

                # -------- llegir transformacions multilínia --------
                idx = 4
                transformacions_text = (lineas[idx].split(":", 1)[1].strip())
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

                try:
                    gramatica = Gramatica(simbols=simbols, inici=inici, transformacions=transformacions)
                    self.problemes.append({
                    "numero": numero_problema,
                    "paraula": paraula,
                    "gramatica": gramatica,
                    "resposta_correcta": resposta_correcta,
                    "descripcio": descripcio,
                    "error": None
                    })

                except ValueError as e:
                    self.problemes.append({
                        "numero": numero_problema,
                        "paraula": paraula,
                        "gramatica": None,
                        "resposta_correcta": resposta_correcta,
                        "descripcio": descripcio,
                        "error": str(e)
                    })
        
                

    def executar(self):
        if not self.problemes:
            print("No hi ha problemes.")
            return

        for problema in self.problemes:
            num = problema["numero"]
            desc_str = f" | {problema['descripcio']}" if problema["descripcio"] else ""

            if problema["error"]:
                print(f"Problema {num}{desc_str}\n      ERROR DE GRAMÀTICA: {problema['error']}\n")
                
            else:
                cky = CKY(problema["gramatica"])
                resultat = cky.accepta(problema["paraula"])
                esperat = problema["resposta_correcta"]

                if esperat is not None:
                    estat = "OK" if resultat == esperat else "ERROR"
                    print(f"Problema {num}{desc_str}\n      Resultat: {resultat} | Resposta correcta: {esperat} | {estat}\n")
                else:
                    print(f"Problema {num}{desc_str}\n      Resultat: {resultat}\n")