from CKY_algoritme import cyk_algoritme
import ast


def carregar_problemes(nombre_fichero):
    problemes = []

    with open(nombre_fichero, "r", encoding="utf-8") as f:
        contenido = f.read()

    bloques = contenido.split("Problema ")

    for bloque in bloques:
        bloque = bloque.strip()

        if not bloque:
            continue

        lineas = [
            linea.strip()
            for linea in bloque.splitlines()
            if linea.strip()
        ]

        numero_problema = int(lineas[0])

        paraula = ast.literal_eval(
            lineas[1].split(":", 1)[1].strip()
        )

        simbols = ast.literal_eval(
            lineas[2].split(":", 1)[1].strip()
        )

        inici = ast.literal_eval(
            lineas[3].split(":", 1)[1].strip()
        )

        # -------- leer transformacions multilínea --------
        idx = 4

        transformacions_text = (
            lineas[idx]
            .split(":", 1)[1]
            .strip()
        )

        idx += 1

        while "]" not in transformacions_text:
            transformacions_text += "\n" + lineas[idx]
            idx += 1

        transformacions = ast.literal_eval(
            transformacions_text
        )

        # -------- respuesta correcta opcional --------
        resposta_correcta = None

        if idx < len(lineas) and lineas[idx].startswith("resposta correcta:"):
            resposta_correcta = ast.literal_eval(
                lineas[idx].split(":", 1)[1].strip()
            )

        gramatica = {
            'simbols': simbols,
            'inici': inici,
            'transformacions': transformacions
        }

        problemes.append({
            "numero": numero_problema,
            "paraula": paraula,
            "gramatica": gramatica,
            "resposta_correcta": resposta_correcta
        })

    return problemes


problemes = carregar_problemes("joc_de_proves.txt")

for problema in problemes:

    resultat = cyk_algoritme(
        problema["paraula"],
        problema["gramatica"]
    )

    num = problema["numero"]
    esperat = problema["resposta_correcta"]

    if esperat is not None:
        estat = "OK" if resultat == esperat else "ERROR"

        print(
            f"Problema {num} | "
            f"Resultat: {resultat} | "
            f"Resposta correcta: {esperat} | "
            f"{estat}"
        )

    else:
        print(
            f"Problema {num} | "
            f"Resultat: {resultat}"
        )