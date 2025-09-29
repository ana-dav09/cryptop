from claasp.cipher import Cipher
from claasp.name_mappings import INPUT_KEY, INPUT_PLAINTEXT

PARAMETERS_CONFIGURATION_LIST = [{'word_size': 4, 'state_size' : 2, 'number_of_rounds': 3}]

class BabyAESCipher(Cipher):

    def __init__(self, number_of_rounds = 3, word_size=4, state_size=2):
        if word_size not in [4]:
            raise ValueError("word_size incorrect (should be 4)")
        if state_size not in [2]: 
            raise ValueError("state_size incorrect (should be 2)")
        
        #cipher dictionary initialize
        self.CIPHER_BLOCK_SIZE = state_size ** 2 * word_size
        self.KEY_BLOCK_SIZE = self.CIPHER_BLOCK_SIZE
        self.NROUNDS = number_of_rounds
        self.SBOX_BIT_SIZE = word_size
        self.NUM_SBOXES = state_size ** 2
        self.NUM_ROWS = state_size
        self.ROW_SIZE = state_size * word_size

        super().__init__(family_name="baby_aes_block_cipher",
                         cipher_type="block_cipher",
                         cipher_inputs=[INPUT_KEY, INPUT_PLAINTEXT],
                         cipher_inputs_bit_size=[self.KEY_BLOCK_SIZE, self.CIPHER_BLOCK_SIZE],
                         cipher_output_bit_size=self.CIPHER_BLOCK_SIZE)
        
        self.sbox = [ 0x06, 0x0b, 0x05, 0x04, 0x02, 0x0e, 0x07, 0x0a,
                      0x09, 0x0d, 0x0f, 0x0c, 0x03, 0x01, 0x00, 0x08]
        
        self.AES_matrix = [[0x03, 0x02], [0x02, 0x03]]

        self.irreducible_polynomial = 0x13

        self.ROUND_CONSTANT = [
                "0x1000", "0x2000", "0x4000", "0x8000", "0x3000", "0x6000", "0xc000", "0xb000",
                "0x5000", "0xa000", "0x7000", "0xe000", "0xf000", "0xd000", "0x9000", "0x1000",
            ]

        self.AES_matrix_description = [self.AES_matrix, self.irreducible_polynomial, word_size]

        #Rounds definition
        #Round 0
        self.add_round()
        first_add_round_key = self.add_XOR_component([INPUT_KEY, INPUT_PLAINTEXT],
                                                     [[i for i in range(self.KEY_BLOCK_SIZE)],
                                                     [i for i in range(self.CIPHER_BLOCK_SIZE)]],
                                                     int(self.CIPHER_BLOCK_SIZE))
        add_round_key = None
        remaining_xors = None
        xor1 = None
        for round_number in range(number_of_rounds):
            sbox_components = self.create_sbox_components(add_round_key, first_add_round_key, round_number)
            shift_rows_components = self.create_shift_rows_components(sbox_components, word_size)
            mix_columns_components = self.create_mix_columns_components(shift_rows_components, round_number)
            key_rotation = self.create_rotate_component(remaining_xors, round_number, word_size)
            key_sboxes_components = self.create_key_sbox_components(key_rotation)
            constant = self.create_constant_component(round_number)
            remaining_xors, xor1 = self.create_xor_components(constant, key_sboxes_components,
                                                              remaining_xors, xor1, round_number)
            self.add_intermediate_output_component([remaining_xors[i].id for i in range(self.NUM_ROWS)],
                                                   [[i for i in range(self.ROW_SIZE)] for _ in range(self.NUM_ROWS)],
                                                   self.KEY_BLOCK_SIZE,
                                                   "round_key_output")


            add_round_key = self.create_round_key(mix_columns_components, remaining_xors, round_number, shift_rows_components)
            self.create_round_output_component(add_round_key, number_of_rounds, round_number)
    
    def create_sbox_components(self, add_round_key, first_add_round_key, round_number):
        sbox_components = []
        for j in range(self.NUM_SBOXES):
            if round_number == 0:
                sbox = self.add_SBOX_component(
                    [first_add_round_key.id],
                    [[i for i in range(j * self.SBOX_BIT_SIZE, (j+1) * self.SBOX_BIT_SIZE)]],
                    self.SBOX_BIT_SIZE, self.sbox
                )
            else:
                sbox = self.add_SBOX_component(
                    [add_round_key.id],
                    [[i for i in range(j * self.SBOX_BIT_SIZE, (j+1) * self.SBOX_BIT_SIZE)]],
                    self.SBOX_BIT_SIZE, self.sbox
                )
            sbox_components.append(sbox)
        return sbox_components

    def create_shift_rows_components(self, sbox_components, word_size):
        shift_rows_components = []
        for j in range(self.NUM_ROWS):
            rotation = self.add_rotate_component(
                [sbox_components[i].id for i in range (j, j + self.NUM_ROWS * (self.NUM_ROWS - 1) + 1, self.NUM_ROWS)],
                [[i for i in range(self.SBOX_BIT_SIZE)] for _ in range (self.NUM_ROWS)],
                self.ROW_SIZE,
                -word_size * j
            )
            shift_rows_components.append(rotation)
        
        return shift_rows_components

    def create_mix_columns_components(self, shift_rows_components, round_number):
        mix_column_components = []
        if round_number != self.NROUNDS - 1:
            for j in range(self.NUM_ROWS):
                mix_column = self.add_mix_column_component(
                    [shift_rows_components[i].id for i in range(self.NUM_ROWS)],
                    [[i for i in range(j * self.SBOX_BIT_SIZE, (j + 1) * self.SBOX_BIT_SIZE)] for _ in
                     range(self.NUM_ROWS)],
                    self.ROW_SIZE,
                    self.AES_matrix_description)
                mix_column_components.append(mix_column)

        return mix_column_components
    
    def create_rotate_component(self, remaining_xors, round_number, word_size):
        if round_number == 0:
            key_rotation = self.add_rotate_component(
                [INPUT_KEY],
                [[i for i in range(self.KEY_BLOCK_SIZE - self.ROW_SIZE, self.KEY_BLOCK_SIZE)]],
                self.ROW_SIZE,
                -word_size)
        else:
            key_rotation = self.add_rotate_component(
                [remaining_xors[self.NUM_ROWS - 1].id],
                [[i for i in range(self.ROW_SIZE)]],
                self.ROW_SIZE,
                -word_size)

        return key_rotation

    def create_key_sbox_components(self, key_rotation):
        key_sboxes_components = []
        for i in range(self.NUM_ROWS):
            key_sub = self.add_SBOX_component(
                [key_rotation.id],
                [[j for j in range(i * self.SBOX_BIT_SIZE, (i + 1) * self.SBOX_BIT_SIZE)]],
                self.SBOX_BIT_SIZE,
                self.sbox)
            key_sboxes_components.append(key_sub)

        return key_sboxes_components

    def create_constant_component(self, round_number):
        constant = self.add_constant_component(self.ROW_SIZE, int(self.ROUND_CONSTANT[round_number], 16))
    
        return constant

    def create_xor_components(self, constant, key_sboxes_components, remaining_xors, xor1, round_number):
        if round_number == 0:
            xor1 = self.add_XOR_component(
                [key_sboxes_components[i].id for i in range(self.NUM_ROWS)] + [constant.id, INPUT_KEY],
                [[i for i in range(self.SBOX_BIT_SIZE)] for _ in range(self.NUM_ROWS)] + [
                    [i for i in range(self.ROW_SIZE)] for _ in range(2)],
                self.ROW_SIZE)
        else:
            xor1 = self.add_XOR_component(
                [key_sboxes_components[i].id for i in range(self.NUM_ROWS)] + [constant.id, xor1.id],
                [[i for i in range(self.SBOX_BIT_SIZE)] for _ in range(self.NUM_ROWS)] + [
                    [i for i in range(self.ROW_SIZE)] for _ in range(2)],
                self.ROW_SIZE)
        tmp_remaining_xors = [xor1]
        for i in range(self.NUM_ROWS - 1):
            if round_number == 0:
                xor = self.add_XOR_component(
                    [tmp_remaining_xors[i].id, INPUT_KEY],
                    [[i for i in range(self.ROW_SIZE)],
                     [i for i in range((i + 1) * self.ROW_SIZE, (i + 2) * self.ROW_SIZE)]],
                    self.ROW_SIZE)
            else:
                xor = self.add_XOR_component(
                    [tmp_remaining_xors[i].id, remaining_xors[i + 1].id],
                    [[i for i in range(self.ROW_SIZE)], [i for i in range(self.ROW_SIZE)]],
                    self.ROW_SIZE)
            tmp_remaining_xors.append(xor)
        remaining_xors = list(tmp_remaining_xors)

        return remaining_xors, xor1

    def create_round_key(self, mix_column_components, remaining_xors, round_number, shift_row_components):
        if round_number != self.NROUNDS - 1:
            add_round_key = self.add_XOR_component(
                [mix_column_components[i].id for i in range(self.NUM_ROWS)] + [remaining_xors[i].id for i in
                                                                               range(self.NUM_ROWS)],
                [[i for i in range(self.ROW_SIZE)] for _ in range(2 * self.NUM_ROWS)],
                self.CIPHER_BLOCK_SIZE)
        else:
            shift_rows_ids = []
            for i in range(self.NUM_ROWS):
                shift_rows_ids.extend([shift_row_components[j].id for j in range(self.NUM_ROWS)])
            shift_rows_input_position_lists = []
            for i in range(self.NUM_ROWS):
                shift_rows_input_position_lists.extend(
                    [[j for j in range(i * self.SBOX_BIT_SIZE, (i + 1) * self.SBOX_BIT_SIZE)] for _ in
                     range(self.NUM_ROWS)])
            add_round_key = self.add_XOR_component(
                shift_rows_ids + [remaining_xors[i].id for i in range(self.NUM_ROWS)],
                shift_rows_input_position_lists + [[i for i in range(self.ROW_SIZE)] for _ in range(self.NUM_ROWS)],
                self.CIPHER_BLOCK_SIZE)

        return add_round_key

    def create_round_output_component(self, add_round_key, number_of_rounds, round_number):
        if round_number == number_of_rounds - 1:
            self.add_cipher_output_component([add_round_key.id],
                                             [[i for i in range(self.CIPHER_BLOCK_SIZE)]],
                                             self.CIPHER_BLOCK_SIZE)
        else:
            self.add_intermediate_output_component([add_round_key.id],
                                                   [[i for i in range(self.CIPHER_BLOCK_SIZE)]],
                                                   self.CIPHER_BLOCK_SIZE,
                                                   "round_output")
            self.add_round()