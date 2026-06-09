# CKY Parser

Implementació de l'algorisme **CKY** (Cocke–Kasami–Younger) per reconèixer paraules a partir de gramàtiques en Forma Normal de Chomsky (CNF). Suporta gramàtiques booleanes i probabilístiques (PCFG), i detecta automàticament el tipus de cada problema.

---

## Requisits

- Python 3.8+
- NumPy

```bash
pip install numpy
```

---

## Estructura del projecte

```
.
├── main.py            # Punt d'entrada
├── carregar_jocs.py   # Càrrega i execució de fitxers de proves
├── gramatica.py       # Classes Gramatica i GramaticaProbabilistica
├── CKY.py             # Algorismes CKY i ProbabilisticCKY
└── *.txt              # Fitxers de problemes
```

---

## Ús

```bash
python3 main.py <fitxer> [--tolerancia VALOR] [--output FITXER]
```

### Arguments

| Argument | Descripció | Default |
|---|---|---|
| `fitxer` | Fitxer de problemes `.txt` | — |
| `--tolerancia` | Tolerància per comparar probabilitats | `1e-6` |
| `--output` | Desa els resultats en un fitxer de text | — |

### Exemples

```bash
# Execució bàsica
python3 main.py jp2.txt

# Amb tolerància personalitzada
python3 main.py jp2.txt --tolerancia 1e-4

# Desant resultats a un fitxer (també es mostra per pantalla)
python3 main.py jp2.txt --output resultats.txt

# Tot junt
python3 main.py jp2.txt --tolerancia 1e-4 --output resultats.txt
```

---

## Format del fitxer de problemes

Cada problema es defineix amb el prefix `Problema` seguit del número. Els camps `descripcio` i `resposta correcta` són opcionals.

### Problema booleà

```
Problema 1
paraula: "ab"
simbols: ["S", "A", "B"]
inici: ["S"]
transformacions: [("S", "A", "B"), ("A", "a"), ("B", "b")]
descripcio: exemple senzill
resposta correcta: True
```

### Problema probabilístic

Les produccions inclouen la probabilitat com a últim element `float`. Les probabilitats de cada símbol han de sumar `1.0`.

```
Problema 2
paraula: "ab"
simbols: ["S", "A", "B"]
inici: ["S"]
transformacions: [("S", "A", "B", 1.0), ("A", "a", 1.0), ("B", "b", 1.0)]
descripcio: exemple probabilístic
resposta correcta: 1.0
```

Els dos tipus es poden barrejar en el mateix fitxer. El programa detecta automàticament quin tipus és cada problema.

---

## Gramàtica

La classe `Gramatica` accepta qualsevol gramàtica i la converteix automàticament a CNF si cal. La conversió segueix els passos:

1. Eliminació de produccions epsilon
2. Eliminació de produccions unitàries
3. Eliminació de símbols inútils
4. Substitució de terminals en produccions mixtes
5. Binarització

`GramaticaProbabilistica` fa el mateix propagant les probabilitats en cada pas.
