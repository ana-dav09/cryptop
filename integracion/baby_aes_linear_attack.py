# baby_aes_linear_attack.py - Versión con traza completa y detallada
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

# Variable global para la traza completa
TRACE = {
    "attack_type": "Linear Cryptanalysis",
    "algorithm": "Baby AES",
    "phases": []
}

def add_phase(phase_name, description, steps):
    """Agrega una fase completa con múltiples pasos"""
    TRACE["phases"].append({
        "phase": phase_name,
        "description": description,
        "steps": steps
    })

# Instancia Baby-AES
aes = mq.SR(ROUNDS, STATE_ARRAY_ROWS, STATE_ARRAY_COLS, EXPONENT,
            allow_zero_inversions=True, star=True)
F = aes.base_ring()
f2 = GF(2)

subBytes = aes.sbox()
invS = SBox(14, 13, 4, 12, 3, 2, 0, 6, 15, 8, 7, 1, 11, 9, 5, 10)

# --- Funciones auxiliares (mantener igual) ---
def readData(namefile):
    with open(namefile, 'r', newline='', encoding='utf-8') as archivo_csv:
        lector_csv = csv.reader(archivo_csv)
        next(lector_csv)
        return list(lector_csv)

def innerProduct(a, b):
    if len(a) != len(b):
        return -1
    sum = 0
    for i in range(len(a)):
        sum += int(a[i])*int(b[i])
    return sum % 2

def innerProductExtended(bitStringA, bitStringB):
    sum = 0
    for nibbleA, nibbleB in zip(bitStringA, bitStringB):
        if nibbleA == "0000":
            continue
        sum += innerProduct(nibbleA, nibbleB)
    return sum % 2

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

def calculateCorrMatrix(agreementMatrix):
    corrMatrix = []
    for a in agreementMatrix:
        row = []
        for b in a:
            row.append(b / 16)
        corrMatrix.append(row)
    return corrMatrix

def calculateProbMatrix(corrMatrix):
    probMatrix = []
    for a in corrMatrix:
        row = []
        for b in a:
            row.append((b + 1) / 2)
        probMatrix.append(row)
    return probMatrix

def bitString2intString(string):
    return [int(str(string[i]),2) for i in range(len(string))]

def intString2bitString(numbers):
    return [f'{numbers[i]:04b}' for i in range(len(numbers))]

def b2F(bin):
    n = int(str(bin),2)
    return F.fetch_int(n)

def h2b(hex):
    n = int(hex, 16)
    return f'{n:04b}'

def bitString2state(string):
    return aes.state_array([b2F(string[i]) for i in range(4)])

def state2bitString(state):
    hexstate = aes.hex_str_vector(state)
    return [h2b(hexstate[i]) for i in range(4)]

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
    """Selecciona la máscara de salida con mayor sesgo"""
    nibbleValues = bitString2intString(inputMask)
    outputMaskValues = []
    selections = []
    
    for idx, row in enumerate(nibbleValues):
        if(row == 0):
            outputMaskValues.append(0)
            selections.append({
                "nibble_position": idx,
                "input_mask": f"0x{row:X}",
                "output_mask": "0x0",
                "reason": "Nibble inactivo (máscara de entrada = 0)"
            })
            continue
        
        temp = 0
        output = 0
        best_prob = 0
        for i, p in enumerate(probMatrix[row]):
            if i == 0:
                continue
            bias = abs(p - 0.5)
            if(bias >= temp):
                output = i
                temp = bias
                best_prob = p
        
        outputMaskValues.append(output)
        selections.append({
            "nibble_position": idx,
            "input_mask": f"0x{row:X}",
            "output_mask": f"0x{output:X}",
            "probability": float(best_prob),
            "bias": float(temp),
            "reason": f"Seleccionada por máximo sesgo ({temp:.4f})"
        })
    
    return intString2bitString(outputMaskValues), selections

def doPermutationBlock(binState):
    stateArray = bitString2state(binState)
    stateArray = aes.shift_rows(stateArray)
    return invMixColumns(stateArray)

def corrRound(a, b, corrMatrix):
    corr = 1.0
    details = []
    for idx, (ai, bi) in enumerate(zip(a, b)):
        aValue = int(str(ai), 2)
        if aValue == 0:
            details.append({
                "nibble": idx,
                "input": f"{ai}",
                "output": f"{bi}",
                "correlation": 1.0,
                "note": "Nibble inactivo"
            })
            continue
        bValue = int(str(bi), 2)
        nibble_corr = corrMatrix[aValue][bValue]
        corr *= nibble_corr
        details.append({
            "nibble": idx,
            "input": f"{ai} (0x{aValue:X})",
            "output": f"{bi} (0x{bValue:X})",
            "correlation": float(nibble_corr)
        })
    return corr, details

def inverseSubBytes(state):
    b = state2bitString(state)
    reverse = [f'{invS(int(str(b[i]), 2)):04b}' for i in range(len(b))]
    return reverse

def hex2bitString(hexString):
    return state2bitString(hex2state(hexString))

def generatePossibleKeys(lastInputMask):
    """Genera todos los candidatos de subclave parcial"""
    maskState = bitString2state(lastInputMask)
    maskAfterShiftRows = state2bitString(aes.shift_rows(maskState))
    keys = []
    inactiveNibbles = []
    activeNibbles = 4
    
    active_positions = []
    for index, nibble in enumerate(maskAfterShiftRows):
        if nibble == "0000":
            inactiveNibbles.append(index)
            activeNibbles -= 1
        else:
            active_positions.append(index)

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
    
    return keys, active_positions, inactiveNibbles

def getLinealAproach(inputMask, probMatrix, corrMatrix):
    """Construye el trail lineal completo con traza detallada"""
    steps = []
    
    a = inputMask
    corr = 1
    
    # Paso inicial
    steps.append({
        "step": "Inicialización",
        "description": "Máscara de entrada seleccionada manualmente para activar nibbles específicos",
        "input_mask": ", ".join(a),
        "active_nibbles": sum(1 for n in a if n != "0000"),
        "note": "Esta máscara determina qué bits del texto plano participan en la aproximación"
    })
    
    for round_num in range(ROUNDS - 1):
        # Seleccionar máscara de salida
        b, mask_selections = getOutputMask(a, probMatrix)
        round_corr, corr_details = corrRound(a, b, corrMatrix)
        corr *= round_corr
        
        # Aplicar permutación (ShiftRows + InvMixColumns)
        a_next = doPermutationBlock(b)
        
        steps.append({
            "round": round_num + 1,
            "description": f"Ronda {round_num + 1}: Propagación a través de SubBytes, ShiftRows y MixColumns",
            "substeps": [
                {
                    "operation": "SubBytes (via LAT)",
                    "input_mask": ", ".join(a),
                    "output_mask": ", ".join(b),
                    "mask_selections": mask_selections,
                    "correlation_details": corr_details,
                    "round_correlation": float(round_corr)
                },
                {
                    "operation": "ShiftRows + InvMixColumns",
                    "input_to_perm": ", ".join(b),
                    "output_after_perm": ", ".join(a_next),
                    "note": "La máscara se propaga linealmente a través de las transformaciones lineales"
                }
            ],
            "accumulated_correlation": float(corr),
            "accumulated_bias": float(abs(corr))
        })
        
        a = a_next
    
    # Máscara final
    steps.append({
        "step": "Máscara Final",
        "description": "Máscara de entrada a la última ronda (después de todas las propagaciones)",
        "final_mask": ", ".join(a),
        "total_correlation": float(corr),
        "total_bias": float(abs(corr)),
        "interpretation": f"Esta máscara tiene un sesgo de {abs(corr):.6f}, "
                         f"lo que significa que la aproximación lineal se cumple con probabilidad {0.5 + abs(corr)/2:.4f}"
    })
    
    add_phase(
        "Fase 2: Construcción del Trail Lineal",
        "Se construye un camino (trail) lineal que conecta bits del texto plano con bits antes de la última ronda. "
        "En cada ronda se selecciona la máscara de salida que maximiza el sesgo estadístico usando la LAT.",
        steps
    )
    
    return (a, corr)

def linear_attack(plaintext_ciphertext_pairs, linear_approximation, corrMatrix):
    """Ejecuta el ataque lineal con traza completa del análisis"""
    
    # FASE 3: Generación de candidatos
    possible_keys, active_positions, inactive_positions = generatePossibleKeys(linear_approximation[1])
    
    phase3_steps = [{
        "step": "Generación de Subclaves Candidatas",
        "description": "Se generan todas las posibles subclaves parciales para los nibbles activos",
        "total_candidates": len(possible_keys),
        "active_nibble_positions": active_positions,
        "inactive_nibble_positions": inactive_positions,
        "search_space": f"2^{4*len(active_positions)} = {2**(4*len(active_positions))} candidatos",
        "note": "Solo se varían los nibbles que la máscara final identifica como relevantes. "
                "Los nibbles inactivos se fijan en 0000."
    }]
    
    add_phase(
        "Fase 3: Generación de Candidatos de Subclave",
        "Se generan todas las posibles subclaves parciales basadas en los nibbles activos de la máscara final.",
        phase3_steps
    )
    
    # FASE 4: Análisis estadístico
    keyCounter = [0 for _ in possible_keys]
    
    # Análisis detallado de los primeros pares
    sample_size = min(10, len(plaintext_ciphertext_pairs))
    detailed_analysis = []
    
    for pair_idx in range(sample_size):
        pair = plaintext_ciphertext_pairs[pair_idx]
        pair_analysis = {
            "pair_index": pair_idx,
            "plaintext": pair[0],
            "ciphertext": pair[1],
            "plaintext_bits": ", ".join(hex2bitString(pair[0])),
            "key_tests": []
        }
        
        # Probar con las primeras 3 llaves candidatas
        for key_idx in range(min(3, len(possible_keys))):
            key = possible_keys[key_idx]
            
            # Desencriptar parcialmente
            y = hex2state(pair[1])
            pk = bitString2state(key)
            w = aes.add_round_key(y, pk)
            v = aes.shift_rows(w)
            u = inverseSubBytes(v)
            
            lhs = innerProductExtended(linear_approximation[0], hex2bitString(pair[0]))
            rhs = innerProductExtended(linear_approximation[1], u)
            match = (lhs == rhs)
            
            pair_analysis["key_tests"].append({
                "key_candidate": ", ".join(key),
                "key_hex": "".join([f"{int(n, 2):X}" for n in key]),
                "state_after_addroundkey": ", ".join(state2bitString(w)),
                "state_after_shiftrows": ", ".join(state2bitString(v)),
                "state_after_inv_sbox": ", ".join(u),
                "lhs_value": lhs,
                "rhs_value": rhs,
                "match": match,
                "counter_delta": "+1" if match else "-1"
            })
        
        detailed_analysis.append(pair_analysis)
    
    phase4_steps = [{
        "step": "Análisis Detallado de Pares (Muestra)",
        "description": f"Para cada par texto-plano/cifrado se verifica la aproximación lineal. "
                      f"Se muestran los primeros {sample_size} pares con 3 candidatos cada uno.",
        "total_pairs": len(plaintext_ciphertext_pairs),
        "pairs_analyzed": detailed_analysis
    }]
    
    # Procesar todos los pares
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
    
    # Estadísticas finales
    max_cont = max(keyCounter, key=abs)
    index = keyCounter.index(max_cont)
    best_key = possible_keys[index]
    
    sorted_idx = sorted(range(len(keyCounter)), key=lambda i: abs(keyCounter[i]), reverse=True)
    top_15 = [
        {
            "rank": rank+1,
            "key_binary": ", ".join(possible_keys[i]),
            "key_hex": "".join([f"{int(n, 2):X}" for n in possible_keys[i]]),
            "score": int(keyCounter[i]),
            "abs_score": abs(keyCounter[i]),
            "estimated_bias": abs(keyCounter[i]) / len(plaintext_ciphertext_pairs),
            "estimated_probability": 0.5 + (abs(keyCounter[i]) / len(plaintext_ciphertext_pairs)) / 2
        }
        for rank, i in enumerate(sorted_idx[:15])
    ]
    
    phase4_steps.append({
        "step": "Resultados Estadísticos",
        "description": "Después de analizar todos los pares, se ordenan los candidatos por score absoluto",
        "best_candidate": {
            "rank": 1,
            "key_binary": ", ".join(best_key),
            "key_hex": "".join([f"{int(n, 2):X}" for n in best_key]),
            "score": int(max_cont),
            "bias": abs(max_cont) / len(plaintext_ciphertext_pairs),
            "probability": 0.5 + (abs(max_cont) / len(plaintext_ciphertext_pairs)) / 2
        },
        "top_candidates": top_15,
        "interpretation": f"El mejor candidato tiene un score de {max_cont}, lo que indica un sesgo estadístico "
                         f"de {abs(max_cont) / len(plaintext_ciphertext_pairs):.6f}. "
                         f"Esto confirma que la aproximación lineal se cumple con mayor frecuencia para esta subclave."
    })
    
    add_phase(
        "Fase 4: Análisis Estadístico de Pares",
        f"Se analizan {len(plaintext_ciphertext_pairs)} pares texto-plano/cifrado. "
        "Para cada par y cada candidato se verifica si la aproximación lineal se cumple. "
        "El candidato correcto mostrará un sesgo estadístico significativo.",
        phase4_steps
    )
    
    return (possible_keys, keyCounter, best_key, index)

# --- Main ---
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--rounds", type=int, default=3)
    parser.add_argument("--pairs", type=int, default=None)
    parser.add_argument("--mask", type=str, default="0010,0000,0000,1000")
    parser.add_argument("--topk", type=int, default=20)
    parser.add_argument("--inputfile", type=str, default="/mnt/c/Users/hp/Desktop/diseno/integracion/plaintext_ciphertext_pairs.csv")
    args = parser.parse_args()

    TRACE["rounds"] = args.rounds
    TRACE["num_pairs"] = args.pairs if args.pairs else "all"
    TRACE["input_mask"] = args.mask

    # FASE 1: Preparación
    phase1_steps = [
        {
            "step": "Cálculo de la S-Box",
            "sbox_values": [int(x) for x in subBytes],
            "sbox_hex": [f"0x{int(x):X}" for x in subBytes],
            "description": "La S-Box es la única componente no-lineal del cifrado"
        },
        {
            "step": "Cálculo de la Tabla de Aproximación Lineal (LAT)",
            "description": "La LAT muestra las correlaciones entre bits de entrada y salida de la S-Box. "
                          "Un valor LAT[a][b] cercano a ±8 indica una aproximación lineal fuerte.",
            "lat_dimension": "16x16",
            "total_entries": 256,
            "note": "Los valores de correlación se calculan como: corr = (agreements - disagreements) / 16"
        }
    ]
    
    add_phase(
        "Fase 1: Preparación y Análisis de la S-Box",
        "Se calcula la Tabla de Aproximación Lineal (LAT) de la S-Box para identificar "
        "aproximaciones lineales con sesgo estadístico explotable.",
        phase1_steps
    )
    
    agreementMatrix = getAgreementMatrix(subBytes)
    corrMatrix = calculateCorrMatrix(agreementMatrix)
    probMatrix = calculateProbMatrix(corrMatrix)

    # Máscaras
    inputMask1 = args.mask.split(",")
    inputMask3, corr = getLinealAproach(inputMask1, probMatrix, corrMatrix)

    # Pares P-C
    plaintext_ciphertext_pairs = readData(args.inputfile)
    if args.pairs:
        plaintext_ciphertext_pairs = plaintext_ciphertext_pairs[:args.pairs]

    linear_approximation = [inputMask1, inputMask3]

    # Ejecución del ataque
    possibleKeys, keyCounter, key, best_index = linear_attack(
        plaintext_ciphertext_pairs,
        linear_approximation,
        corrMatrix
    )
    best_key = possibleKeys[best_index]

    # FASE 5: Conclusión
    phase5_steps = [{
        "step": "Subclave Recuperada",
        "recovered_subkey": {
            "binary": ", ".join(best_key),
            "hex": "".join([f"{int(n, 2):X}" for n in best_key]),
            "nibbles": [f"{int(n, 2):X}" for n in best_key]
        },
        "score": int(max(keyCounter, key=abs)),
        "confidence": abs(max(keyCounter, key=abs)) / len(plaintext_ciphertext_pairs),
        "conclusion": "Esta es la subclave parcial de la última ronda con mayor probabilidad de ser correcta. "
                     "Con esta información se podría continuar el ataque para recuperar el resto de la clave maestra."
    }]
    
    add_phase(
        "Fase 5: Recuperación de la Subclave",
        "El ataque ha identificado exitosamente la subclave parcial de la última ronda.",
        phase5_steps
    )

    # Exportar archivos
    import os
    script_dir = os.path.dirname(os.path.realpath(__file__))

    # CSV de contadores
    csv_counts_path = os.path.join(script_dir, "linear_counts.csv")
    with open(csv_counts_path, "w", newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["index", "counter", "key"])
        for idx, (k, c) in enumerate(zip(possibleKeys, keyCounter)):
            writer.writerow([idx, int(c), " ".join(k)])

    # CSV matriz de correlación
    csv_corr_path = os.path.join(script_dir, "corr_matrix.csv")
    with open(csv_corr_path, "w", newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        for row in corrMatrix:
            writer.writerow([float(x) for x in row])

    # CSV matriz de probabilidad
    csv_prob_path = os.path.join(script_dir, "prob_matrix.csv")
    with open(csv_prob_path, "w", newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        for row in probMatrix:
            writer.writerow([float(x) for x in row])

    # JSON resumen
    top_k = 20
    sorted_idx = sorted(range(len(keyCounter)), key=lambda i: abs(keyCounter[i]), reverse=True)
    top_idx = sorted_idx[:top_k]
    top_candidates = [{"index": i, "counter": int(keyCounter[i]), "key": possibleKeys[i]} for i in top_idx]

    for c in top_candidates:
        c["key"] = ["".join(n) for n in c["key"]]

    result = {
        "a1": inputMask1,
        "a3": inputMask3,
        "correlation": float(abs(corr)),
        "best_key_index": int(best_index),
        "best_key": ["".join(n) for n in best_key],
        "top_count": int(max(keyCounter, key=abs)),
        "top_candidates": top_candidates
    }

    json_path = os.path.join(script_dir, "linear_attack_result.json")
    with open(json_path, "w", encoding='utf-8') as f:
        json.dump(result, f, indent=4)

    # 🔥 Exportar traza completa
    trace_path = os.path.join(script_dir, "linear_attack_trace.json")
    with open(trace_path, "w", encoding='utf-8') as f:
        json.dump(TRACE, f, indent=2)

    print(json.dumps(result))