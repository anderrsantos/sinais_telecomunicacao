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

        self.fs = 44100 # Garanta que esta taxa de amostragem seja a mesma do EnviaSinal!
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

        btn_fechar = tk.Button(self.root, text="Fechar", command=self.root.destroy)
        btn_fechar.pack(pady=10)

    def demodular_sinal(self):
        try:
            fs, data = read(self.arquivo_modulado)
            if data.dtype == np.int16:
                data = data.astype(np.float32) / 32768.0

            envelope = np.abs(data)

            # --- FOCO AQUI PARA REMOVER O ZUMBIDO ---
            # Ajustar cutoff e ordem para melhor filtragem da portadora
            # Se a voz foi filtrada em 4000 Hz na modulação (EnviaSinal),
            # o cutoff aqui deve ser 4000 Hz ou um pouco acima, mas ainda bem abaixo da portadora (10kHz).
            # Aumentar a ordem para uma atenuação mais forte.
            sinal_demodulado = self.filtra_passa_baixa(envelope, cutoff=4000, fs=fs, ordem=20) # Ajustado aqui
            # Experimente:
            # - cutoff=3500, ordem=20
            # - cutoff=4000, ordem=25
            # - cutoff=3800, ordem=25 (uma boa combinação)


            max_val = np.max(np.abs(sinal_demodulado))
            if max_val > 0:
                sinal_demodulado_norm = sinal_demodulado / max_val
            else:
                sinal_demodulado_norm = sinal_demodulado

            os.makedirs("src/assents", exist_ok=True)
            sinal_int16 = np.int16(sinal_demodulado_norm * 32767)
            write("src/assents/demodulado.wav", fs, sinal_int16)

            # Ajusta o tempo para o zoom nas plots
            t = np.linspace(0, len(data) / fs, len(data), endpoint=False)


            self.fig.clear()
            axs = self.fig.subplots(3, 1)

            axs[0].plot(t, data)
            axs[0].set_title("Sinal Modulado")
            axs[0].set_xlabel("Tempo [s]")
            axs[0].set_ylabel("Amplitude")
            axs[0].set_xlim([0, 0.1])
            axs[0].set_ylim([-1.1, 1.1])


            axs[1].plot(t, sinal_demodulado_norm)
            axs[1].set_title("Envelope Demodulado e Filtrado")
            axs[1].set_xlabel("Tempo [s]")
            axs[1].set_ylabel("Amplitude")
            axs[1].set_xlim([0, 0.1])
            axs[1].set_ylim([-1.1, 1.1])


            try:
                fs2, existente = read("src/assents/enviarAudio.wav")
                if existente.dtype == np.int16:
                    existente = existente.astype(np.float32) / 32768.0

                max_val_existente = np.max(np.abs(existente))
                if max_val_existente > 0:
                    existente_norm = existente / max_val_existente
                else:
                    existente_norm = existente

                t2 = np.linspace(0, len(existente) / fs2, len(existente), endpoint=False)
                axs[2].plot(t2, existente_norm)
                axs[2].set_title("Sinal Original de Referência (Normalizado)")
                axs[2].set_xlabel("Tempo [s]")
                axs[2].set_ylabel("Amplitude")
                axs[2].set_xlim([0, 0.1])
                axs[2].set_ylim([-1.1, 1.1])
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


            self.fig.tight_layout()
            self.canvas.draw()
            messagebox.showinfo("Sucesso", "Sinal demodulado e salvo com sucesso!")

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
    def filtra_passa_baixa(signal, cutoff, fs, ordem=10):
        """
        Aplica um filtro passa-baixa Butterworth a um sinal.

        Args:
            signal (array_like): O sinal de entrada a ser filtrado.
            cutoff (float): A frequência de corte do filtro em Hz.
            fs (float): A taxa de amostragem do sinal em Hz.
            ordem (int, optional): A ordem do filtro. Padrão é 10.

        Returns:
            array_like: O sinal filtrado.

        Raises:
            ValueError: Se a frequência de corte for muito alta para a taxa de amostragem.
        """
        nyquist = 0.5 * fs  # Frequência de Nyquist (metade da taxa de amostragem)
        normal_cutoff = cutoff / nyquist # Frequência de corte normalizada (entre 0 e 1)

        # Garante que a frequência de corte normalizada esteja dentro do intervalo válido (0, 1)
        if not (0 < normal_cutoff < 1):
            raise ValueError(f"A frequência de corte {cutoff} Hz é muito alta para a taxa de amostragem {fs} Hz. "
                             "Por favor, escolha uma frequência de corte menor que a frequência de Nyquist (fs/2).")

        # Projeta o filtro Butterworth (coeficientes 'b' e 'a')
        b, a = butter(ordem, normal_cutoff, btype='low')

        # Aplica o filtro ao sinal usando filtfilt para fase zero (sem atraso de fase)
        return filtfilt(b, a, signal)