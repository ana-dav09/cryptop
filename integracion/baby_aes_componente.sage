#!/usr/bin/env sage

from babyAES_block_cipher import BabyAESCipher

def reverse_bits_16(value):
    return int(format(value, '016b')[::-1], 2)

babyAES = BabyAESCipher(number_of_rounds=3, word_size=4, state_size=2)

pt_inv = 0xdc60
ct_inv = 0x4ac7
key_original = 0x21c2
key_recovered = 0x6716

key_orig_inv = reverse_bits_16(key_original)
key_recovered_inv = reverse_bits_16(key_recovered)

print("Probando todas las combinaciones en el mundo invertido:")
print("="*60)

tests = [
    (pt_inv, key_original, "Key original"),
    (pt_inv, key_orig_inv, "Key original invertida"),
    (pt_inv, key_recovered, "Key recuperada"),
    (pt_inv, key_recovered_inv, "Key recuperada invertida"),
]

for pt, key, desc in tests:
    ct = babyAES.evaluate([key, pt])
    match = "✓" if ct == ct_inv else ""
    print(f"{desc:25s}: Key=0x{key:04x} → CT=0x{ct:04x} {match}")

print(f"\nCT esperado: 0x{ct_inv:04x}")

print("\n" + "="*60)
print("Si ninguna coincide, entonces hay un bug más profundo en CLAASP")