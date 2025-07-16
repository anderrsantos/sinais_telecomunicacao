import tkinter as tk
from tkinter import messagebox
#import sounddevice as sd
from scipy.io.wavfile import write, read
import numpy as np
#import matplotlib.pyplot as plt
#from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from src.interface.enviarSinal import  EnviaSinal
from src.interface.receberSinal import  RecebeSinal

class Main:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Sistema de Sinais - Enviar e Receber")

        # Aumentando o pady e adicionando padx para o rótulo
        label = tk.Label(self.root, text="Escolha uma opção:", font=("Arial", 16))
        label.pack(pady=30, padx=50) # Aumentado pady e adicionado padx para as laterais

        # Aumentando o pady e adicionando padx para os botões
        btn_enviar = tk.Button(self.root, text="Enviar Sinal", font=("Arial", 14), width=20, command=self.abrir_envia_sinal)
        btn_enviar.pack(pady=15, padx=50) # Aumentado pady e adicionado padx para as laterais

        btn_receber = tk.Button(self.root, text="Receber Sinal", font=("Arial", 14), width=20, command=self.abrir_recebe_sinal)
        btn_receber.pack(pady=15, padx=50) # Aumentado pady e adicionado padx para as laterais

    def abrir_envia_sinal(self):
        EnviaSinal(self.root)

    def abrir_recebe_sinal(self):
        RecebeSinal(self.root)

    def run(self):
        self.root.mainloop()

# Para testar a classe Main (opcional, se você quiser executar este arquivo diretamente)
# if __name__ == "__main__":
#     app = Main()
#     app.run()