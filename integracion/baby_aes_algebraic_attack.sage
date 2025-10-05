from babyAES_block_cipher import BabyAESCipher
from claasp.cipher_modules.models.sat.sat_models.sat_cipher_model import SatCipherModel
from claasp.utils.integer import to_binary
import json


babyAES = BabyAESCipher(number_of_rounds = 3, word_size = 4, state_size = 2)
sat = SatCipherModel(babyAES)

# Generacion de valores
plaintext = 0x063b
key = 0x21c2

plaintext_binary = to_binary(plaintext, 16)
#print(to_binary(plaintext, 16)[::-1])
#print(to_binary(key, 16)[::-1])

ciphertext = babyAES.evaluate([key, plaintext])
ciphertext_binary = to_binary(ciphertext, 16)
#print(ciphertext_binary)
fixed_variables = [{
    'component_id': 'plaintext',
    'constraint_type': 'equal',
    'bit_positions': [0, 1, 2, 3, 4, 5, 6, 7],
    'bit_values': [plaintext_binary[i] for i in range(8)]
}, {
    'component_id': 'plaintext',
    'constraint_type': 'equal',
    'bit_positions': [8, 9, 10, 11, 12, 13, 14, 15],
    'bit_values': [plaintext_binary[i] for i in range(8, 16)]
}, {
    'component_id': 'cipher_output_2_14',
    'constraint_type': 'equal',
    'bit_positions': [0, 1, 2, 3, 4, 5, 6, 7],
    'bit_values': [ciphertext_binary[i] for i in range(8)]
}, {
    'component_id': 'cipher_output_2_14',
    'constraint_type': 'equal',
    'bit_positions': [8, 9, 10, 11, 12, 13, 14, 15],
    'bit_values': [ciphertext_binary[i] for i in range(8,16)]
}]
sat.build_cipher_model(fixed_variables)
solution = sat.solve('cipher', solver_name="cryptominisat")

res = {"solver": "cryptominisat", "plaintext": f'0x{plaintext:04x}', "ciphertext": f'0x{ciphertext:04x}', "key": solution['components_values']['key']['value'], "time": solution['solving_time_seconds']}
print(json.dumps(res))

#print(solution)