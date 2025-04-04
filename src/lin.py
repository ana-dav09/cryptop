import sys
import random
from itertools import product
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QPushButton, QSpinBox, QTextEdit

class ReducedAES:
    def __init__(self, num_rounds, key):
        self.num_rounds = num_rounds
        self.key = key  # Lista de claves de ronda
        self.sbox = [
            0x63, 0x7C, 0x77, 0x7B, 0xF2, 0x6B, 0x6F, 0xC5, 0x30, 0x01, 0x67, 0x2B, 0xFE, 0xD7, 0xAB, 0x76,
            0xCA, 0x82, 0xC9, 0x7D, 0xFA, 0x59, 0x47, 0xF0, 0xAD, 0xD4, 0xA2, 0xAF, 0x9C, 0xA4, 0x72, 0xC0,
        ]
        self.pbox = [0, 4, 8, 12, 1, 5, 9, 13, 2, 6, 10, 14, 3, 7, 11, 15]
    
    def encrypt(self, plaintext):
        state = plaintext
        for round in range(self.num_rounds):
            state ^= self.key[round]  # XOR con clave de ronda
            state = self._substitute(state)
            state = self._permute(state)
        return state ^ self.key[-1]  # Última XOR con clave final

    def _substitute(self, state):
        return (self.sbox[(state >> 12) & 0xF] << 12) | (self.sbox[(state >> 8) & 0xF] << 8) | \
               (self.sbox[(state >> 4) & 0xF] << 4) | (self.sbox[state & 0xF])

    def _permute(self, state):
        result = 0
        for i in range(16):
            bit = (state >> i) & 1
            result |= bit << self.pbox[i]
        return result

def linear_approximation(cipher, input_mask, output_mask, num_samples):
    count = 0
    for _ in range(num_samples):
        plaintext = random.randint(0, 65535)
        ciphertext = cipher.encrypt(plaintext)
        input_parity = bin(plaintext & input_mask).count('1') % 2
        output_parity = bin(ciphertext & output_mask).count('1') % 2
        if input_parity == output_parity:
            count += 1
    return (count / num_samples) - 0.5

def linear_attack(cipher, num_samples):
    input_masks = [0x1, 0x2, 0x4, 0x8, 0x10, 0x20, 0x40, 0x80]
    output_masks = [0x1, 0x2, 0x4, 0x8, 0x10, 0x20, 0x40, 0x80]
    bias_table = {}
    
    for input_mask, output_mask in product(input_masks, output_masks):
        bias = linear_approximation(cipher, input_mask, output_mask, num_samples)
        bias_table[(input_mask, output_mask)] = bias
    
    print("Tabla de sesgo calculada:")
    for (input_mask, output_mask), bias in bias_table.items():
        print(f"Máscara entrada: {input_mask:016b}, Máscara salida: {output_mask:016b}, Sesgo: {bias:.6f}")
    
    recovered_key = 0
    for bit in range(16):
        best_mask = max(bias_table.items(), key=lambda x: abs(x[1]))[0]
        if bias_table[best_mask] > 0:
            recovered_key |= (1 << bit)
    return recovered_key

class CryptoAnalysisApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
    
    def initUI(self):
        self.setWindowTitle("Criptoanálisis Lineal - AES Reducido")
        self.setGeometry(100, 100, 600, 400)
        layout = QVBoxLayout()
        self.rounds_spinbox = QSpinBox()
        self.rounds_spinbox.setRange(1, 10)
        self.rounds_spinbox.setValue(2)
        self.samples_spinbox = QSpinBox()
        self.samples_spinbox.setRange(100, 100000)
        self.samples_spinbox.setValue(10000)
        self.run_button = QPushButton("Ejecutar Criptoanálisis")
        self.run_button.clicked.connect(self.run_cryptoanalysis)
        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        layout.addWidget(QLabel("Número de rondas:"))
        layout.addWidget(self.rounds_spinbox)
        layout.addWidget(QLabel("Número de muestras:"))
        layout.addWidget(self.samples_spinbox)
        layout.addWidget(self.run_button)
        layout.addWidget(self.result_text)
        self.setLayout(layout)
    
    def run_cryptoanalysis(self):
        num_rounds = self.rounds_spinbox.value()
        num_samples = self.samples_spinbox.value()
        key = [random.randint(0, 65535) for _ in range(num_rounds + 1)]
        cipher = ReducedAES(num_rounds, key)
        recovered_key = linear_attack(cipher, num_samples)
        result = f"Clave real: {[f'{k:016b}' for k in key]}\n"
        result += f"Clave recuperada: {recovered_key:016b}\n"
        self.result_text.setText(result)
        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CryptoAnalysisApp()
    window.show()
    sys.exit(app.exec())
