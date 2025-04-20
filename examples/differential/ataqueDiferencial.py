from sage.all import *
from sage.crypto.sbox import SBox
from itertools import *
import csv

# Constantes de baby-AES
ROUNDS = 3
STATE_ARRAY_ROWS = 2
STATE_ARRAY_COLS = 2
EXPONENT = 4

# Definimos los parametros de baby aes
aes = mq.SR(ROUNDS, STATE_ARRAY_ROWS, STATE_ARRAY_COLS, EXPONENT, allow_zero_inversions=True, star=True)
# Obtenemos el campo finito sobre el que opera
F = aes.base_ring()
# Obtenemos la caja de sustitucion
S = aes.sbox()
invS = SBox(14, 13, 4, 12, 3, 2, 0, 6, 15, 8, 7, 1, 11, 9, 5, 10)

#Funcion para leer un CSV con los pares entrada salida
# input: namefile.csv
# output: lista de pares entrada salida en hexadecimal
def readData(namefile):
    try:
        with open(namefile, 'r', newline='', encoding='utf-8') as archivo_csv:
            lector_csv = csv.reader(archivo_csv)
            header = next(lector_csv)  # Lee la primera fila como encabezado
            data = list(lector_csv)
            return data

    except FileNotFoundError:
        print(f'El archivo "{namefile}" no fue encontrado.')
    except Exception as e:
        print(f'Ocurrió un error al leer el archivo CSV: {e}')
    
# Funcion para convertir un elemento de campo finito a entero
def F2i(element):
    return eval(str(element).replace('a', '2').replace('^', "**"))

# Funcion para convertir un entero a un elemento dentro del campo finito del algoritmo
def i2F(n):
    return F.fetch_int(n)

def hexStrings2states(a, b, c, d):
    aState = aes.state_array([i2F(int(i, 16)) for i in list(a)])
    bState = aes.state_array([i2F(int(i, 16)) for i in list(b)])
    cState = aes.state_array([i2F(int(i, 16)) for i in list(c)])
    dState = aes.state_array([i2F(int(i, 16)) for i in list(d)])

    return (aState, bState, cState, dState)

# Funcion que obtiene todos los pares de elementos dentro del campo finito que tienen
# una diferencia de dx
def getPairsWithDifference(dx):
    pairs = []
    for x, xStar in product(F, repeat=2):
        if x + xStar is dx:
            pairs.append((x, xStar))
    
    return pairs

# Funcion que obtiene las frequencias
def getAbsoluteFrequency(dx):
    freq = [0 for _ in F]
    pairs = getPairsWithDifference(dx)
    for x, xStar in pairs:
        dy = S(x) + S(xStar)
        freq[F2i(dy)] += 1

    return freq

# Funcion para obtener la matriz de frecuencias absolutas dx/dy
def getFrequencyMatrix():
    array = []
    for dx in range(F.order()):
        row = getAbsoluteFrequency(i2F(dx))
        array.append(row)
    
    return matrix(QQ, 16,16, array)

# Funcion que obtiene por cada elemento de la matriz de sustitucion, el differencial con 
# mayor ratio de propagacion y retorna la matriz de estado con los differenciales encotrados
def getDifferential(inputArray, freqMatrix):
    differential = []
    freqAcum = 1
    for element in inputArray.list():
        if not element.is_unit():
            differential.append(element)
            continue
        diff = 0
        temp = 0
        for i, freq in enumerate(freqMatrix[F2i(element)]):
            if freq > temp:
                diff = i
                temp = freq
        freqAcum *= temp/16
        differential.append(i2F(diff))
    
    return (matrix(F, 2, 2, differential), freqAcum)

# Funcion que realiza las operaciones de permutacion del algoritmo, en este caso Shift Rows y Mix Columns
def doPermutationBlock(stateArray):
    res = aes.shift_rows(stateArray)
    return aes.mix_columns(res)

# Funcion que obtiene el differential trail sobre un differencial de entrada dado
def getDifferentialTrail(stateArray, freqMatrix):
    propagationRatio = 1
    du = stateArray
    for i in range(1, ROUNDS):
        dv, freq = getDifferential(du, freqMatrix)
        # algo

        propagationRatio *= freq
        du = doPermutationBlock(dv)
    
    return (du, propagationRatio)

# Funcion que genera las posibles llaves para el ataque differencial
def getPossibleKeys(u):
    v = aes.shift_rows(u)
    active = 0
    activeIndex = []
    for i, element in enumerate(v.list()):
        if element.is_unit():
            active += 1
            activeIndex.append(i)

    keys = []
    for partialKey in product(F, repeat=active):
        key = []
        aux = 0
        for i in range(STATE_ARRAY_ROWS * STATE_ARRAY_COLS):
            if i in activeIndex:
                key.append(partialKey[aux])
                aux += 1
            else:
                key.append(i2F(0))
        
        keys.append(matrix(F, 2, 2, key))
    
    return keys

def inverseSubBytes(state):
    reverse = [invS(e) for e in state.list()]
    return matrix(F, STATE_ARRAY_ROWS, STATE_ARRAY_COLS, reverse)

def inactivesEqual(y, yStar, du3):
    mask = aes.shift_rows(du3)
    inactivesIndex = []
    for i, element in enumerate(mask.list()):
        if not element.is_unit():
            inactivesIndex.append(i)

    flag = True
    aux = 0
    for yi, yStari in zip(y.list(), yStar.list()):
        if not aux in inactivesIndex:
            continue
        if yi == yStari:
            flag = flag and True
        else:
            flag = flag and False
    
    return flag

def differential_attack(io_pairs, differentials):
    du1, du3 = differentials
    candidateKeys = getPossibleKeys(du3)
    keyCounter = [0 for _ in candidateKeys]
    for xh, xStarh, yh, yStarh in io_pairs:
        x, xStar, y, yStar = hexStrings2states(xh, xStarh, yh, yStarh)
        # Filter
        if not inactivesEqual(y, yStar, du3):
            continue
        
        for i, key in enumerate(candidateKeys):
            w = y + key
            wStar = yStar + key
            v = aes.shift_rows(w)
            vStar = aes.shift_rows(wStar)
            u = inverseSubBytes(v)
            uStar = inverseSubBytes(vStar)
            du3Prime = u + uStar
            if du3Prime == du3:
                keyCounter[i] += 1 

    return (candidateKeys, keyCounter)

            

    
# Ejemplo
inputS = [i2F(6), i2F(0), i2F(0), i2F(8)]
du1 = aes.state_array(inputS)
freqMatrix = getFrequencyMatrix()

print(f"Δu1: \n{du1}")
du3, ratio = getDifferentialTrail(du1, freqMatrix)

print(f"\nΔu3: \n{du3}")
print(f"\nPropagation ratio: {ratio}")

print("Leyendo pares entrada/salida...")
input_output_pairs = readData("plaintext_ciphertext_pairs.csv")
differentials = [du1, du3]

print("Iniciando ataque differencial...")
possibleKeys, keyCounter = differential_attack(input_output_pairs, differentials)
max_cont = max(keyCounter)
index = keyCounter.index(max_cont)
key = possibleKeys[index]

print(f"Llave parcial recuperada: \n{key}")