#!/usr/bin/env sage
# present_linear_attack_complete.py
"""
Análisis Lineal Completo para PRESENT
Incluye generación de pares y ejecución del ataque
"""

import json
import csv
import os
from sage.all import *
from sage.crypto.sbox import SBox
from sage.crypto.block_cipher.present import PRESENT
from itertools import product

# Importar random de Python antes de que Sage lo sobrescriba
import random as py_random

# --- Constantes PRESENT ---
BLOCK_SIZE = 64  # bits
SBOX_SIZE = 4    # bits (nibbles)
NUM_SBOXES = 16  # 64/4
ROUNDS = 31      # por defecto en PRESENT

# S-box de PRESENT (hexadecimal)
PRESENT_SBOX = SBox([0xC, 0x5, 0x6, 0xB, 0x9, 0x0, 0xA, 0xD, 
                     0x3, 0xE, 0xF, 0x8, 0x4, 0x7, 0x1, 0x2])

# S-box inversa
PRESENT_INV_SBOX = PRESENT_SBOX.inverse()

# Campo base
F2 = GF(2)

# --- Permutación pLayer ---
P_LAYER = [
    0, 16, 32, 48, 1, 17, 33, 49, 2, 18, 34, 50, 3, 19, 35, 51,
    4, 20, 36, 52, 5, 21, 37, 53, 6, 22, 38, 54, 7, 23, 39, 55,
    8, 24, 40, 56, 9, 25, 41, 57, 10, 26, 42, 58, 11, 27, 43, 59,
    12, 28, 44, 60, 13, 29, 45, 61, 14, 30, 46, 62, 15, 31, 47, 63
]

INV_P_LAYER = [0] * 64
for i, p in enumerate(P_LAYER):
    INV_P_LAYER[p] = i


# ============================================================================
# SECCIÓN 1: FUNCIONES AUXILIARES
# ============================================================================

def int2bits(n, length=64):
    """Convierte entero a lista de bits (LSB primero)."""
    return [int(b) for b in bin(n)[2:].zfill(length)][::-1]

def bits2int(bits):
    """Convierte lista de bits a entero (LSB primero)."""
    return int(''.join(str(b) for b in bits[::-1]), 2)

def hex2bits(hex_str, length=64):
    """Convierte cadena hexadecimal a bits."""
    n = int(hex_str, 16) if isinstance(hex_str, str) else hex_str
    return int2bits(n, length)

def bits2hex(bits):
    """Convierte bits a hexadecimal."""
    return hex(bits2int(bits))

def inner_product(a, b):
    """Producto interno módulo 2 de dos vectores de bits."""
    return sum(ai * bi for ai, bi in zip(a, b)) % 2

def apply_sbox(nibble_value, inverse=False):
    """Aplica S-box (o inversa) a un valor de 4 bits."""
    sbox = PRESENT_INV_SBOX if inverse else PRESENT_SBOX
    return sbox(nibble_value)

def apply_pLayer(state_bits, inverse=False):
    """Aplica permutación pLayer a un estado de 64 bits."""
    perm = INV_P_LAYER if inverse else P_LAYER
    return [state_bits[perm[i]] for i in range(64)]


# ============================================================================
# SECCIÓN 2: GENERACIÓN DE PARES
# ============================================================================

def generate_random_pairs(num_pairs, key, key_size=80):
    """Genera pares plaintext-ciphertext aleatorios."""
    print(f"Generando {num_pairs} pares aleatorios con clave {key_size}-bit...")
    
    present = PRESENT(keySchedule=key_size, doFinalRound=True)
    
    pairs = []
    for i in range(num_pairs):
        plaintext = py_random.randint(0, 2**64 - 1)
        ciphertext = present.encrypt(plaintext, key)
        
        pt_hex = f"{plaintext:016x}"
        ct_hex = f"{ciphertext:016x}"
        
        pairs.append((pt_hex, ct_hex))
        
        if (i + 1) % 10000 == 0:
            print(f"  Generados {i + 1}/{num_pairs} pares...")
    
    print(f"✓ {len(pairs)} pares generados")
    return pairs


def generate_sequential_pairs(num_pairs, key, key_size=80):
    """Genera pares con plaintexts secuenciales."""
    print(f"Generando {num_pairs} pares secuenciales...")
    
    present = PRESENT(keySchedule=key_size, doFinalRound=True)
    
    pairs = []
    for i in range(num_pairs):
        plaintext = i
        ciphertext = present.encrypt(plaintext, key)
        
        pt_hex = f"{plaintext:016x}"
        ct_hex = f"{ciphertext:016x}"
        
        pairs.append((pt_hex, ct_hex))
        
        if (i + 1) % 10000 == 0:
            print(f"  Generados {i + 1}/{num_pairs} pares...")
    
    print(f"✓ {len(pairs)} pares generados")
    return pairs


def generate_low_hamming_pairs(num_pairs, key, max_weight=4, key_size=80):
    """Genera pares con plaintexts de bajo peso de Hamming."""
    print(f"Generando {num_pairs} pares con HW(PT) ≤ {max_weight}...")
    
    present = PRESENT(keySchedule=key_size, doFinalRound=True)
    
    pairs = []
    attempts = 0
    max_attempts = num_pairs * 100
    
    while len(pairs) < num_pairs and attempts < max_attempts:
        plaintext = py_random.randint(0, 2**64 - 1)
        
        hw = bin(plaintext).count('1')
        if hw <= max_weight:
            ciphertext = present.encrypt(plaintext, key)
            
            pt_hex = f"{plaintext:016x}"
            ct_hex = f"{ciphertext:016x}"
            
            pairs.append((pt_hex, ct_hex))
            
            if len(pairs) % 1000 == 0:
                print(f"  Generados {len(pairs)}/{num_pairs} pares...")
        
        attempts += 1
    
    if len(pairs) < num_pairs:
        print(f"⚠ Solo se generaron {len(pairs)} pares después de {attempts} intentos")
    
    print(f"✓ {len(pairs)} pares generados")
    return pairs


def save_pairs_to_csv(pairs, filename):
    """Guarda pares en archivo CSV."""
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['plaintext', 'ciphertext'])
        writer.writerows(pairs)
    print(f"✓ Pares guardados en {filename}")


def load_pairs_from_csv(filename, max_pairs=None):
    """Carga pares desde archivo CSV."""
    pairs = []
    with open(filename, 'r') as f:
        reader = csv.reader(f)
        next(reader)  # Skip header
        for row in reader:
            pairs.append((row[0], row[1]))
            if max_pairs and len(pairs) >= max_pairs:
                break
    print(f"✓ {len(pairs)} pares cargados desde {filename}")
    return pairs


# ============================================================================
# SECCIÓN 3: ANÁLISIS LINEAL
# ============================================================================

def compute_lat(sbox, size=4):
    """Calcula la Linear Approximation Table (LAT) para la S-box."""
    n = 2 ** size
    lat = [[0 for _ in range(n)] for _ in range(n)]
    
    for a in range(n):
        for b in range(n):
            count = 0
            a_bits = int2bits(a, size)
            for x in range(n):
                x_bits = int2bits(x, size)
                sx = sbox(x)
                sx_bits = int2bits(sx, size)
                b_bits = int2bits(b, size)
                
                if inner_product(a_bits, x_bits) == inner_product(b_bits, sx_bits):
                    count += 1
            
            lat[a][b] = count - (n // 2)
    
    return lat


def lat_to_correlation(lat):
    """Convierte LAT a matriz de correlación."""
    n = len(lat)
    size = int(log(n, 2))
    corr = [[lat[a][b] / (2 ** size) for b in range(n)] for a in range(n)]
    return corr


def lat_to_probability(corr_matrix):
    """Convierte correlación a probabilidad."""
    prob = [[(c + 1) / 2 for c in row] for row in corr_matrix]
    return prob


def find_best_output_mask(input_mask_nibble, corr_matrix):
    """Encuentra la mejor máscara de salida para un nibble dado."""
    if input_mask_nibble == 0:
        return 0
    
    best_output = 0
    best_corr = 0
    
    for b in range(1, len(corr_matrix[0])):
        corr = abs(corr_matrix[input_mask_nibble][b])
        if corr > best_corr:
            best_corr = corr
            best_output = b
    
    return best_output


def propagate_mask_through_round(input_mask, corr_matrix):
    """Propaga una máscara a través de una ronda (S-box + pLayer)."""
    # Dividir máscara en nibbles
    nibbles_in = [bits2int(input_mask[i*4:(i+1)*4]) for i in range(16)]
    
    # Pasar por S-boxes
    nibbles_out = []
    total_corr = 1.0
    
    for nib_in in nibbles_in:
        nib_out = find_best_output_mask(nib_in, corr_matrix)
        nibbles_out.append(nib_out)
        
        if nib_in != 0:
            total_corr *= corr_matrix[nib_in][nib_out]
    
    # Reconstruir máscara de 64 bits
    mask_after_sbox = []
    for nib in nibbles_out:
        mask_after_sbox.extend(int2bits(nib, 4))
    
    # Aplicar pLayer
    mask_after_pLayer = apply_pLayer(mask_after_sbox, inverse=False)
    
    return mask_after_pLayer, total_corr


def build_linear_trail(input_mask, num_rounds, corr_matrix):
    """Construye un trail lineal para num_rounds rondas."""
    current_mask = input_mask[:]
    total_corr = 1.0
    trail = [current_mask[:]]
    
    for r in range(num_rounds):
        current_mask, corr = propagate_mask_through_round(current_mask, corr_matrix)
        total_corr *= corr
        trail.append(current_mask[:])
    
    return trail[-1], total_corr, trail


def generate_partial_key_candidates(active_sboxes):
    """Genera candidatos de clave parcial para las S-boxes activas."""
    num_active = len(active_sboxes)
    candidates = []
    
    for values in product(range(16), repeat=num_active):
        key_nibbles = [0] * 16
        for idx, sbox_idx in enumerate(active_sboxes):
            key_nibbles[sbox_idx] = values[idx]
        candidates.append(key_nibbles)
    
    return candidates


def partial_decrypt_last_round(ciphertext_bits, partial_key_nibbles):
    """Desencripta parcialmente la última ronda."""
    # AddRoundKey
    key_bits = []
    for nib in partial_key_nibbles:
        key_bits.extend(int2bits(nib, 4))
    
    state = [(c ^ k) for c, k in zip(ciphertext_bits, key_bits)]
    
    # InvPLayer
    state = apply_pLayer(state, inverse=True)
    
    # InvSbox (solo donde la clave es no-cero)
    result_nibbles = []
    for i in range(16):
        nibble_bits = state[i*4:(i+1)*4]
        nibble_val = bits2int(nibble_bits)
        
        if partial_key_nibbles[i] != 0:
            nibble_val = apply_sbox(nibble_val, inverse=True)
        
        result_nibbles.extend(int2bits(nibble_val, 4))
    
    return result_nibbles


def linear_attack(pairs, input_mask, output_mask, num_attack_rounds=2):
    """Ejecuta el ataque lineal en PRESENT."""
    # Identificar S-boxes activas
    active_sboxes = []
    for i in range(16):
        nibble_mask = bits2int(output_mask[i*4:(i+1)*4])
        if nibble_mask != 0:
            active_sboxes.append(i)
    
    print(f"S-boxes activas: {active_sboxes}")
    
    # Generar candidatos
    candidates = generate_partial_key_candidates(active_sboxes)
    print(f"Candidatos de clave: {len(candidates)}")
    
    # Contadores
    counters = [0] * len(candidates)
    
    # Procesar pares
    for idx, (pt_hex, ct_hex) in enumerate(pairs):
        pt_bits = hex2bits(pt_hex, 64)
        ct_bits = hex2bits(ct_hex, 64)
        
        pt_inner = inner_product(input_mask, pt_bits)
        
        for i, key_nibbles in enumerate(candidates):
            partial_state = partial_decrypt_last_round(ct_bits, key_nibbles)
            ct_inner = inner_product(output_mask, partial_state)
            
            if pt_inner == ct_inner:
                counters[i] += 1
            else:
                counters[i] -= 1
        
        if (idx + 1) % 10000 == 0:
            print(f"  Procesados {idx + 1}/{len(pairs)} pares...")
    
    # Encontrar mejor candidato
    best_idx = max(range(len(counters)), key=lambda i: abs(counters[i]))
    best_key = candidates[best_idx]
    best_count = counters[best_idx]
    
    return {
        'candidates': candidates,
        'counters': counters,
        'best_key': best_key,
        'best_index': best_idx,
        'best_count': best_count,
        'active_sboxes': active_sboxes
    }


# ============================================================================
# SECCIÓN 4: EXPORTACIÓN DE RESULTADOS
# ============================================================================

def export_results(result_data, corr_matrix, prob_matrix, output_dir='.'):
    """Exporta todos los resultados a archivos."""
    
    # 1. JSON principal
    json_path = os.path.join(output_dir, 'linear_attack_result.json')
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(result_data, f, indent=4)
    print(f"✓ Resultado guardado en {json_path}")
    
    # 2. CSV de contadores
    csv_counts_path = os.path.join(output_dir, 'linear_counts.csv')
    with open(csv_counts_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['index', 'counter', 'key'])
        for idx, (k, c) in enumerate(zip(result_data['all_candidates'][:100], 
                                         result_data['all_counters'][:100])):
            key_str = ''.join(f'{n:x}' for n in k)
            writer.writerow([idx, int(c), key_str])
    print(f"✓ Contadores guardados en {csv_counts_path}")
    
    # 3. CSV de matriz de correlación
    csv_corr_path = os.path.join(output_dir, 'corr_matrix.csv')
    with open(csv_corr_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        for row in corr_matrix:
            writer.writerow([float(x) for x in row])
    print(f"✓ Matriz de correlación guardada en {csv_corr_path}")
    
    # 4. CSV de matriz de probabilidad
    csv_prob_path = os.path.join(output_dir, 'prob_matrix.csv')
    with open(csv_prob_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        for row in prob_matrix:
            writer.writerow([float(x) for x in row])
    print(f"✓ Matriz de probabilidad guardada en {csv_prob_path}")


# ============================================================================
# SECCIÓN 5: FUNCIÓN PRINCIPAL
# ============================================================================

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Análisis Lineal Completo de PRESENT')
    
    # Opciones de generación de pares
    gen_group = parser.add_argument_group('Generación de Pares')
    gen_group.add_argument('--generate', action='store_true',
                          help='Generar nuevos pares PT-CT')
    gen_group.add_argument('--gen-mode', type=str, default='random',
                          choices=['random', 'sequential', 'low-hamming'],
                          help='Modo de generación')
    gen_group.add_argument('--num-pairs', type=int, default=50000,
                          help='Número de pares a generar')
    gen_group.add_argument('--max-weight', type=int, default=4,
                          help='Peso de Hamming máximo (low-hamming)')
    
    # Opciones de ataque
    attack_group = parser.add_argument_group('Ataque Lineal')
    attack_group.add_argument('--input', type=str, default=None,
                             help='Archivo CSV con pares existentes')
    attack_group.add_argument('--rounds', type=int, default=2,
                             help='Número de rondas para el trail lineal')
    attack_group.add_argument('--input-mask', type=str, default='0x0001000000000000',
                             help='Máscara de entrada en hexadecimal')
    attack_group.add_argument('--use-pairs', type=int, default=None,
                             help='Limitar número de pares a usar en el ataque')
    
    # Opciones generales
    parser.add_argument('--key', type=str, default='0x0',
                       help='Clave maestra en hexadecimal')
    parser.add_argument('--key-size', type=int, default=80, choices=[80, 128],
                       help='Tamaño de clave (80 o 128 bits)')
    parser.add_argument('--output-dir', type=str, default='.',
                       help='Directorio para archivos de salida')
    parser.add_argument('--save-pairs', type=str, default=None,
                       help='Guardar pares generados en este archivo')
    
    args = parser.parse_args()
    
    # Convertir clave
    key = int(args.key, 16)
    
    print("=" * 70)
    print("ANÁLISIS LINEAL COMPLETO DE PRESENT")
    print("=" * 70)
    print(f"Clave: {key:016x} ({args.key_size}-bit)")
    print(f"Rondas atacadas: {args.rounds}")
    print("=" * 70)
    
    # PASO 1: Obtener pares
    if args.generate:
        print("\n[PASO 1] Generando pares plaintext-ciphertext...")
        
        if args.gen_mode == 'random':
            pairs = generate_random_pairs(args.num_pairs, key, args.key_size)
        elif args.gen_mode == 'sequential':
            pairs = generate_sequential_pairs(args.num_pairs, key, args.key_size)
        elif args.gen_mode == 'low-hamming':
            pairs = generate_low_hamming_pairs(args.num_pairs, key, args.max_weight, args.key_size)
        
        # Guardar si se especificó
        if args.save_pairs:
            save_pairs_to_csv(pairs, args.save_pairs)
    
    elif args.input:
        print("\n[PASO 1] Cargando pares desde archivo...")
        pairs = load_pairs_from_csv(args.input, args.use_pairs)
    
    else:
        print("Error: Debe especificar --generate o --input")
        return
    
    # Limitar pares si se especificó
    if args.use_pairs and len(pairs) > args.use_pairs:
        pairs = pairs[:args.use_pairs]
        print(f"Usando {args.use_pairs} pares para el ataque")
    
    # PASO 2: Calcular LAT y matrices
    print("\n[PASO 2] Calculando LAT y matrices de correlación...")
    lat = compute_lat(PRESENT_SBOX, SBOX_SIZE)
    corr_matrix = lat_to_correlation(lat)
    prob_matrix = lat_to_probability(corr_matrix)
    print("✓ Matrices calculadas")
    
    # PASO 3: Construir trail lineal
    print("\n[PASO 3] Construyendo trail lineal...")
    input_mask_int = int(args.input_mask, 16)
    input_mask = int2bits(input_mask_int, 64)
    
    output_mask, correlation, trail = build_linear_trail(
        input_mask, args.rounds, corr_matrix
    )
    
    print(f"✓ Trail construido")
    print(f"  Correlación: {correlation:.6f}")
    print(f"  Bias: {abs(correlation):.6f}")
    print(f"  Pares teóricos necesarios: ~{int(1/(correlation**2))}")
    
    # PASO 4: Ejecutar ataque
    print("\n[PASO 4] Ejecutando ataque lineal...")
    result = linear_attack(pairs, input_mask, output_mask, args.rounds)
    
    print(f"\n✓ Ataque completado")
    print(f"  Mejor clave encontrada: {''.join(f'{n:x}' for n in result['best_key'])}")
    print(f"  Contador: {result['best_count']}")
    print(f"  Bias observado: {abs(result['best_count'])/len(pairs):.6f}")
    
    # PASO 5: Exportar resultados
    print("\n[PASO 5] Exportando resultados...")
    
    # Top 20 candidatos
    sorted_indices = sorted(range(len(result['counters'])), 
                           key=lambda i: abs(result['counters'][i]), 
                           reverse=True)
    top_candidates = []
    for i in sorted_indices[:20]:
        top_candidates.append({
            'index': int(i),
            'counter': int(result['counters'][i]),
            'key': ''.join(f'{n:x}' for n in result['candidates'][i]),
            'bias': abs(result['counters'][i]) / len(pairs)
        })
    
    result_data = {
        'input_mask': args.input_mask,
        'output_mask': '0x' + ''.join(f'{bits2int(output_mask[i*4:(i+1)*4]):x}' 
                                       for i in range(16)),
        'correlation': float(correlation),
        'bias': float(abs(correlation)),
        'rounds_attacked': args.rounds,
        'pairs_used': len(pairs),
        'best_key': ''.join(f'{n:x}' for n in result['best_key']),
        'best_count': int(result['best_count']),
        'active_sboxes': result['active_sboxes'],
        'top_candidates': top_candidates,
        'all_candidates': result['candidates'],
        'all_counters': result['counters']
    }
    
    export_results(result_data, corr_matrix, prob_matrix, args.output_dir)
    
    print("\n" + "=" * 70)
    print("✓ ANÁLISIS COMPLETADO")
    print("=" * 70)


if __name__ == '__main__':
    main()