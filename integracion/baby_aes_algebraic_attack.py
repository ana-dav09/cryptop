#!/usr/bin/env sage
# baby_aes_algebraic_attack_sage.py
# Versión para ejecutarse con Sage (no venv)

import os
import sys
import json
import argparse
import traceback
import shutil

# Para Sage, los imports deben estar después de asegurar que Sage está cargado
try:
    # Verificar que estamos en Sage
    from sage.all import *
except ImportError:
    sys.stderr.write("ERROR: Este script debe ejecutarse con Sage, no con Python puro.\n")
    sys.stderr.write("Usa: sage baby_aes_algebraic_attack_sage.py\n")
    sys.exit(1)

# Ahora importar las dependencias del proyecto
PROJECT_ROOT = "/mnt/c/users/hp/desktop/diseno/integracion"
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

try:
    from babyAES_block_cipher import BabyAESCipher
    from claasp.cipher_modules.models.sat.sat_models.sat_cipher_model import SatCipherModel
    from claasp.utils.integer import to_binary
except Exception as e:
    sys.stderr.write("ERROR: No se pudieron importar las dependencias necesarias.\n")
    sys.stderr.write(str(e) + "\n")
    sys.stderr.write(traceback.format_exc())
    sys.exit(2)

def parse_int(s):
    if isinstance(s, int):
        return s
    s = str(s).strip()
    if s.startswith("0x") or s.startswith("0X"):
        return int(s, 16)
    return int(s, 10)

def build_fixed_variables(plaintext_binary, ciphertext_binary):
    return [{
        'component_id': 'plaintext',
        'constraint_type': 'equal',
        'bit_positions': list(range(0, 8)),
        'bit_values': [int(plaintext_binary[i]) for i in range(0,8)]
    }, {
        'component_id': 'plaintext',
        'constraint_type': 'equal',
        'bit_positions': list(range(8, 16)),
        'bit_values': [int(plaintext_binary[i]) for i in range(8,16)]
    }, {
        'component_id': 'cipher_output_2_14',
        'constraint_type': 'equal',
        'bit_positions': list(range(0,8)),
        'bit_values': [int(ciphertext_binary[i]) for i in range(0,8)]
    }, {
        'component_id': 'cipher_output_2_14',
        'constraint_type': 'equal',
        'bit_positions': list(range(8,16)),
        'bit_values': [int(ciphertext_binary[i]) for i in range(8,16)]
    }]

def detect_available_solver():
    """
    Detecta automáticamente un solver SAT disponible.
    Retorna el nombre del solver en formato CLAASP.
    """
    # Preferir solvers externos (_EXT) ya que pycryptosat está roto
    if shutil.which("cryptominisat5") or shutil.which("cryptominisat"):
        return "CRYPTOMINISAT_EXT"
    elif shutil.which("minisat"):
        return "MINISAT_EXT"
    elif shutil.which("glucose"):
        return "GLUCOSE_EXT"
    elif shutil.which("glucose-syrup"):
        return "GLUCOSE_SYRUP_EXT"
    elif shutil.which("kissat"):
        return "KISSAT_EXT"
    elif shutil.which("cadical"):
        return "CADICAL_EXT"
    
    # Si no hay solvers externos, intentar internos de Sage
    # (probablemente no funcionarán si pycryptosat está roto)
    try:
        import pycryptosat
        return "cryptominisat"
    except:
        pass
    
    return None

def main():
    parser = argparse.ArgumentParser(description="Ataque algebraico a BabyAES (Sage).")
    parser.add_argument("--plaintext", type=parse_int, default=parse_int("0x063b"),
                        help="Plaintext (hex 0xNNNN o decimal). Default 0x063b")
    parser.add_argument("--key", type=parse_int, default=parse_int("0x21c2"),
                        help="Clave (hex 0xNNNN o decimal). Default 0x21c2")
    parser.add_argument("--rounds", type=int, default=3, help="Número de rondas de BabyAES")
    parser.add_argument("--solver", type=str, default=None,
                        help="Solver SAT a usar. Opciones: CRYPTOMINISAT_EXT, MINISAT_EXT, GLUCOSE_EXT, etc.")
    parser.add_argument("--quiet", action="store_true", help="No imprimir logs, sólo JSON al final")
    args = parser.parse_args()

    try:
        number_of_rounds = args.rounds
        word_size = 4
        state_size = 2

        babyAES = BabyAESCipher(number_of_rounds=number_of_rounds,
                               word_size=word_size,
                               state_size=state_size)
        sat = SatCipherModel(babyAES)

        plaintext = int(args.plaintext)
        key = int(args.key)

        if not args.quiet:
            sys.stderr.write(f"Info: plaintext=0x{plaintext:04x}, key=0x{key:04x}, rounds={number_of_rounds}\n")

        plaintext_binary = to_binary(plaintext, 16)
        ciphertext = babyAES.evaluate([key, plaintext])
        ciphertext_binary = to_binary(ciphertext, 16)

        fixed_variables = build_fixed_variables(plaintext_binary, ciphertext_binary)

        if not args.quiet:
            sys.stderr.write("Info: Construyendo modelo SAT...\n")

        sat.build_cipher_model(fixed_variables)

        # Decidir solver
        solver_name = args.solver
        if not solver_name:
            solver_name = detect_available_solver()
        
        if solver_name is None:
            sys.stderr.write("ERROR: No se encontró un SAT solver disponible.\n")
            sys.stderr.write("Solvers soportados por CLAASP:\n")
            sys.stderr.write("  Externos (requieren binario en PATH):\n")
            sys.stderr.write("    - CRYPTOMINISAT_EXT (cryptominisat5 o cryptominisat)\n")
            sys.stderr.write("    - MINISAT_EXT (minisat)\n")
            sys.stderr.write("    - GLUCOSE_EXT (glucose)\n")
            sys.stderr.write("    - KISSAT_EXT (kissat)\n")
            sys.stderr.write("  Internos (requieren pycryptosat funcionando):\n")
            sys.stderr.write("    - cryptominisat\n")
            sys.exit(4)

        if not args.quiet:
            sys.stderr.write(f"Info: Usando solver '{solver_name}'.\n")
            sys.stderr.write("Info: Resolviendo...\n")

        solution = sat.solve('cipher', solver_name=solver_name)

        res = {
            "solver": solver_name,
            "plaintext": f"0x{plaintext:04x}",
            "ciphertext": f"0x{ciphertext:04x}",
            "solving_time_seconds": solution.get('solving_time_seconds', None),
            "status": solution.get('status', None),
            "components_values": {}
        }

        try:
            key_value = solution['components_values']['key']['value']
            res["components_values"]["key"] = key_value
            if isinstance(key_value, (list, tuple)):
                bitstr = ''.join(str(int(b)) for b in key_value)
                try:
                    ival = int(bitstr, 2)
                    res["components_values"]["key_hex_reconstructed"] = f"0x{ival:04x}"
                    
                    if not args.quiet:
                        match = "✓ CORRECTO" if ival == key else "✗ INCORRECTO"
                        sys.stderr.write(f"\nClave original:      0x{key:04x}\n")
                        sys.stderr.write(f"Clave recuperada:    0x{ival:04x} {match}\n")
                except Exception:
                    pass
        except Exception as e:
            if not args.quiet:
                sys.stderr.write(f"Advertencia: No se pudo extraer la clave: {e}\n")

        print(json.dumps(res, indent=2))
        sys.exit(0)

    except Exception as e:
        sys.stderr.write("EXCEPCIÓN durante la ejecución del ataque:\n")
        sys.stderr.write(str(e) + "\n")
        sys.stderr.write(traceback.format_exc())
        sys.exit(3)

if __name__ == "__main__":
    main()