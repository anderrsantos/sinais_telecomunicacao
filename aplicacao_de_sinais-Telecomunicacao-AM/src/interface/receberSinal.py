import tkinter as tk
from tkinter import messagebox
import sounddevice as sd
from scipy.io.wavfile import write, read
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from scipy.signal import butter, filtfilt
import os


class RecebeSinal:
    def __init__(self, root):
        self.root = tk.Toplevel(root)
        self.root.title("Receber Sinal")

        self.fs = 44100
        self.arquivo_modulado = "src/assents/modulated.wav"

        label = tk.Label(self.root, text="Receber e Demodular Sinal", font=("Arial", 14))
        label.pack(padx=20, pady=10)

        btn_receber = tk.Button(self.root, text="Receber (Demodular) o sinal", font=("Arial", 12), command=self.demodular_sinal)
        btn_receber.pack(pady=5)

        btn_ouvir = tk.Button(self.root, text="▶ Ouvir Demodulado", font=("Arial", 12), command=self.ouvir_sinal)
        btn_ouvir.pack(pady=5)

        self.fig = plt.Figure(figsize=(8, 6))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas.get_tk_widget().pack()



    def demodular_sinal(self):
        try:
            fs, data = read(self.arquivo_modulado)
            if data.dtype == np.int16:
                data = data.astype(np.float32) / 32768.0

            envelope = np.abs(data)
            sinal_demodulado = self.filtra_passa_baixa(envelope, cutoff=1500, fs=fs, ordem=10)

            max_val = np.max(np.abs(sinal_demodulado))
            if max_val > 0:
                sinal_demodulado_norm = sinal_demodulado / max_val
            else:
                sinal_demodulado_norm = sinal_demodulado

            os.makedirs("src/assents", exist_ok=True)
            sinal_int16 = np.int16(sinal_demodulado_norm * 32767)
            write("src/assents/demodulado.wav", fs, sinal_int16)

            t = np.linspace(0, len(data) / fs, len(data))

            self.fig.clear()
            axs = self.fig.subplots(3, 1)

            axs[0].plot(t, data)
            axs[0].set_title("Sinal Modulado")
            axs[0].set_xlabel("Tempo [s]")
            axs[0].set_ylabel("Amplitude")

            axs[1].plot(t, sinal_demodulado_norm)
            axs[1].set_title("Envelope Demodulado e Filtrado")
            axs[1].set_xlabel("Tempo [s]")
            axs[1].set_ylabel("Amplitude")

            try:
                fs2, existente = read("src/assents/enviarAudio.wav")
                if existente.dtype == np.int16:
                    existente = existente.astype(np.float32) / 32768.0
                t2 = np.linspace(0, len(existente) / fs2, len(existente))
                axs[2].plot(t2, existente)
                axs[2].set_title("Sinal Original de Referência")
                axs[2].set_xlabel("Tempo [s]")
                axs[2].set_ylabel("Amplitude")
            except FileNotFoundError:
                axs[2].text(0.5, 0.5, "Arquivo 'enviarAudio.wav' não disponível", ha='center', va='center', transform=axs[2].transAxes)
                axs[2].set_title("Sinal Original de Referência")
                axs[2].set_xlabel("Tempo [s]")
                axs[2].set_ylabel("Amplitude")
            except Exception as e:
                axs[2].text(0.5, 0.5, f"Erro ao carregar 'enviarAudio.wav':\n{e}", ha='center', va='center', transform=axs[2].transAxes)
                axs[2].set_title("Sinal Original de Referência")
                axs[2].set_xlabel("Tempo [s]")
                axs[2].set_ylabel("Amplitude")


            self.fig.tight_layout() # Added to improve spacing
            self.canvas.draw()
            #messagebox.showinfo("Sucesso", "Sinal demodulado e salvo com sucesso!")

        except FileNotFoundError:
            messagebox.showerror("Erro", f"Arquivo '{self.arquivo_modulado}' não encontrado. Certifique-se de que o arquivo esteja no caminho correto.")
        except Exception as e:
            messagebox.showerror("Erro", str(e))

    def ouvir_sinal(self):
        try:
            fs, data = read("src/assents/demodulado.wav")
            if data.dtype == np.int16:
                data = data.astype(np.float32) / 32768.0
            sd.play(data, fs)
            sd.wait()
        except FileNotFoundError:
            messagebox.showerror("Erro ao reproduzir", "Arquivo 'demodulado.wav' não encontrado. Demodule o sinal primeiro.")
        except Exception as e:
            messagebox.showerror("Erro ao reproduzir", str(e))

    @staticmethod
    def filtra_passa_baixa(signal, cutoff=1500, fs=44100, ordem=10):
        nyquist = 0.5 * fs
        normal_cutoff = cutoff / nyquist
        # Ensure that the normalized cutoff frequency is within (0, 1)
        if not (0 < normal_cutoff < 1):
            raise ValueError(f"Cutoff frequency {cutoff} Hz is too high for sampling rate {fs} Hz. "
                             "Please choose a cutoff frequency less than Nyquist frequency (fs/2).")
        b, a = butter(ordem, normal_cutoff, btype='low')
        return filtfilt(b, a, signal)