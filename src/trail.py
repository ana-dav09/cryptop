from sage.all import *
import sys
#sys.path.append("/mnt/c/users/hp/desktop/diseño/src")

from claasp.ciphers.block_ciphers.aes_block_cipher import AESBlockCipher

aes = AESBlockCipher(number_of_rounds=4)
key = 0xFFFFFF
plaintext = 0x000000

print(aes.evaluate([plaintext, key]))
