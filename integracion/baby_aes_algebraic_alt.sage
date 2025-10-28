#!/usr/bin/env sage
# baby_aes_algebraic_full_check.sage
# Intenta: (A) variantes de construcción SAT (endianness/bytes) y (B) enumeración por fuerza bruta
import sys, json, time
from sage.all import *
PROJECT_ROOT = "/mnt/c/users/hp/desktop/diseno/integracion"
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from babyAES_block_cipher import BabyAESCipher
from claasp.cipher_modules.models.sat.sat_models.sat_cipher_model import SatCipherModel
from claasp.utils.integer import to_binary

def build_fixed_vars_from_bits(component_plain_id, component_cipher_id, plaintext_bits_le, ciphertext_bits_le):
    # Construye fixed_variables usando lista LSB-first completa (16 bits)
    fixed = [{
        'component_id': component_plain_id,
        'constraint_type': 'equal',
        'bit_positions': list(range(0,8)),
        'bit_values': plaintext_bits_le[0:8]
    }, {
        'component_id': component_plain_id,
        'constraint_type': 'equal',
        'bit_positions': list(range(8,16)),
        'bit_values': plaintext_bits_le[8:16]
    }, {
        'component_id': component_cipher_id,
        'constraint_type': 'equal',
        'bit_positions': list(range(0,8)),
        'bit_values': ciphertext_bits_le[0:8]
    }, {
        'component_id': component_cipher_id,
        'constraint_type': 'equal',
        'bit_positions': list(range(8,16)),
        'bit_values': ciphertext_bits_le[8:16]
    }]
    return fixed

def build_variant_B_bits_from_le(bits_le):
    # Variante B: invertir el orden DENTRO de cada byte (MSB-first por byte),
    # manteniendo el orden de bytes (low byte primero, high byte después).
    low = bits_le[0:8][::-1]   # low byte LSB->MSB revertido -> MSB->LSB
    high = bits_le[8:16][::-1]
    return low + high

def try_sat_variant(babyAES, plaintext, key_expected, component_plain_id='plaintext', component_cipher_id=None, solver_name="CRYPTOMINISAT_EXT", variant='A'):
    """
    Construye SAT con la variante seleccionada ('A' LSB-first, 'B' MSB-per-byte)
    y resuelve. Devuelve (status, recovered_key_int_or_None, solution_dict_or_None).
    """
    if component_cipher_id is None:
        # obtener último componente output por defecto
        component_cipher_id = babyAES.get_all_components()[-1].id

    plaintext_bits_le = to_binary(plaintext, 16)   # LSB-first
    ciphertext = babyAES.evaluate([key_expected, plaintext])
    ciphertext_bits_le = to_binary(ciphertext, 16)

    if variant == 'A':
        bits_plain = plaintext_bits_le
        bits_cipher = ciphertext_bits_le
    else:
        bits_plain = build_variant_B_bits_from_le(plaintext_bits_le)
        bits_cipher = build_variant_B_bits_from_le(ciphertext_bits_le)

    fixed_vars = build_fixed_vars_from_bits(component_plain_id, component_cipher_id, bits_plain, bits_cipher)

    sat = SatCipherModel(babyAES)
    try:
        sat.build_cipher_model(fixed_vars)
    except Exception as e:
        return ('ERROR_BUILD', None, {"error": str(e)})

    try:
        solution = sat.solve('cipher', solver_name=solver_name)
    except Exception as e:
        return ('ERROR_SOLVE', None, {"error": str(e)})

    status = solution.get('status')
    if status != 'SATISFIABLE':
        return (status, None, solution)
    # extraer key
    comps = solution.get('components_values', {})
    # buscar candidato 'key'
    key_val = None
    if 'key' in comps:
        key_val = comps['key'].get('value')
    else:
        # heurística
        for cid, cinfo in comps.items():
            if 'key' in cid.lower():
                key_val = cinfo.get('value'); break
    if key_val is None:
        return (status, None, solution)
    # convertir a entero (soporta '0x..' o int o lista)
    recovered = None
    try:
        if isinstance(key_val, str) and key_val.startswith('0x'):
            recovered = int(key_val, 16)
        elif isinstance(key_val, (list, tuple)):
            # suponer little-endian (LSB-first)
            val = 0
            for i,b in enumerate(key_val):
                val |= (int(b) & 1) << i
            recovered = val
        elif isinstance(key_val, str) and all(c in '01' for c in key_val):
            # binario como string: asumir MSB-first
            recovered = int(key_val, 2)
        else:
            recovered = int(key_val)
    except Exception:
        recovered = None

    return (status, recovered, solution)

def brute_force_find_keys(babyAES, plaintext, ciphertext):
    """Forza bruta sobre toda la clave de 16 bits, devuelve lista de keys que producen ciphertext."""
    matches = []
    # iterar 0..65535
    for k in range(0, 1<<16):
        if babyAES.evaluate([k, plaintext]) == ciphertext:
            matches.append(k)
    return matches

def main():
    babyAES = BabyAESCipher(number_of_rounds=3, word_size=4, state_size=2)
    plaintext = 0x063b
    expected_key = 0x21c2
    ciphertext = babyAES.evaluate([expected_key, plaintext])

    print("Valores:")
    print(f"  PT: 0x{plaintext:04x}")
    print(f"  Key esperada: 0x{expected_key:04x}")
    print(f"  CT objetivo: 0x{ciphertext:04x}\n")

    # Intento 1: SAT variante A (LSB-first)
    print("Intentando SAT Variante A (LSB-first)...")
    statusA, recA, solA = try_sat_variant(babyAES, plaintext, expected_key, variant='A', solver_name="CRYPTOMINISAT_EXT")
    if statusA == 'SATISFIABLE' and recA is not None:
        print(f"  SAT A devolvió key = 0x{recA:04x}")
        ct_test = babyAES.evaluate([recA, plaintext])
        print(f"   -> CT con key recuperada: 0x{ct_test:04x}  (igual a objetivo? {ct_test == ciphertext})")
        if recA == expected_key or ct_test == ciphertext:
            print("  ==> Clave correcta encontrada por SAT (Variante A).")
            result = {"method":"SAT_variant_A", "recovered_key":f"0x{recA:04x}", "match": (recA==expected_key or ct_test==ciphertext)}
            print(json.dumps(result, indent=2))
            return
    else:
        print(f"  SAT A status={statusA}")

    # Intento 2: SAT variante B (MSB per byte)
    print("\nIntentando SAT Variante B (MSB per byte dentro de cada byte)...")
    statusB, recB, solB = try_sat_variant(babyAES, plaintext, expected_key, variant='B', solver_name="CRYPTOMINISAT_EXT")
    if statusB == 'SATISFIABLE' and recB is not None:
        print(f"  SAT B devolvió key = 0x{recB:04x}")
        ct_test = babyAES.evaluate([recB, plaintext])
        print(f"   -> CT con key recuperada: 0x{ct_test:04x}  (igual a objetivo? {ct_test == ciphertext})")
        if recB == expected_key or ct_test == ciphertext:
            print("  ==> Clave correcta encontrada por SAT (Variante B).")
            result = {"method":"SAT_variant_B", "recovered_key":f"0x{recB:04x}", "match": (recB==expected_key or ct_test==ciphertext)}
            print(json.dumps(result, indent=2))
            return
    else:
        print(f"  SAT B status={statusB}")

    # Si llegamos aquí, SAT (ambas variantes) no devolvió la clave correcta.
    print("\nNo se obtuvo la clave correcta desde SAT con las dos variantes.")
    print("Ahora ejecutando fuerza bruta completa (2^16 = 65536 claves) para enumerar todas las claves que producen el ciphertext esperado...\n")
    t0 = time.time()
    matches = brute_force_find_keys(babyAES, plaintext, ciphertext)
    dt = time.time() - t0
    print(f"Búsqueda por fuerza bruta finalizada en {dt:.3f}s. Encontradas {len(matches)} coincidencias.\n")
    if matches:
        print("Claves encontradas (hex):")
        for k in matches:
            print(f"  0x{k:04x}")
    else:
        print("No se encontró ninguna clave mediante fuerza bruta (esto sería sorprendente).")

    # Output JSON resumen
    summary = {
        "method": "SAT_variants_then_bruteforce",
        "plaintext": f"0x{plaintext:04x}",
        "ciphertext": f"0x{ciphertext:04x}",
        "expected_key": f"0x{expected_key:04x}",
        "sat_variant_A_status": statusA,
        "sat_variant_A_key": f"0x{recA:04x}" if recA is not None else None,
        "sat_variant_B_status": statusB,
        "sat_variant_B_key": f"0x{recB:04x}" if recB is not None else None,
        "bruteforce_matches": [f"0x{k:04x}" for k in matches],
        "bruteforce_time_seconds": dt
    }
    print("\nJSON resumen:")
    print(json.dumps(summary, indent=2))

if __name__ == "__main__":
    main()
