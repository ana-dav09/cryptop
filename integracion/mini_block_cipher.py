from claasp.cipher import Cipher
from claasp.name_mappings import INPUT_KEY, INPUT_PLAINTEXT, BLOCK_CIPHER
import math

class MiniBlockCipher(Cipher):

    def __init__(self):

        # Set the default values
        self.cipher_block_size = 8
        self.key_block_size = 16
        self.nrounds = 4
        self.sbox = [0x0e, 0x04, 0x0d, 0x01, 0x02, 0x0f, 0x0b, 0x08, 0x03, 0x0a, 0x06, 0x0c, 0x05, 0x09, 0x00, 0x07]
        # Permutation equivalent to [5, 2, 6, 0, 7, 1, 4, 3] described in the paper
        self.permutation = [4, 3, 6, 0, 7, 1, 5, 2]
        self.sbox_size = 4
        self.add_round_constant = True
        self.final_xor = True

        super().__init__(
            family_name="mini_block_cipher",
            cipher_type=BLOCK_CIPHER,
            cipher_inputs=[INPUT_KEY, INPUT_PLAINTEXT],
            cipher_inputs_bit_size=[self.key_block_size, self.cipher_block_size],
            cipher_output_bit_size=self.cipher_block_size,
        )

    def set_parameters(self, number_of_rounds: int = None, sbox: list = None, permutation: list = None, final_xor: bool = None, add_round_constant: bool = None):
        if number_of_rounds is not None:
            self.nrounds = number_of_rounds
        if sbox is not None and len(sbox) in [2, 4, 16, 256]:
            self.sbox = sbox
            self.sbox_size = int(math.log2(len(sbox)))
        if permutation is not None and len(permutation) == self.cipher_block_size:
            self.permutation = permutation
        if final_xor is not None:
            self.final_xor = final_xor
        if add_round_constant is not None:
            self.add_round_constant = add_round_constant

    def build_cipher(self):
        # Build the cipher rounds definition
        last_key_component = None
        first_key_component = None
        round_output_component = None
        for round in range(self.nrounds):
            self.add_round()
            # Key schedule
            round_key_component = self.key_schedule(round, last_key_component, first_key_component)
            add_round_key_component = None

            # Add the round key component tracking variables
            if round == 0:
                first_key_component = round_key_component
                add_round_key_component = self.add_XOR_component(
                    [INPUT_PLAINTEXT] + [round_key_component.id],
                    [list(range(self.cipher_block_size))] + [list(range(self.cipher_block_size))],
                    self.cipher_block_size,
                )
            else:
                last_key_component = round_key_component
                add_round_key_component = self.add_XOR_component(
                    [round_output_component.id] + [round_key_component.id],
                    [list(range(self.cipher_block_size))] + [list(range(self.cipher_block_size))],
                    self.cipher_block_size,
                )

            # Apply S-box
            sboxes_components = []
            for i in range(self.cipher_block_size // self.sbox_size):
                sbox_component = self.add_SBOX_component(
                    [add_round_key_component.id],
                    [list(range(i*self.sbox_size, (i+1)*self.sbox_size))],
                    self.sbox_size,
                    self.sbox,
                )
                sboxes_components.append(sbox_component)
            
            # Combine S-box outputs
            sbox_output_component = self.add_rotate_component(
                [sboxes_components[i].id for i in range(len(sboxes_components))],
                [[i for i in range(self.sbox_size)] for _ in range(len(sboxes_components))],
                self.cipher_block_size,
                0
            )

            permutation_component = self.add_permutation_component(
                [sbox_output_component.id],
                [self.permutation],
                self.cipher_block_size,
                list(range(self.cipher_block_size)),
            )

            if self.add_round_constant:
                # Add round constant
                round_constant_component = self.add_constant_component(
                    self.cipher_block_size,
                    round + 1,
                )

                round_output_component = self.add_MODADD_component(
                    [permutation_component.id] + [round_constant_component.id],
                    [list(range(self.cipher_block_size))] + [list(range(self.cipher_block_size))],
                    self.cipher_block_size,
                    256,
                )
            else:
                round_output_component = permutation_component

        cipher_output_component = None
        if self.final_xor:
            cipher_output_component = self.add_XOR_component(
                [round_output_component.id] + [first_key_component.id],
                [list(range(self.cipher_block_size))] + [list(range(self.cipher_block_size))],
                self.cipher_block_size,
            )
        else:
            cipher_output_component = round_output_component

        self.add_cipher_output_component(
            [cipher_output_component.id],
            [list(range(self.cipher_block_size))],
            self.cipher_block_size,
        )

    def key_schedule(self, round: int, last_key_component = None, first_key_component = None):
        match round:
            case 0:
                return self.add_rotate_component(
                    [INPUT_KEY],
                    [list(range(self.cipher_block_size, self.key_block_size))],
                    self.cipher_block_size,
                    0,
                )
            case 1:
                return self.add_rotate_component(
                    [INPUT_KEY],
                    [list(range(self.cipher_block_size))],
                    self.cipher_block_size,
                    0,  
                )
            case 2:
                return self.add_XOR_component(
                    [first_key_component.id] + [last_key_component.id],
                    [list(range(self.cipher_block_size))] + [list(range(self.cipher_block_size))],
                    self.cipher_block_size,
                )
            case 3:
                return self.add_rotate_component(
                    [first_key_component.id],
                    [list(range(self.cipher_block_size))],
                    self.cipher_block_size,
                    -3,
                )
            case _:
                # Here comes the algorithm when there are more than 4 rounds
                # For now, raise an error
                raise ValueError(f"Invalid round number: {round}")


    def get_dict(self):
        return {
            "cipher_block_size": self.cipher_block_size,
            "key_block_size": self.key_block_size,
            "nrounds": self.nrounds,
            "sbox": self.sbox,
            "permutation": self.permutation,
            "sbox_size": self.sbox_size,
            "final_xor": self.final_xor,
        }



