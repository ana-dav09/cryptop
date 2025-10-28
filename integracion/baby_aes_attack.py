# baby_aes_attack.py (OPTIMIZADO - versión rápida)
import json, os, csv, sys
import argparse
from sage.all import *
from sage.crypto.sbox import SBox
from itertools import product

# --- Constantes ---
ROUNDS = 3
STATE_ARRAY_ROWS = 2
STATE_ARRAY_COLS = 2
EXPONENT = 4

# Variable global para la traza completa
TRACE = {
    "attack_type": "Differential Cryptanalysis",
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

# --- Instancia Baby-AES ---
print("⏳ Inicializando Baby AES...", flush=True)
aes = mq.SR(ROUNDS, STATE_ARRAY_ROWS, STATE_ARRAY_COLS, EXPONENT,
            allow_zero_inversions=True, star=True)
F = aes.base_ring()
S = aes.sbox()
invS = SBox(14, 13, 4, 12, 3, 2, 0, 6, 15, 8, 7, 1, 11, 9, 5, 10)

# --- Funciones auxiliares ---
def i2F(n): 
    return F.fetch_int(n)

def F2i(element): 
    return eval(str(element).replace('a', '2').replace('^', "**"))

def elem_to_int(e):
    try:
        return int(e.integer_representation())
    except Exception:
        try:
            return int(e)
        except Exception:
            try:
                return F2i(e)
            except Exception:
                raise ValueError(f"Imposible convertir el elemento a entero: {e}")

def elem_to_hex(e):
    return f"{elem_to_int(e):X}"

def state_to_hex(state):
    return "".join([elem_to_hex(e) for e in state.list()])

def key_matrix_to_binary_str(key_matrix):
    ints = [elem_to_int(el) for el in key_matrix.list()]
    nibbles = [format(x, '04b') for x in ints]
    compact = ''.join(nibbles)
    spaced = ' '.join(nibbles)
    return compact, spaced

def hexStrings2states(a, b, c, d):
    aState = aes.state_array([i2F(int(i, 16)) for i in list(a)])
    bState = aes.state_array([i2F(int(i, 16)) for i in list(b)])
    cState = aes.state_array([i2F(int(i, 16)) for i in list(c)])
    dState = aes.state_array([i2F(int(i, 16)) for i in list(d)])
    return (aState, bState, cState, dState)

def readData(namefile, max_pairs=None):
    """Lee pares del CSV, limitando opcionalmente la cantidad"""
    with open(namefile, 'r', newline='', encoding='utf-8') as archivo_csv:
        lector_csv = csv.reader(archivo_csv)
        next(lector_csv)  # saltamos header
        pairs = list(lector_csv)
        
        if max_pairs and len(pairs) > max_pairs:
            print(f"⚠️ Limitando análisis a {max_pairs} de {len(pairs)} pares disponibles", flush=True)
            return pairs[:max_pairs]
        
        return pairs

# --- Matriz de frecuencias (DDT) ---
def getPairsWithDifference(dx):
    return [(x, xStar) for x, xStar in product(F, repeat=2) if x + xStar is dx]

def getAbsoluteFrequency(dx):
    freq = [0 for _ in F]
    for x, xStar in getPairsWithDifference(dx):
        dy = S(x) + S(xStar)
        freq[F2i(dy)] += 1
    return freq

def getFrequencyMatrix():
    """Calcula la DDT completa (versión simplificada para velocidad)"""
    print("⏳ Calculando DDT (Difference Distribution Table)...", flush=True)
    
    matrix_data = []
    high_prob_diffs = []
    
    for dx_int in range(F.order()):
        dx = i2F(dx_int)
        freq_row = getAbsoluteFrequency(dx)
        matrix_data.append(freq_row)
        
        # Identificar solo los top diferenciales
        for dy_int, freq in enumerate(freq_row):
            if freq > 4 and dx_int != 0:
                high_prob_diffs.append({
                    "delta_input": f"0x{dx_int:X}",
                    "delta_output": f"0x{dy_int:X}",
                    "frequency": int(freq),
                    "probability": float(freq) / 16
                })
    
    # Traza simplificada
    phase1_steps = [{
        "step": "DDT calculada",
        "high_probability_differentials": high_prob_diffs[:10],
        "note": "DDT de 16x16 calculada exitosamente"
    }]
    
    add_phase(
        "Fase 1: Construcción de la DDT",
        "Tabla de distribución de diferencias calculada",
        phase1_steps
    )
    
    print("✅ DDT calculada", flush=True)
    return matrix(QQ, 16, 16, matrix_data)

# --- Diferenciales ---
def getDifferential(inputArray, freqMatrix):
    differential = []
    freqAcum = 1
    selections = []
    
    for idx, element in enumerate(inputArray.list()):
        if not element.is_unit():
            differential.append(element)
            selections.append({
                "nibble_position": idx,
                "delta_input": "0x0",
                "delta_output": "0x0",
                "frequency": 16,
                "probability": 1.0
            })
            continue
        
        diff, temp = 0, 0
        element_int = F2i(element)
        
        for i, freq in enumerate(freqMatrix[element_int]):
            if freq > temp:
                diff, temp = i, freq
        
        freqAcum *= temp / 16
        differential.append(i2F(diff))
        
        selections.append({
            "nibble_position": idx,
            "delta_input": f"0x{element_int:X}",
            "delta_output": f"0x{diff:X}",
            "frequency": int(temp),
            "probability": float(temp) / 16
        })
    
    return (matrix(F, 2, 2, differential), freqAcum, selections)

def doPermutationBlock(stateArray):
    return aes.mix_columns(aes.shift_rows(stateArray))

def getDifferentialTrail(stateArray, freqMatrix):
    """Construye el trail diferencial (versión simplificada)"""
    print("⏳ Construyendo trail diferencial...", flush=True)
    
    steps = []
    propagationRatio = 1
    du = stateArray
    
    for round_num in range(1, ROUNDS):
        dv, freq, selections = getDifferential(du, freqMatrix)
        propagationRatio *= freq
        du = doPermutationBlock(dv)
        
        steps.append({
            "round": round_num,
            "input_diff": state_to_hex(du),
            "probability": float(freq),
            "accumulated": float(propagationRatio)
        })
    
    steps.append({
        "final_difference": state_to_hex(du),
        "total_probability": float(propagationRatio)
    })
    
    add_phase(
        "Fase 2: Trail Diferencial",
        f"Trail de {ROUNDS-1} rondas construido",
        steps
    )
    
    print(f"✅ Trail calculado con probabilidad {float(propagationRatio):.8f}", flush=True)
    return (du, propagationRatio)

# --- Ataque diferencial OPTIMIZADO ---
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
        key = []
        aux = 0
        for i in range(STATE_ARRAY_ROWS * STATE_ARRAY_COLS):
            if i in activeIndex:
                key.append(partialKey[aux])
                aux += 1
            else:
                key.append(i2F(0))
        keys.append(matrix(F, 2, 2, key))
    
    return keys, activeIndex

def differential_attack(io_pairs, differentials):
    """Ataque diferencial OPTIMIZADO"""
    du1, du3 = differentials
    
    print("⏳ Generando candidatos de subclave...", flush=True)
    candidateKeys, active_positions = getPossibleKeys(du3)
    
    phase3_steps = [{
        "total_candidates": len(candidateKeys),
        "active_positions": active_positions
    }]
    
    add_phase(
        "Fase 3: Candidatos Generados",
        f"{len(candidateKeys)} candidatos de subclave",
        phase3_steps
    )
    
    print(f"✅ {len(candidateKeys)} candidatos generados", flush=True)
    
    # Análisis de pares
    print(f"⏳ Analizando {len(io_pairs)} pares...", flush=True)
    
    keyCounter = [0 for _ in candidateKeys]
    valid_pairs_count = 0
    discarded_pairs_count = 0
    
    # Mostrar progreso cada 10%
    checkpoint = max(1, len(io_pairs) // 10)
    
    for pair_idx, (xh, xStarh, yh, yStarh) in enumerate(io_pairs):
        if pair_idx % checkpoint == 0:
            progress = (pair_idx / len(io_pairs)) * 100
            print(f"   Progreso: {progress:.0f}% ({pair_idx}/{len(io_pairs)} pares)", flush=True)
        
        x, xStar, y, yStar = hexStrings2states(xh, xStarh, yh, yStarh)
        
        # Verificar diferencia de entrada
        delta_input = x + xStar
        if state_to_hex(delta_input) != state_to_hex(du1):
            continue
        
        # Verificar nibbles inactivos
        if not inactivesEqual(y, yStar, du3):
            discarded_pairs_count += 1
            continue
        
        valid_pairs_count += 1
        
        # Probar todos los candidatos
        for i, key in enumerate(candidateKeys):
            w = y + key
            wStar = yStar + key
            u = inverseSubBytes(aes.shift_rows(w))
            uStar = inverseSubBytes(aes.shift_rows(wStar))
            
            if u + uStar == du3:
                keyCounter[i] += 1
    
    print(f"✅ Análisis completo: {valid_pairs_count} válidos, {discarded_pairs_count} descartados", flush=True)
    
    # Resultados
    max_count = max(keyCounter)
    best_idx = keyCounter.index(max_count)
    best_key = candidateKeys[best_idx]
    
    phase4_steps = [{
        "valid_pairs": valid_pairs_count,
        "discarded_pairs": discarded_pairs_count,
        "best_key_count": int(max_count)
    }]
    
    add_phase(
        "Fase 4: Análisis Estadístico",
        f"Mejor candidato aparece {max_count} veces",
        phase4_steps
    )
    
    return (candidateKeys, keyCounter)

# --- PARSEO DE ARGUMENTOS ---
def parse_arguments():
    parser = argparse.ArgumentParser(description="Ataque diferencial en Baby AES")
    parser.add_argument("--rounds", type=int, default=3, help="Número de rondas")
    parser.add_argument("--du1", type=str, default="6008", 
                       help="Diferencia de entrada (hex: 6008 o binario: 0110,0000,0000,1000)")
    parser.add_argument("--pairs", type=int, default=5000, help="Número máximo de pares a usar")
    return parser.parse_args()

def parse_du1_input(du1_str):
    """Convierte string a lista de elementos de F"""
    clean = du1_str.replace(",", "").replace(" ", "").strip()
    
    # Formato hexadecimal directo (ej: "6008")
    if len(clean) == 4 and all(c in '0123456789ABCDEFabcdef' for c in clean):
        return [i2F(int(c, 16)) for c in clean]
    
    # Formato binario (16 bits)
    if len(clean) == 16 and all(c in '01' for c in clean):
        nibbles = [clean[i:i+4] for i in range(0, 16, 4)]
        return [i2F(int(n, 2)) for n in nibbles]
    
    # Nibbles binarios separados
    if ',' in du1_str:
        parts = [p.strip() for p in du1_str.split(',')]
        if len(parts) == 4:
            return [i2F(int(p, 2)) for p in parts]
    
    print(f"⚠️ Formato no reconocido: '{du1_str}', usando 6008 por defecto", flush=True)
    return [i2F(6), i2F(0), i2F(0), i2F(8)]

# --- EJECUCIÓN PRINCIPAL ---
if __name__ == "__main__":
    print("=" * 60, flush=True)
    print("🔐 ATAQUE DIFERENCIAL EN BABY AES", flush=True)
    print("=" * 60, flush=True)
    
    args = parse_arguments()
    ROUNDS = args.rounds
    
    # Parsear diferencia de entrada
    inputS = parse_du1_input(args.du1)
    du1 = aes.state_array(inputS)
    
    print(f"🔹 Diferencia de entrada (Δu₁): {state_to_hex(du1)}", flush=True)
    print(f"🔹 Rondas: {ROUNDS}", flush=True)
    print(f"🔹 Pares máximos: {args.pairs}", flush=True)
    print("", flush=True)
    
    TRACE["rounds"] = ROUNDS
    TRACE["input_difference"] = state_to_hex(du1)
    
    # Calcular DDT y trail
    freqMatrix = getFrequencyMatrix()
    du3, ratio = getDifferentialTrail(du1, freqMatrix)
    
    # Leer pares (limitados)
    script_dir = os.path.dirname(os.path.realpath(__file__))
    csv_path = os.path.join(script_dir, "plaintext_ciphertext_pairs.csv")
    
    print(f"⏳ Leyendo pares desde {os.path.basename(csv_path)}...", flush=True)
    input_output_pairs = readData(csv_path, max_pairs=args.pairs)
    print(f"✅ {len(input_output_pairs)} pares cargados", flush=True)
    print("", flush=True)
    
    # Ejecutar ataque
    keys, counts = differential_attack(input_output_pairs, [du1, du3])
    best_key = keys[counts.index(max(counts))]
    
    print("", flush=True)
    print("=" * 60, flush=True)
    print("✅ ATAQUE COMPLETADO", flush=True)
    print("=" * 60, flush=True)
    
    # Exportar DDT
    ddt_path = os.path.join(script_dir, "ddt_matrix.csv")
    with open(ddt_path, "w", newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        for row in freqMatrix:
            writer.writerow([int(x) for x in row])
    
    # Top candidatos
    sorted_idx = sorted(range(len(counts)), key=lambda i: counts[i], reverse=True)
    top_k = 20
    top_candidates = []
    
    for i in sorted_idx[:top_k]:
        compact, spaced = key_matrix_to_binary_str(keys[i])
        top_candidates.append({
            "index": int(i),
            "counter": int(counts[i]),
            "key": state_to_hex(keys[i]),
            "key_binary_compact": compact,
            "key_binary_spaced": spaced
        })
    
    best_compact, best_spaced = key_matrix_to_binary_str(best_key)
    
    # JSON resultado
    result = {
        "du1": state_to_hex(du1),
        "du3": state_to_hex(du3),
        "ratio": str(ratio),
        "best_key": state_to_hex(best_key),
        "best_key_binary_compact": best_compact,
        "best_key_binary_spaced": best_spaced,
        "top_count": int(max(counts)),
        "top_candidates": top_candidates
    }
    
    json_path = os.path.join(script_dir, "differential_attack_result.json")
    with open(json_path, "w", encoding='utf-8') as f:
        json.dump(result, f, indent=4)
    
    # Traza
    trace_path = os.path.join(script_dir, "differential_attack_trace.json")
    with open(trace_path, "w", encoding='utf-8') as f:
        json.dump(TRACE, f, indent=2)
    
    print(f"📊 Mejor subclave: {state_to_hex(best_key)} ({best_spaced})", flush=True)
    print(f"📊 Apariciones: {max(counts)}/{len(input_output_pairs)}", flush=True)
    print(f"💾 Resultados guardados en: {os.path.basename(json_path)}", flush=True)
    
    print(json.dumps(result))