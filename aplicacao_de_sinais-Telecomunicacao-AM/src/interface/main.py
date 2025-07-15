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

        label = tk.Label(self.root, text="Escolha uma opção:", font=("Arial", 16))
        label.pack(pady=20)

        btn_enviar = tk.Button(self.root, text="Enviar Sinal", font=("Arial", 14), width=20, command=self.abrir_envia_sinal)
        btn_enviar.pack(pady=10)

        btn_receber = tk.Button(self.root, text="Receber Sinal", font=("Arial", 14), width=20, command=self.abrir_recebe_sinal)
        btn_receber.pack(pady=10)

    def abrir_envia_sinal(self):
        EnviaSinal(self.root)

    def abrir_recebe_sinal(self):
        RecebeSinal(self.root)

    def run(self):
        self.root.mainloop()