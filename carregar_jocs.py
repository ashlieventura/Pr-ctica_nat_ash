import ast

from gramatica import Gramatica
from CKY import CKY


class TestRunner:

    def __init__(self):
        self.problemes = []

    def carregar(self, fitxer):

        self.problemes = []
        with open(fitxer, "r", encoding="utf-8") as f:
            contingut = f.read()

        blocs = contingut.split("Problema ")

        for bloc in blocs:

            bloc = bloc.strip()
            if not bloc:
                continue

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

            # -------- resposta correcta opcional --------
            resposta_correcta = None

            if (idx < len(lineas) and lineas[idx].startswith("resposta correcta:")):
                resposta_correcta = ast.literal_eval(lineas[idx].split(":", 1)[1].strip())

            gramatica = Gramatica(simbols=simbols, inici=inici, transformacions=transformacions)

            self.problemes.append({
                "numero": numero_problema,
                "paraula": paraula,
                "gramatica": gramatica,
                "resposta_correcta": resposta_correcta
            })

    def executar(self):

        if not self.problemes:
            print("No hi ha problemes carregats.")
            return

        for problema in self.problemes:

            cky = CKY(problema["gramatica"])
            resultat = cky.accepta(problema["paraula"])
            num = problema["numero"]
            esperat = problema["resposta_correcta"]

            if esperat is not None:

                estat = ("OK" if resultat == esperat else "ERROR")

                print(f"Problema {num} | Resultat: {resultat} | Resposta correcta: {esperat} | {estat}")

            else:
                print(f"Problema {num} | Resultat: {resultat}")

