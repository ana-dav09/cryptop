# baby_aes_attack.py
import json, os
from sage.all import *
from sage.crypto.sbox import SBox
from itertools import *
import csv

# --- Constantes ---
ROUNDS = 3
STATE_ARRAY_ROWS = 2
STATE_ARRAY_COLS = 2
EXPONENT = 4

# --- Instancia Baby-AES ---
aes = mq.SR(ROUNDS, STATE_ARRAY_ROWS, STATE_ARRAY_COLS, EXPONENT,
            allow_zero_inversions=True, star=True)
F = aes.base_ring()
S = aes.sbox()
invS = SBox(14, 13, 4, 12, 3, 2, 0, 6, 15, 8, 7, 1, 11, 9, 5, 10)

# --- Funciones auxiliares ---
def i2F(n): return F.fetch_int(n)
def hexStrings2states(a, b, c, d):
    aState = aes.state_array([i2F(int(i, 16)) for i in list(a)])
    bState = aes.state_array([i2F(int(i, 16)) for i in list(b)])
    cState = aes.state_array([i2F(int(i, 16)) for i in list(c)])
    dState = aes.state_array([i2F(int(i, 16)) for i in list(d)])
    return (aState, bState, cState, dState)

def readData(namefile):
    with open(namefile, 'r', newline='', encoding='utf-8') as archivo_csv:
        lector_csv = csv.reader(archivo_csv)
        next(lector_csv)  # saltamos header
        return list(lector_csv)

# --- Matriz de frecuencias ---
def F2i(element): return eval(str(element).replace('a', '2').replace('^', "**"))
def getPairsWithDifference(dx):
    return [(x, xStar) for x, xStar in product(F, repeat=2) if x + xStar is dx]
def getAbsoluteFrequency(dx):
    freq = [0 for _ in F]
    for x, xStar in getPairsWithDifference(dx):
        dy = S(x) + S(xStar)
        freq[F2i(dy)] += 1
    return freq
def getFrequencyMatrix():
    return matrix(QQ, 16, 16, [getAbsoluteFrequency(i2F(dx)) for dx in range(F.order())])

# --- Diferenciales ---
def getDifferential(inputArray, freqMatrix):
    differential, freqAcum = [], 1
    for element in inputArray.list():
        if not element.is_unit():
            differential.append(element)
            continue
        diff, temp = 0, 0
        for i, freq in enumerate(freqMatrix[F2i(element)]):
            if freq > temp:
                diff, temp = i, freq
        freqAcum *= temp/16
        differential.append(i2F(diff))
    return (matrix(F, 2, 2, differential), freqAcum)

def doPermutationBlock(stateArray):
    return aes.mix_columns(aes.shift_rows(stateArray))

def getDifferentialTrail(stateArray, freqMatrix):
    propagationRatio, du = 1, stateArray
    for i in range(1, ROUNDS):
        dv, freq = getDifferential(du, freqMatrix)
        propagationRatio *= freq
        du = doPermutationBlock(dv)
    return (du, propagationRatio)

# --- Ataque diferencial ---
def inverseSubBytes(state):
    reverse = [invS(e) for e in state.list()]
    return matrix(F, STATE_ARRAY_ROWS, STATE_ARRAY_COLS, reverse)

def inactivesEqual(y, yStar, du3):
    mask = aes.shift_rows(du3)
    inactivesIndex = [i for i, el in enumerate(mask.list()) if not el.is_unit()]
    for idx, (yi, yStari) in enumerate(zip(y.list(), yStar.list())):
        if idx in inactivesIndex and yi != yStari:
            return False
    return True

def getPossibleKeys(u):
    v = aes.shift_rows(u)
    activeIndex = [i for i, el in enumerate(v.list()) if el.is_unit()]
    keys = []
    for partialKey in product(F, repeat=len(activeIndex)):
        key, aux = [], 0
        for i in range(STATE_ARRAY_ROWS * STATE_ARRAY_COLS):
            if i in activeIndex:
                key.append(partialKey[aux]); aux += 1
            else:
                key.append(i2F(0))
        keys.append(matrix(F, 2, 2, key))
    return keys

def differential_attack(io_pairs, differentials):
    du1, du3 = differentials
    candidateKeys = getPossibleKeys(du3)
    keyCounter = [0 for _ in candidateKeys]
    for xh, xStarh, yh, yStarh in io_pairs:
        x, xStar, y, yStar = hexStrings2states(xh, xStarh, yh, yStarh)
        if not inactivesEqual(y, yStar, du3):
            continue
        for i, key in enumerate(candidateKeys):
            w, wStar = y + key, yStar + key
            u, uStar = inverseSubBytes(aes.shift_rows(w)), inverseSubBytes(aes.shift_rows(wStar))
            if u + uStar == du3:
                keyCounter[i] += 1
    return (candidateKeys, keyCounter)

# --- Ejecución ---
inputS = [i2F(6), i2F(0), i2F(0), i2F(8)]
du1 = aes.state_array(inputS)
freqMatrix = getFrequencyMatrix()
du3, ratio = getDifferentialTrail(du1, freqMatrix)
script_dir = os.path.dirname(os.path.realpath(__file__))
csv_path = os.path.join(script_dir, "plaintext_ciphertext_pairs.csv")
input_output_pairs = readData(csv_path)

keys, counts = differential_attack(input_output_pairs, [du1, du3])
best_key = keys[counts.index(max(counts))]

# Guardamos resultados en JSON para que PyQt los lea
result = {
    "du1": str(du1),
    "du3": str(du3),
    "ratio": str(ratio),
    "best_key": str(best_key),
    "top_count": max(counts)
}

print(json.dumps(result))
