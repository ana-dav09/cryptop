# baby_aes_sat.py
from pysat.formula import CNF
from pysat.solvers import Minisat22
from itertools import count

# Asignador de índices a variables (x0, x1, ..., k0, ..., y0, ..., intermediates)
var_ids = {}
var_counter = count(1)

def new_var(name):
    if name not in var_ids:
        var_ids[name] = next(var_counter)
    return var_ids[name]

# XOR lógico en CNF: z = x ^ y  => 4 cláusulas
def xor_cnf(x, y, z):
    return [
        [-x, -y, -z],
        [-x,  y,  z],
        [ x, -y,  z],
        [ x,  y, -z]
    ]

# XNOR lógico (para igualdad): z = x == y
def xnor_cnf(x, y, z):
    return xor_cnf(x, y, z) + [[-z]]  # z = NOT(xor) == 0

# ----------- Ejemplo básico: input xor key = output ----------
def build_simple_system():
    cnf = CNF()

    # 4 bits de input, key y output
    for i in range(4):
        x = new_var(f"x{i}")
        k = new_var(f"k{i}")
        y = new_var(f"y{i}")
        z = new_var(f"z{i}")  # x ^ k = z
        cnf.extend(xor_cnf(x, k, z))
        # Luego, z == y  →  z XOR y = 0
        cnf.extend(xnor_cnf(z, y, new_var(f"eq{i}")))

    return cnf

# ----------- Resolver sistema con Minisat ----------
def solve_system(cnf, input_vals, output_vals):
    with Minisat22(bootstrap_with=cnf.clauses) as solver:
        # Fijar input bits
        for i, val in enumerate(input_vals):
            lit = new_var(f"x{i}")
            solver.add_clause([lit if val else -lit])

        # Fijar output bits
        for i, val in enumerate(output_vals):
            lit = new_var(f"y{i}")
            solver.add_clause([lit if val else -lit])

        if solver.solve():
            model = solver.get_model()
            # Extraer bits de clave
            key_bits = []
            for i in range(4):
                var = new_var(f"k{i}")
                key_bits.append(1 if var in model else 0)
            print(f"Clave recuperada: {key_bits}")
        else:
            print("No se encontró solución.")

# ----------- Prueba ----------
if __name__ == "__main__":
    # Sistema ejemplo: x ^ k = y
    cnf = build_simple_system()

    # Entrada y salida conocidas
    input_bits = [0, 1, 1, 0]
    key_bits = [1, 0, 1, 1]
    output_bits = [i ^ k for i, k in zip(input_bits, key_bits)]

    print(f"Salida cifrada: {output_bits}")
    solve_system(cnf, input_bits, output_bits)
