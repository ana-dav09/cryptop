import csv
from sage.all import *

ROUNDS = 3
STATE_ARRAY_ROWS = 2
STATE_ARRAY_COLS = 2
EXPONENT = 4

N = 1024

aes = mq.SR(ROUNDS, STATE_ARRAY_ROWS, STATE_ARRAY_COLS, EXPONENT, allow_zero_inversions=True, star=True)
F = aes.base_ring()

def i2F(n):
    return F.fetch_int(n)

def state2hexString(state):
    return aes.hex_str_vector(state)

def encrypt(x, K):
    Kr = K
    Y = aes.add_round_key(x, Kr)
    for r in range(1, ROUNDS):
        Kr = aes.key_schedule(Kr, r)
        Y = aes.sub_bytes(Y)
        Y = aes.shift_rows(Y)
        Y = aes.mix_columns(Y)
        Y = aes.add_round_key(Y, Kr)
    
    Kr = aes.key_schedule(Kr, ROUNDS)
    Y = aes.sub_bytes(Y)
    Y = aes.shift_rows(Y)
    Y = aes.add_round_key(Y, Kr)

    return (Y, Kr)

def saveData(datos):
    try:
        with open("plaintext_ciphertext_pairs.csv", 'w', newline='', encoding='utf-8') as archivo_csv:
            # Crea un objeto escritor CSV
            escritor_csv = csv.writer(archivo_csv)

            # Escribe la fila de encabezado
            escritor_csv.writerow(datos[0])

            # Escribe las filas de datos
            escritor_csv.writerows(datos[1:])

        print(f'El archivo CSV "plaintext_ciphertext_pairs.csv" se ha generado exitosamente.')

    except Exception as e:
        print(f'Ocurrió un error al escribir el archivo CSV: {e}')

inputS = [i2F(6), i2F(0), i2F(0), i2F(8)]
du1 = aes.state_array(inputS)

K = aes.random_state_array()

data = [
    ["x", "xStar", "y", "yStar"]
]

print(f"Generando {N} pares de texto plano/cifrado...")
Kr = ""

for i in range(N):
    X = aes.random_state_array()
    xStar = X + du1
    Y, Kr = encrypt(X, K)
    yStar, Kr = encrypt(xStar, K)
    pair = [state2hexString(X), state2hexString(xStar), state2hexString(Y), state2hexString(yStar)]
    data.append(pair)


print(f"Ultima llave de ronda: {state2hexString(Kr)}")

saveData(data)