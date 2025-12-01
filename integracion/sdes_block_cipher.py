from claasp.cipher import Cipher
from claasp.name_mappings import INPUT_KEY, INPUT_PLAINTEXT, BLOCK_CIPHER

class SimplifiedDESCipher(Cipher):

    #################################### NOTAS ################################################
    # Uso rotate en lugar de concatenate en los pasos de juntar bloques de bits               #
    # para evitar mensajes de error al momento de solicitar el cnf o solucionar el sistema.   #
    # Esto no afecta el funcionamiento del cifrado, ya que los bits quedan en el mismo orden. #
    ###########################################################################################
    
    def __init__(self,number_of_rounds: int = 2, word_size: int = 8):
        if word_size != 8:
            raise ValueError("wordsize incorrect")
        if number_of_rounds != 2:
            raise ValueError("number of rounds incorrect")
        
        self.cipher_block_size = word_size
        self.key_block_size = 10
        self.nrounds = number_of_rounds
        self.sbox_input_bit_size = 4
        self.sbox_output_bit_size = 2
        self.number_of_sboxes = 2

        super().__init__(
            family_name="sdes_block_cipher",
            cipher_type=BLOCK_CIPHER,
            cipher_inputs=[INPUT_KEY, INPUT_PLAINTEXT],
            cipher_inputs_bit_size=[self.key_block_size, self.cipher_block_size],
            cipher_output_bit_size=self.cipher_block_size,
        )

        self.sbox0 = [0x01, 0x03, 0x00, 0x02, 0x03, 0x01, 0x02, 0x00, 0x00, 0x03, 0x02, 0x01, 0x01, 0x03, 0x03, 0x02]
        self.sbox1 = [0x00, 0x02, 0x01, 0x00, 0x02, 0x01, 0x03, 0x03, 0x03, 0x02, 0x00, 0x01, 0x01, 0x00, 0x00, 0x03]

        self.inital_permutation = [1, 5, 2, 0, 3, 7, 4, 6]
        self.expansion_permutation = [3, 0, 1, 2, 1, 2, 3, 0]
        self.key_permutation_10 = [2, 4, 1, 6, 3, 9, 0, 8, 7, 5]
        self.key_permutation_8 = [5, 2, 6, 3, 7, 4, 9, 8]
        self.permutation_4 = [1, 3, 2, 0]
        self.final_permutation = [3, 0, 2, 4, 6, 1, 7, 5]

        #Rounds definition
        self.add_round()
        # Aplly the initial permutation
        first_permutation = self.add_permutation_component(
            [INPUT_PLAINTEXT],
            [self.inital_permutation],
            self.cipher_block_size,
            list(range(self.cipher_block_size)),
        )

        # Apply the key permutation (p10)
        key_permutation = self.add_permutation_component(
            [INPUT_KEY],
            [self.key_permutation_10],
            10,
            list(range(10)),
        )

        accumulated_word = first_permutation
        accumulated_key = key_permutation
        # For each round
        for round in range(self.nrounds):
            # Separate left and right
            left_word = self.add_permutation_component(
                [accumulated_word.id],
                [[0, 1, 2, 3]],
                4,
                [0, 1, 2, 3],
            )
            right_word = self.add_permutation_component(
                [accumulated_word.id],
                [[4, 5, 6, 7]],
                4,
                [0, 1, 2, 3],
            )
            # Expand right word
            expansion_permutation = self.add_permutation_component(
                [right_word.id],
                [self.expansion_permutation],
                8,
                list(range(8)),
            )

            

            # Get round key
            if round == 0:
                accumulated_key = self.add_permutation_component(
                    [accumulated_key.id],
                    [[1, 2, 3, 4, 0, 6, 7, 8, 9, 5]],
                    10,
                    list(range(10)),
                )
            else:
                accumulated_key = self.add_permutation_component(
                    [accumulated_key.id],
                    [[2, 3, 4, 0, 1, 7, 8, 9, 5, 6]],
                    10,
                    list(range(10)),
                )
            
            round_key = self.add_permutation_component(
                [accumulated_key.id],
                [self.key_permutation_8],
                8,
                list(range(8)),
            )

            # XOR with round key
            add_round_key = self.add_XOR_component(
                [expansion_permutation.id]+ [round_key.id],
                [list(range(self.cipher_block_size))]+ [list(range(self.cipher_block_size))],
                8,
            )

            # S-Boxes
            sbox_components = []
            for i in range(self.number_of_sboxes):
                sbox = self.add_SBOX_component(
                    [add_round_key.id],
                    [[j for j in range(i * self.sbox_input_bit_size, (i + 1) * self.sbox_input_bit_size)]],
                    self.sbox_output_bit_size,
                    self.sbox0 if i == 0 else self.sbox1,
                )
                sbox_components.append(sbox)
            
            # Concatenate the sbox outputs
            sbox_output = self.add_rotate_component(
                [sbox_components[i].id for i in range(self.number_of_sboxes)],
                [[i for i in range(self.sbox_output_bit_size)] for _ in range(self.number_of_sboxes)],
                4,
                0
            )
            
            # Permutation4 over the sbox output
            permutation4 = self.add_permutation_component(
                [sbox_output.id],
                [self.permutation_4],
                4,
                list(range(4)),
            )

            # XOR left part with P4 output
            add_left_xor = self.add_XOR_component(
                [permutation4.id] + [left_word.id],
                [list(range(4))] + [list(range(4))],
                4,
            )

            # Combine left and right 
            accumulated_word = self.add_rotate_component(
                [add_left_xor.id, right_word.id],
                [[i for i in range(4)] for _ in range(2)],
                8,
                0
            )

            if round == 0:
                # Swap for next round
                accumulated_word = self.add_rotate_component(
                    [accumulated_word.id],
                    [list(range(self.cipher_block_size))],
                    self.cipher_block_size,
                    4
                )
                self.add_round()

        # Apply the final permutation (inverse of initial permutation)
    
        final_permutation = self.add_permutation_component(
            [accumulated_word.id],
            [self.final_permutation],
            self.cipher_block_size,
            list(range(self.cipher_block_size)),
        )

        self.add_cipher_output_component(
            [final_permutation.id],
            [list(range(self.cipher_block_size))],
            self.cipher_block_size
        )