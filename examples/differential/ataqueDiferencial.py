from sage.all import *
from itertools import *

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

def F2i(element):
    return eval(str(element).replace('a', '2').replace('^', "**"))

def i2F(n):
    return F.fetch_int(n)

def getPairsWithDifference(dx):
    pairs = []
    for x, xStar in product(F, repeat=2):
        if x + xStar is dx:
            pairs.append((x, xStar))
    
    return pairs

def getAbsoluteFrequency(dx):
    freq = [0 for _ in F]
    pairs = getPairsWithDifference(dx)
    for x, xStar in pairs:
        dy = S(x) + S(xStar)
        freq[F2i(dy)] += 1

    return freq
    
def getFrequencyMatrix():
    array = []
    for dx in range(F.order()):
        row = getAbsoluteFrequency(i2F(dx))
        array.append(row)
    
    return matrix(QQ, 16,16, array)

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

def doPermutationBlock(stateArray):
    res = aes.shift_rows(stateArray)
    return aes.mix_columns(res)


def getDifferentialTrail(stateArray, freqMatrix):
    propagationRatio = 1
    du = stateArray
    for i in range(1, ROUNDS):
        dv, freq = getDifferential(du, freqMatrix)
        # algo

        propagationRatio *= freq
        du = doPermutationBlock(dv)
    
    return (du, propagationRatio)

# Ejemplo
inputS = [i2F(6), i2F(0), i2F(0), i2F(8)]
state = aes.state_array(inputS)
freqMatrix = getFrequencyMatrix()

print(state)
out, ratio = getDifferentialTrail(state, freqMatrix)

print(out)
print(ratio)
