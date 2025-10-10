# sdes_lineal.py
# Versión corregida e integrada del ataque lineal reforzado sobre S-DES usando Sage.
# Ejecutar con: sage -python sdes_lineal.py

import os
import csv
import json
import random
from collections import defaultdict
from itertools import product
import importlib
pyrandom = importlib.import_module("random")
from sage.all import *
from sage.crypto.block_cipher.sdes import SimplifiedDES

# --------------------------
# Config
# --------------------------
PAIRS_COUNT = 5000       # número de pares (ajusta si quieres)
OUTPUT_DIR = "sdes_linear_outputs"
USE_CSV_INPUT = False
CSV_INPUT_PATH = "plaintext_ciphertext_pairs.csv"
RANDOM_SEED = 42

# --------------------------
# Instancia S-DES
# --------------------------
sdes = SimplifiedDES()
S0, S1 = sdes.sbox()  # cada S-box como tupla de 16 valores en 0..3 (2 bits)

# --------------------------
# Helpers: bits <-> int, parity, expansion E/P
# --------------------------
def bits_list_to_int(bits):
    """bits puede contener objetos Sage; se normaliza a '0'/'1' y se convierte a int."""
    return int("".join(str(int(str(b))) for b in bits), 2)

def int_to_bits_list(x, width):
    return [ (x >> (width - 1 - i)) & 1 for i in range(width) ]

def bitparity(n):
    return bin(int(n)).count("1") % 2

# E/P para S-DES: mapea 4 bits -> 8 bits, convención: indices 1..4 -> mapping [4,1,2,3,2,3,4,1]
E_TABLE = [4,1,2,3,2,3,4,1]
def expansion_4_to_8(n4):
    """n4: int 0..15 representing 4 input bits (MSB first).
       returns int 0..255 representing 8-bit expansion."""
    bits4 = int_to_bits_list(int(n4), 4)
    outbits = []
    for idx in E_TABLE:
        outbits.append(bits4[idx-1])  # idx-1 since E_TABLE is 1-indexed
    return bits_list_to_int(outbits)

# --------------------------
# Build LAT (Agreement Matrix) for a 4->2 S-box
# --------------------------
def build_agreement_matrix_sbox(sbox_tuple):
    IN = 4
    OUT = 2
    size_in = 1 << IN
    size_out = 1 << OUT
    matrix = [[0]*size_out for _ in range(size_in)]
    for a in range(size_in):
        for b in range(size_out):
            c = 0
            for x in range(size_in):
                ax = bitparity(a & x)
                sx = int(sbox_tuple[x])  # 0..3
                bsx = bitparity(b & sx)
                if ax == bsx:
                    c += 1
                else:
                    c -= 1
            matrix[a][b] = c
    return matrix

def correlation_matrix_from_agreement(agreement):
    denom = 1 << 4  # 16
    return [[agreement[a][b] / denom for b in range(len(agreement[0]))] for a in range(len(agreement))]

def probability_matrix_from_correlation(corr):
    return [[(corr[a][b] + 1.0) / 2.0 for b in range(len(corr[0]))] for a in range(len(corr))]

def best_approximation_nontrivial(agreement):
    best = None
    for a in range(len(agreement)):
        for b in range(len(agreement[0])):
            if a == 0 and b == 0:
                continue
            val = agreement[a][b]
            if val != 0:
                if best is None or abs(val) > abs(best[0]):
                    best = (val, a, b)
    return best  # (lat_value, alpha, beta)

# --------------------------
# Pairs generation / read
# --------------------------
def read_pairs_from_csv(path):
    pairs = []
    with open(path, newline='', encoding='utf-8') as f:
        rdr = csv.reader(f)
        for row in rdr:
            if not row: continue
            p_str = row[0].strip()
            c_str = row[1].strip()
            p_list = sdes.string_to_list(p_str)
            c_list = sdes.string_to_list(c_str)
            pairs.append((p_list, c_list))
    return pairs

def generate_pairs_with_random_key(num_pairs, seed=None):
    if seed is not None:
        pyrandom.seed(seed)
    key_int = pyrandom.randint(0, 1023)  # clave de 10 bits
    key_bits = int_to_bits_list(key_int, 10)
    pairs = []
    for _ in range(num_pairs):
        p = pyrandom.randint(0, 255)
        plaintext_bits = int_to_bits_list(p, 8)
        c = sdes.encrypt(plaintext_bits, key_bits)
        pairs.append((plaintext_bits, c))
    return key_bits, pairs

def int_to_bits(x, length):
    """Convierte entero x a lista de bits de tamaño length (MSB first)."""
    return [(x >> i) & 1 for i in reversed(range(length))]

# --------------------------
# Partial decrypt last round logic (helper)
# --------------------------
def get_preoutput_from_ciphertext(c_list):
    preout = sdes.initial_permutation(c_list, inverse=True)  # usamos inverse=True para IP^{-1}
    # normalizar a ints
    preout_ints = [int(str(b)) for b in preout]
    left4 = (preout_ints[0]<<3) | (preout_ints[1]<<2) | (preout_ints[2]<<1) | preout_ints[3]
    right4 = (preout_ints[4]<<3) | (preout_ints[5]<<2) | (preout_ints[6]<<1) | preout_ints[7]
    return left4, right4

# --------------------------
# Attack single S-box: corrected (XOR and normalization)
# --------------------------
def attack_single_sbox_on_subkey(pairs, sbox_index, best_alpha, best_beta):
    N = len(pairs)
    counts_zero = [0]*16
    sbox = S0 if sbox_index == 0 else S1

    # ensure alpha,beta are ints
    alpha = int(best_alpha)
    beta = int(best_beta)

    for p_list, c_list in pairs:
        # get R0 (preoutput left nibble)
        preout = sdes.initial_permutation(c_list, inverse=True)
        preout_ints = [int(str(b)) for b in preout]
        R0 = preout_ints[:4]
        R0_int = (R0[0]<<3) | (R0[1]<<2) | (R0[2]<<1) | R0[3]

        exp8 = expansion_4_to_8(R0_int)
        if sbox_index == 0:
            u_exp_chunk = (exp8 >> 4) & 0xF
        else:
            u_exp_chunk = exp8 & 0xF

        for k4 in range(16):
            u = (int(u_exp_chunk) ^ int(k4)) & 0xF
            s_out = int(sbox[u])       # 0..3
            u_par = bitparity(u & alpha)
            s_par = bitparity(s_out & beta)
            if (u_par ^ s_par) == 0:
                counts_zero[k4] += 1

    results = []
    for k in range(16):
        dev = counts_zero[k] - (N//2)
        results.append((k, dev, counts_zero[k], N))
    results_sorted = sorted(results, key=lambda x: abs(x[1]), reverse=True)
    return results_sorted

# --------------------------
# Multi-approximations / reinforced search for subkey2
# --------------------------
def get_top_approxs_from_agreement(agreement, top_n=6):
    entries = []
    for a in range(len(agreement)):
        for b in range(len(agreement[0])):
            if a == 0 and b == 0:
                continue
            entries.append((a, b, agreement[a][b]))
    entries.sort(key=lambda t: abs(t[2]), reverse=True)
    return entries[:top_n]

def eval_one_approx_on_candidate_sbox(pairs, sbox_index, alpha, beta, candidate_k4):
    """Evalúa una aproximación simple para una sbox y un k4 candidato; devuelve (dev, count_zero)."""
    N = len(pairs)
    count_zero = 0
    sbox = S0 if sbox_index == 0 else S1
    alpha = int(alpha); beta = int(beta)
    for P_bits, C_bits in pairs:
        preout = sdes.initial_permutation(C_bits, inverse=True)
        preout_ints = [int(str(b)) for b in preout]
        R0 = preout_ints[:4]
        R0_int = (R0[0]<<3) | (R0[1]<<2) | (R0[2]<<1) | R0[3]

        exp8 = expansion_4_to_8(R0_int)
        if sbox_index == 0:
            u_exp_chunk = (exp8 >> 4) & 0xF
        else:
            u_exp_chunk = exp8 & 0xF

        u = (int(u_exp_chunk) ^ int(candidate_k4)) & 0xF
        s_out = int(sbox[u])
        u_par = bitparity(u & alpha)
        s_par = bitparity(s_out & beta)
        if (u_par ^ s_par) == 0:
            count_zero += 1
    dev = count_zero - (N//2)
    return dev, count_zero

def score_k2_with_multi_approxs(k2_int, pairs, s0_approxs, s1_approxs):
    k0 = (k2_int >> 4) & 0xF
    k1 = k2_int & 0xF
    acc = 0
    details = {"k2": f"{k2_int:08b}", "parts": (f"{k0:04b}", f"{k1:04b}"), "approxs": []}
    for (alpha, beta, lat) in s0_approxs:
        dev, cnt = eval_one_approx_on_candidate_sbox(pairs, 0, alpha, beta, k0)
        acc += abs(dev)
        details["approxs"].append(("S0", f"{alpha:04b}", f"{beta:02b}", int(lat), dev, cnt))
    for (alpha, beta, lat) in s1_approxs:
        dev, cnt = eval_one_approx_on_candidate_sbox(pairs, 1, alpha, beta, k1)
        acc += abs(dev)
        details["approxs"].append(("S1", f"{alpha:04b}", f"{beta:02b}", int(lat), dev, cnt))
    return acc, details

def multi_approx_subkey2_search(pairs, top_n_per_sbox=6, restrict_to_topk_candidates=8):
    agree0 = build_agreement_matrix_sbox(S0)
    agree1 = build_agreement_matrix_sbox(S1)
    s0_approxs = get_top_approxs_from_agreement(agree0, top_n=top_n_per_sbox)
    s1_approxs = get_top_approxs_from_agreement(agree1, top_n=top_n_per_sbox)

    # obtén top candidates por S-box (usando la mejor aproximación solo para filtrar)
    best_alpha0, best_beta0 = s0_approxs[0][0], s0_approxs[0][1]
    best_alpha1, best_beta1 = s1_approxs[0][0], s1_approxs[0][1]

    s0_scores = []
    for k4 in range(16):
        dev, cnt = eval_one_approx_on_candidate_sbox(pairs, 0, best_alpha0, best_beta0, k4)
        s0_scores.append((k4, abs(dev)))
    s1_scores = []
    for k4 in range(16):
        dev, cnt = eval_one_approx_on_candidate_sbox(pairs, 1, best_alpha1, best_beta1, k4)
        s1_scores.append((k4, abs(dev)))

    s0_scores.sort(key=lambda t: t[1], reverse=True)
    s1_scores.sort(key=lambda t: t[1], reverse=True)

    top_k0 = [k for k,_ in s0_scores[:restrict_to_topk_candidates]]
    top_k1 = [k for k,_ in s1_scores[:restrict_to_topk_candidates]]

    candidates = [(a<<4) | b for a in top_k0 for b in top_k1]

    ranking = []
    for k2 in candidates:
        acc_score, details = score_k2_with_multi_approxs(k2, pairs, s0_approxs, s1_approxs)
        ranking.append((k2, acc_score, details))

    ranking.sort(key=lambda t: t[1], reverse=True)
    return ranking, s0_approxs, s1_approxs

def verify_full_key_from_subkey2_candidate(k2_int, pairs, max_check_pairs=200):
    valid_keys = []
    for key_int in range(1024):
        key_bits = int_to_bits_list(key_int, 10)
        sk2 = sdes.subkey(key_bits, n=2)
        sk2_int = bits_list_to_int(sk2)
        if sk2_int != k2_int:
            continue
        ok = True
        for P_bits, C_bits in pairs[:max_check_pairs]:
            c_test = sdes.encrypt(P_bits, key_bits)
            c_test_str = "".join(str(int(str(b))) for b in c_test)
            C_bits_str = "".join(str(int(str(b))) for b in C_bits)
            if c_test_str != C_bits_str:
                ok = False
                break
        if ok:
            valid_keys.append(key_bits)
    return valid_keys

# --------------------------
# Main flow
# --------------------------
def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # 1) Build LATs / agreement / corr / prob for both S-boxes
    agree0 = build_agreement_matrix_sbox(S0)
    agree1 = build_agreement_matrix_sbox(S1)
    corr0 = correlation_matrix_from_agreement(agree0)
    corr1 = correlation_matrix_from_agreement(agree1)
    prob0 = probability_matrix_from_correlation(corr0)
    prob1 = probability_matrix_from_correlation(corr1)
    best0 = best_approximation_nontrivial(agree0)  # (lat_val, alpha, beta)
    best1 = best_approximation_nontrivial(agree1)

    # export LATs to CSV
    def export_matrix_csv(mat, path, in_width=4, out_width=2, header=None):
        with open(path, "w", newline='', encoding='utf-8') as f:
            w = csv.writer(f)
            if header:
                w.writerow(header)
            for a in range(len(mat)):
                for b in range(len(mat[0])):
                    w.writerow([f"{a:0{in_width}b}", f"{b:0{out_width}b}", float(mat[a][b])])

    export_matrix_csv(agree0, os.path.join(OUTPUT_DIR, "s0_agreement.csv"), header=["alpha_4bit","beta_2bit","LAT"])
    export_matrix_csv(corr0, os.path.join(OUTPUT_DIR, "s0_correlation.csv"), header=["alpha_4bit","beta_2bit","correlation"])
    export_matrix_csv(prob0, os.path.join(OUTPUT_DIR, "s0_probability.csv"), header=["alpha_4bit","beta_2bit","probability"])

    export_matrix_csv(agree1, os.path.join(OUTPUT_DIR, "s1_agreement.csv"), header=["alpha_4bit","beta_2bit","LAT"])
    export_matrix_csv(corr1, os.path.join(OUTPUT_DIR, "s1_correlation.csv"), header=["alpha_4bit","beta_2bit","correlation"])
    export_matrix_csv(prob1, os.path.join(OUTPUT_DIR, "s1_probability.csv"), header=["alpha_4bit","beta_2bit","probability"])

    # print best approximations
    lat0, alpha0, beta0 = best0
    lat1, alpha1, beta1 = best1
    print("S0 best: alpha={} beta={} LAT={} corr={:.5f}".format(f"{alpha0:04b}", f"{beta0:02b}", lat0, lat0/16.0))
    print("S1 best: alpha={} beta={} LAT={} corr={:.5f}".format(f"{alpha1:04b}", f"{beta1:02b}", lat1, lat1/16.0))

    # 2) Generate or read pairs
    if USE_CSV_INPUT and os.path.exists(CSV_INPUT_PATH):
        pairs = read_pairs_from_csv(CSV_INPUT_PATH)
        random_key = None
    else:
        pyrandom.seed(RANDOM_SEED)
        key, pairs = generate_pairs_with_random_key(PAIRS_COUNT, seed=RANDOM_SEED)
        random_key = key
        with open(os.path.join(OUTPUT_DIR,"generated_key.txt"), "w", encoding='utf-8') as f:
            f.write("".join(str(b) for b in random_key))
        with open(os.path.join(OUTPUT_DIR,"pairs.csv"), "w", newline='', encoding='utf-8') as f:
            w = csv.writer(f)
            for p,c in pairs:
                w.writerow(["".join(str(b) for b in p), "".join(str(b) for b in c)])

    print(f"Pairs used: {len(pairs)}")
    if random_key is not None:
        print("Clave real (10 bits):", "".join(str(b) for b in random_key))
        subk2 = sdes.subkey(random_key, n=2)
        print("Subkey 2 real (8 bits):", "".join(str(b) for b in subk2))

    # 3) Attack each S-box individually (produce candidates)
    res_s0 = attack_single_sbox_on_subkey(pairs, sbox_index=0, best_alpha=alpha0, best_beta=beta0)
    res_s1 = attack_single_sbox_on_subkey(pairs, sbox_index=1, best_alpha=alpha1, best_beta=beta1)

    # save s-box candidate CSVs
    with open(os.path.join(OUTPUT_DIR,"s0_candidates.csv"), "w", newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(["k4","deviation","count_zero","N"])
        for k,dev,cnt,Nn in res_s0:
            w.writerow([f"{k:04b}", int(dev), int(cnt), Nn])

    with open(os.path.join(OUTPUT_DIR,"s1_candidates.csv"), "w", newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(["k4","deviation","count_zero","N"])
        for k,dev,cnt,Nn in res_s1:
            w.writerow([f"{k:04b}", int(dev), int(cnt), Nn])

    # 4) Multi-approx reinforced search for subkey2
    # Ajusta top_n_per_sbox y restrict_to_topk_candidates según recursos
    ranking, s0_approxs, s1_approxs = multi_approx_subkey2_search(pairs, top_n_per_sbox=6, restrict_to_topk_candidates=8)

    # print top candidates
    print("\nTop candidates (subkey2) by accumulated score:")
    for k2, score, details in ranking[:16]:
        print(f" Candidate: {k2:08b} score: {score}")

    best_k2 = ranking[0][0] if ranking else None
    best_score = ranking[0][1] if ranking else None
    print("Guessed subkey2 (multi-approx best):", f"{best_k2:08b}" if best_k2 is not None else None, "score:", best_score)

    # 5) Verify full 10-bit keys compatible with best_k2
    found_keys = []
    if best_k2 is not None:
        found_keys = verify_full_key_from_subkey2_candidate(best_k2, pairs, max_check_pairs=min(200, len(pairs)))
        print("Claves completas (10-bit) compatibles con subkey2 candidato (verificadas sobre pares):")
        for kb in found_keys:
            print(" ", "".join(str(b) for b in kb))
    else:
        print("No candidate k2 found.")

    # 6) Summary JSON
    real_subk2_int = None
    if random_key is not None:
        real_subk2_bits = sdes.subkey(random_key, n=2)
        real_subk2_int = bits_list_to_int(real_subk2_bits)

    summary = {
        "pairs_used": len(pairs),
        "random_key": "".join(str(b) for b in random_key) if random_key is not None else None,
        "subkey2_real": "{:08b}".format(real_subk2_int) if real_subk2_int is not None else None,
        "subkey2_best_guess": "{:08b}".format(real_subk2_int) if best_k2 is not None else None,
        "best_guess_score": int(best_score) if best_score is not None else None,
        "s0_best_alpha": f"{alpha0:04b}",
        "s0_best_beta": f"{beta0:02b}",
        "s0_lat": int(lat0),
        "s1_best_alpha": f"{alpha1:04b}",
        "s1_best_beta": f"{beta1:02b}",
        "s1_lat": int(lat1),
        "s0_top_candidates": [ {"k4":f"{k:04b}","deviation":int(dev),"count_zero":int(cnt)} for k,dev,cnt,_ in res_s0[:8] ],
        "s1_top_candidates": [ {"k4":f"{k:04b}","deviation":int(dev),"count_zero":int(cnt)} for k,dev,cnt,_ in res_s1[:8] ],
    }
    with open(os.path.join(OUTPUT_DIR,"linear_attack_summary.json"), "w", encoding='utf-8') as jf:
        json.dump(summary, jf, indent=4)

    print("\nResumen guardado en:", OUTPUT_DIR)
    print(json.dumps(summary, indent=2))

if __name__ == "__main__":
    main()
