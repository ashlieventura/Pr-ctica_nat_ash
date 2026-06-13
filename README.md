# CKY Parser

Implementació de l'algorisme **CKY** (Cocke–Kasami–Younger) per reconèixer paraules a partir de gramàtiques en Forma Normal de Chomsky (CNF). Suporta gramàtiques booleanes i probabilístiques (PCFG), converteix automàticament qualsevol gramàtica lliure de context a CNF, detecta el tipus de cada problema i, opcionalment, reconstrueix l'arbre de derivació.

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
├── carregar_jocs.py   # Càrrega i execució de fitxers de proves (TestRunner)
├── gramatica.py       # Classes Gramatica i GramaticaProbabilistica
├── CKY.py             # Algorismes CKY i ProbabilisticCKY
└── jp_*.txt           # Fitxers de problemes
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
python3 main.py jp_02_cky_boolea.txt

# Amb tolerància personalitzada
python3 main.py jp_03_cky_probabilistic.txt --tolerancia 1e-4

# Desant resultats a un fitxer (també es mostra per pantalla)
python3 main.py jp_02_cky_boolea.txt --output resultats_jp_02.txt

# Tot junt
python3 main.py jp_03_cky_probabilistic.txt --tolerancia 1e-4 --output resultats.txt
```

---

## Format del fitxer de problemes

Cada problema es defineix amb el prefix `Problema` seguit del número. Els camps obligatoris són `paraula`, `simbols`, `inici` i `transformacions`. Els camps `descripcio`, `arbre` i `resposta correcta` són opcionals.

| Camp | Obligatori | Descripció |
|---|---|---|
| `paraula` | Sí | Cadena (`'ab'`) o llista de paraules (`['the', 'dog']`) |
| `simbols` | Sí | Llista de símbols no terminals |
| `inici` | Sí | Llista de símbols inicials |
| `transformacions` | Sí | Llista de produccions (tuples) |
| `descripcio` | No | Text lliure per identificar el cas |
| `arbre` | No | `True` per mostrar l'arbre de derivació |
| `resposta correcta` | No | Resultat esperat (booleà o nombre) per validar automàticament |

### Problema booleà

```
Problema 1
paraula: 'ab'
simbols: ['S', 'A', 'B']
inici: ['S']
transformacions: [('S', 'A', 'B'), ('A', 'a'), ('B', 'b')]
descripcio: exemple senzill
resposta correcta: True
```

### Problema probabilístic

Les produccions inclouen la probabilitat com a últim element `float`. Les probabilitats de cada símbol han de sumar `1.0`.

```
Problema 2
paraula: 'ab'
simbols: ['S', 'A', 'B']
inici: ['S']
transformacions: [('S', 'A', 'B', 1.0), ('A', 'a', 1.0), ('B', 'b', 1.0)]
descripcio: exemple probabilístic
resposta correcta: 1.0
```

Els dos tipus es poden barrejar en el mateix fitxer: el programa detecta automàticament quin tipus és cada problema segons si les produccions porten probabilitat.

### Reconstrucció de l'arbre de derivació

Amb el camp opcional `arbre: True`, el programa mostra també l'arbre de derivació del problema (el més probable, en el cas probabilístic). Si la paraula no pertany a la gramàtica, ho indica amb `(sense arbre)`.

```
Problema 3
paraula: ['the', 'cat', 'sees', 'the', 'dog']
simbols: ['S', 'NP', 'VP', 'Det', 'N', 'V']
inici: ['S']
transformacions: [('S', 'NP', 'VP'), ('NP', 'Det', 'N'), ('VP', 'V', 'NP'), ('Det', 'the'), ('N', 'cat'), ('N', 'dog'), ('V', 'sees')]
descripcio: anàlisi sintàctica
arbre: True
resposta correcta: True
```

---

## Gramàtica

La classe `Gramatica` accepta qualsevol gramàtica lliure de context i la converteix automàticament a CNF si cal. La conversió segueix els passos:

1. Eliminació de produccions epsilon
2. Eliminació de produccions unitàries
3. Eliminació de símbols inútils (no productius i no accessibles)
4. Substitució de terminals en produccions mixtes
5. Binarització

`GramaticaProbabilistica` fa el mateix propagant les probabilitats en cada pas i renormalitzant quan cal. Si una gramàtica ja està en CNF, la conversió s'omet.

> **Nota:** no cal declarar els símbols terminals. Qualsevol símbol que aparegui a la part dreta d'una producció i que no estigui a la llista `simbols` es tracta automàticament com a terminal.

---

## Components principals

| Fitxer | Classes / funcions | Funció |
|---|---|---|
| `CKY.py` | `CKY`, `ProbabilisticCKY` | Algorisme de reconeixement i reconstrucció de l'arbre |
| `gramatica.py` | `Gramatica`, `GramaticaProbabilistica` | Emmagatzematge, validació i conversió a CNF |
| `carregar_jocs.py` | `TestRunner` | Càrrega i execució dels fitxers de proves |
| `main.py` | — | Punt d'entrada i gestió d'arguments |
