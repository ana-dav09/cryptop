from mini_block_cipher import MiniBlockCipher
from claasp.cipher_modules.models.sat.sat_models.sat_cipher_model import SatCipherModel
from claasp.utils.integer import to_binary
import random

mini = MiniBlockCipher()
print(mini.get_dict())
mini.build_cipher()

sat = SatCipherModel(mini)

# number of tries
N = 256
key_to_be_found = random.randint(0,65535)  
# Without modifications, in my computer the keys [0x1866, 0x4416] or [6246,17430] with all the samples finds the key correctly
key_binary = to_binary(key_to_be_found, 16)[::-1]

print(f"We need to found this key: {key_to_be_found} or in binary: {key_binary} or in hex {hex(key_to_be_found)}")
print(f"We are trying with {N} random plaintext")

keys_founded = {}

# Generacion de valores
for i in range(N):
    #plaintext = random.randint(0,255)
    plaintext = i
    plaintext_binary = to_binary(plaintext, 8)[::-1]
    ciphertext = mini.evaluate([key_to_be_found, plaintext])
    ciphertext_binary = to_binary(ciphertext, 8)[::-1]
    #cipher_output_3_9
    fixed_variables = [{
        'component_id': 'plaintext',
        'constraint_type': 'equal',
        'bit_positions': [0, 1, 2, 3],
        'bit_values': [plaintext_binary[i] for i in range(4)]
    }, {
        'component_id': 'plaintext',
        'constraint_type': 'equal',
        'bit_positions': [4, 5, 6, 7],
        'bit_values': [plaintext_binary[i] for i in range(4, 8)]
    }, {
        'component_id': 'cipher_output_3_9',
        'constraint_type': 'equal',
        'bit_positions': [0, 1, 2, 3],
        'bit_values': [ciphertext_binary[i] for i in range(4)]
    }, {
        'component_id': 'cipher_output_3_9',
        'constraint_type': 'equal',
        'bit_positions': [4, 5, 6, 7],
        'bit_values': [ciphertext_binary[i] for i in range(4,8)]
    }]
    
    sat.build_cipher_model(fixed_variables)
    solution = sat.solve('cipher', solver_name="cryptominisat")

    if solution['status'] == 'SATISFIABLE':
        key_founded = solution['components_values']['key']['value']
        keys_founded[key_founded] = keys_founded.get(key_founded, 0) + 1
        
most_probable_key = max(keys_founded, key=keys_founded.get)
print(f"Probable key: {most_probable_key}")