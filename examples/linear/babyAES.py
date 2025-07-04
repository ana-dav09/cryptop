import csv
from sage.all import *

ROUNDS = 3
STATE_ARRAY_ROWS = 2
STATE_ARRAY_COLS = 2
EXPONENT = 4

aes = mq.SR(ROUNDS, STATE_ARRAY_ROWS, STATE_ARRAY_COLS, EXPONENT, allow_zero_inversions=True, star=True)
F = aes.base_ring()

def h2b(hex):
    n = int(hex, 16)
    return f'{n:04b}'

def b2F(bin):
    n = int(str(bin),2)
    return F.fetch_int(n)

def state2hexString(state):
    hexstate = aes.hex_str_vector(state)
    return hexstate

def state2bitString(state):
    hexstate = aes.hex_str_vector(state)
    return [h2b(hexstate[i]) for i in range(4)]

def bitString2state(string):
    return aes.state_array([b2F(string[i]) for i in range(4)])

def encrypt(x, K):
    Kr = K
    Y = aes.add_round_key(x, Kr)
    for r in range(1, ROUNDS):
        Kr = aes.key_schedule(Kr, r)
        Y = aes.sub_bytes(Y)
        Y = aes.shift_rows(Y)
        Y = aes.mix_columns(Y)
        Y = aes.add_round_key(Y, Kr)
    
    Kr = aes.key_schedule(Kr, r)
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



# Generamos una llave aleatoria
K = aes.random_state_array()
print(f"Key used: {state2bitString(K)}")
print(f"{state2hexString(K)}")
N = 1024

data = [
    ["plaintext", "ciphertext"]
]

Kr = ""

print(f"Generando {N} pares de texto plano/cifrado")

for i in range(N):

    # Para un set de N pares entrada salida aleatoria uniforme
    X = aes.random_state_array()
    Y, Kr = encrypt(X, K)
    pair = [state2hexString(X), state2hexString(Y)]

    # Para todo el set de pares entrada salida
    #X = [f'{((i >> 12) & 15):04b}',f'{((i >> 8) & 15):04b}',f'{((i >> 4) & 15):04b}',f'{(i & 15):04b}']
    #Y, Kr = encrypt(bitString2state(X), K)
    #pair = [state2hexString(bitString2state(X)), state2hexString(Y)]
    
    data.append(pair)

print(f"Ultima llave de ronda: {state2hexString(Kr)}")

saveData(data)