# baby_aes_linear_attack.py
import json
import csv
from sage.all import *
from sage.crypto.sbox import SBox
from itertools import *

# --- Constantes ---
ROUNDS = 3
STATE_ARRAY_ROWS = 2
STATE_ARRAY_COLS = 2
EXPONENT = 4

# Instancia Baby-AES
aes = mq.SR(ROUNDS, STATE_ARRAY_ROWS, STATE_ARRAY_COLS, EXPONENT,
            allow_zero_inversions=True, star=True)
F = aes.base_ring()
f2 = GF(2)

subBytes = aes.sbox()
invS = SBox(14, 13, 4, 12, 3, 2, 0, 6, 15, 8, 7, 1, 11, 9, 5, 10)

# --- Lectura CSV ---
def readData(namefile):
    with open(namefile, 'r', newline='', encoding='utf-8') as archivo_csv:
        lector_csv = csv.reader(archivo_csv)
        next(lector_csv)
        return list(lector_csv)

# Producto interno de 2 elementos(nibbles/bytes) del cifrado
def innerProduct(a, b):
    if len(a) != len(b):
        return -1
    sum = 0
    for i in range(len(a)):
        sum += int(a[i])*int(b[i])
    
    return sum % 2

# Producto interno de una cadena de entrada del cifrador
def innerProductExtended(bitStringA, bitStringB):
    sum = 0
    for nibbleA, nibbleB in zip(bitStringA, bitStringB):
        # Si el nibble/byte es 0 su producto interno es igual a 0
        if nibbleA == "0000":
            continue
        sum += innerProduct(nibbleA, nibbleB)

    return sum % 2

#Funcion que obtiene la matriz de acuerdos para posteriormente generar
#la matriz de correlacion y probabilidad sobre la caja de sustitucion utilizada.
def getAgreementMatrix(sbox):
    matrix = []
    
    for a in range(2**EXPONENT):
        row = []
        for b in range(2**EXPONENT):
            c = 0
            binA = list(f'{a:04b}')
            binB = list(f'{b:04b}')
            for x in range(2**EXPONENT):
                binX = list(f'{x:04b}')
                ax = innerProduct(binA, binX)
                binSx = list(f'{int(sbox[x]):04b}')
                bSx = innerProduct(binB, binSx)
                if ax == bSx:
                    c += 1
                else:
                    c -= 1
            row.append(c)
        matrix.append(row)
            
    return matrix

# Calculo de la matriz de correlacion usado para elegir la mascara de salida b
# para cada nibble activo por ronda.
def calculateCorrMatrix(agreementMatrix):
    corrMatrix = []
    for a in agreementMatrix:
        row = []
        for b in a:
            row.append(b / 16)
        corrMatrix.append(row)
    
    return corrMatrix

# Calculo de la matriz de probabilidad de correlacion usado para elegir la mascara de salida b
# para cada nibble activo por ronda. 
def calculateProbMatrix(corrMatrix):
    probMatrix = []
    for a in corrMatrix:
        row = []
        for b in a:
            row.append((b + 1) / 2)
        probMatrix.append(row)
    
    return probMatrix

# Funcion auxiliar que transforma entradas del tipo:
# ["0001","0010","0011", "0100"]
# a listas del tipo:
# [1, 2, 3, 4]
def bitString2intString(string):
    return [int(str(string[i]),2) for i in range(len(string))]

# Funcion auxiliar que transforma entradas del tipo:
# [1, 2, 3, 4]
# a listas del tipo:
# ["0001","0010","0011", "0100"]
def intString2bitString(numbers):
    return [f'{numbers[i]:04b}' for i in range(len(numbers))]

# Funcion auxiliar que transforma entradas del tipo:
# "1010"
# a salidas del tipo
# a^3 + a      :elemento sobre F2^4
def b2F(bin):
    n = int(str(bin),2)
    return F.fetch_int(n)

# Funcion auxiliar que transforma entradas del tipo:
# "A"
# a salidas del tipo
# "1010"
def h2b(hex):
    n = int(hex, 16)
    return f'{n:04b}'

# Funcion auxiliar que transforma entradas del tipo:
# ["0001","0010","0011", "0100"]
# a salidas del tipo
# Matriz de estado
# [ 1 ][a + 1]
# [ a ][ a^2 ]
def bitString2state(string):
    return aes.state_array([b2F(string[i]) for i in range(4)])

# Funcion auxiliar que transforma entradas del tipo:
# Matriz de estado
# [ 1 ][a + 1]
# [ a ][ a^2 ] 
# a salidas del tipo
#["0001","0010","0011", "0100"]
def state2bitString(state):
    hexstate = aes.hex_str_vector(state)
    return [h2b(hexstate[i]) for i in range(4)]

# Funcion auxiliar que transforma entradas del tipo:
# "1234"
# a salidas del tipo
# Matriz de estado
# [ 1 ][a + 1]
# [ a ][ a^2 ]
def hex2state(hexString):
    binString = []
    for h in list(hexString):
        binString.append(h2b(h))
    
    return bitString2state(binString)


def int2state(n):
    h = f'{n:04x}'
    return hex2state(h)

def Matrix2bitString(matrix):
    transpose = matrix.transpose()
    bits = ""
    for row in transpose.rows():
        for e in row:
            bits += str(e)
    
    bitString = [bits[0:4], bits[4:8], bits[8:12], bits[12:16]]
    return bitString

def bitString2Matrix(b):
    bMatrix = []
    columns = [f'{b[0]}{b[1]}', f'{b[2]}{b[3]}']
    
    for i in range(8):
        row = []
        for j in range(2):
            row.append(columns[j][i])
        bMatrix.append(row)
    
    return matrix(f2, 8, 2, bMatrix)

def mc(b):
    C = matrix(f2, 8, 8, [[1, 0, 1, 1, 0, 0, 1, 1],[1, 1, 0, 0, 1, 0, 0, 0], [0, 1, 1, 0, 0, 1, 0, 0], [0, 0, 1, 1, 0, 0, 1, 0], [0, 0, 1, 1, 1, 0, 1, 1], [1, 0, 0, 0, 1, 1, 0, 0], [0, 1, 0, 0, 0, 1, 1, 0], [0, 0, 1, 0, 0, 0, 1, 1]])
    bm = bitString2Matrix(b)
    res = C * bm

    return bitString2state(Matrix2bitString(res))

def invMixColumns(a):
    for B in product(F, repeat=4):
        b = state2bitString(aes.state_array(list(B)))
        if mc(b) == a:
            return b


def getOutputMask(inputMask, probMatrix):
    nibbleValues = bitString2intString(inputMask)
    outputMaskValues = []
    
    for row in nibbleValues:
        if(row == 0):
            outputMaskValues.append(0)
            # si es una SBox inactiva
            continue
        temp = 0
        output = 0
        for i, p in enumerate(probMatrix[row]):
            if i == 0:
                continue
            bias = abs(p - 0.5)
            if(bias >= temp):
                output = i
                temp = bias
        outputMaskValues.append(output)

    return intString2bitString(outputMaskValues)

def doPermutationBlock(binState):
    stateArray = bitString2state(binState)
    stateArray = aes.shift_rows(stateArray)
    return invMixColumns(stateArray)

def corrRound(a, b, corrMatrix):
    corr = 1.0
    for ai, bi in zip(a, b):
        aValue = int(str(ai), 2)
        if aValue == 0:
            continue
        bValue = int(str(bi), 2)
        corr *= corrMatrix[aValue][bValue]
    
    return corr

def inverseSubBytes(state):
    b = state2bitString(state)
    reverse = [f'{invS(int(str(b[i]), 2)):04b}' for i in range(len(b))]
        
    return reverse

def hex2bitString(hexString):
    return state2bitString(hex2state(hexString))


def printMatrix(matrix):
    for row in matrix:
        print("[", end="")
        for index, i in enumerate(row):
            if index == 0:
                print(f"{i}", end="\t")
            else:
                print(f", {i}", end="\t")
        print("]")
    
    return

def generatePossibleKeys(lastInputMask):
    maskState = bitString2state(lastInputMask)
    maskAfterShiftRows = state2bitString(aes.shift_rows(maskState))
    keys = []
    inactiveNibbles = []
    activeNibbles = 4
    for index, nibble in enumerate(maskAfterShiftRows):
        if nibble == "0000":
            inactiveNibbles.append(index)
            activeNibbles -= 1

    iterations = 2 ** EXPONENT
    for aux in range(iterations**activeNibbles):
        key = []
        cont = 0
        for i in range(3, -1, -1):
            if i in inactiveNibbles:
                key.append("0000")
                continue
            if cont == 0:
                key.append(f'{(aux & 15):04b}')
            if cont == 1:
                key.append(f'{((aux >> 4) & 15):04b}')
            if cont == 2:
                key.append(f'{((aux >> 8) & 15):04b}')
            if cont == 3:
                key.append(f'{((aux >> 12) & 15):04b}')
            cont += 1
        keys.append(key)
    
    return keys

# --- Ataque lineal ---
def getLinealAproach(inputMask, probMatrix, corrMatrix):
    a = inputMask
    corr = 1
    for i in range(ROUNDS - 1):
        b = getOutputMask(a, probMatrix)
        corr *= corrRound(a, b, corrMatrix)
        a = doPermutationBlock(b)
    return (a, corr)

def linear_attack(plaintext_ciphertext_pairs, linear_approximation):
    possible_keys = generatePossibleKeys(linear_approximation[1])
    keyCounter = [0 for _ in possible_keys]
    for pair in plaintext_ciphertext_pairs:
        for i, key in enumerate(possible_keys):
            y = hex2state(pair[1])
            pk = bitString2state(key)
            w = aes.add_round_key(y, pk)
            v = aes.shift_rows(w)
            u = inverseSubBytes(v)
            if(innerProductExtended(linear_approximation[0], hex2bitString(pair[0])) ==
               innerProductExtended(linear_approximation[1], u)):
                keyCounter[i] += 1
            else:
                keyCounter[i] -= 1
    max_cont = max(keyCounter, key=abs)
    index = keyCounter.index(max_cont)
    key = possible_keys[index]
    return (possible_keys, keyCounter, key)

# --- Main ---
agreementMatrix = getAgreementMatrix(subBytes)
corrMatrix = calculateCorrMatrix(agreementMatrix)
probMatrix = calculateProbMatrix(corrMatrix)

inputMask1 = ["0010", "0000", "0000", "1000"]
inputMask3, corr = getLinealAproach(inputMask1, probMatrix, corrMatrix)

plaintext_ciphertext_pairs = readData("plaintext_ciphertext_pairs.csv")
linear_approximation = [inputMask1, inputMask3]

possibleKeys, keyCounter, bestKey = linear_attack(plaintext_ciphertext_pairs, linear_approximation)

# --- Exportar resultado como JSON ---
result = {
    "a1": inputMask1,
    "a3": inputMask3,
    "correlation": abs(corr),
    "best_key": bestKey,
    "top_count": max(keyCounter, key=abs)
}

print(json.dumps(result))
