import tkinter as tk
from tkinter import messagebox
import sounddevice as sd
from scipy.io.wavfile import write, read
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import os # Importado para garantir a criação do diretório


class EnviaSinal:
    def __init__(self, root):
        self.root = tk.Toplevel(root)
        self.root.title("Enviar Sinal")

        self.fs = 44100 # Taxa de amostragem
        # Garante que o diretório para salvar os arquivos exista
        self.assests_dir = "src/assents"
        os.makedirs(self.assests_dir, exist_ok=True)
        self.arquivo_audio = os.path.join(self.assests_dir, "enviarAudio.wav")
        self.arquivo_modulado = os.path.join(self.assests_dir, "modulated.wav")

        self.is_recording = False
        self.audio_frames = []

        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=10)

        self.btn_gravar = tk.Button(btn_frame, text="Gravar", font=("Arial", 14), command=self.iniciar_gravacao)
        self.btn_gravar.pack(side=tk.LEFT, padx=5)

        self.btn_parar = tk.Button(btn_frame, text="Parar", font=("Arial", 14), command=self.parar_gravacao, state=tk.DISABLED)
        self.btn_parar.pack(side=tk.LEFT, padx=5)

        # O figsize precisa ser ajustado para gráficos um abaixo do outro.
        # Aumentamos a altura (8) em relação à largura (6) para acomodar melhor 3 plots verticais.
        self.fig = plt.Figure(figsize=(6, 8))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas.get_tk_widget().pack()

        self.stream = None

    def callback(self, indata, frames, time, status):
        """Callback para a gravação de áudio em tempo real."""
        if status:
            print(status) # Imprime mensagens de status, se houver
        self.audio_frames.append(indata.copy())

    def iniciar_gravacao(self):
        """Inicia a gravação de áudio."""
        if self.is_recording:
            return
        self.audio_frames = []
        self.is_recording = True
        self.btn_gravar.config(state=tk.DISABLED)
        self.btn_parar.config(state=tk.NORMAL)
        try:
            self.stream = sd.InputStream(samplerate=self.fs, channels=1, callback=self.callback)
            self.stream.start()
            messagebox.showinfo("Gravando", "Gravação iniciada! Fale agora...")
        except Exception as e:
            messagebox.showerror("Erro de Gravação", f"Não foi possível iniciar a gravação: {e}\nVerifique seu microfone e drivers de áudio.")
            self.is_recording = False
            self.btn_gravar.config(state=tk.NORMAL)
            self.btn_parar.config(state=tk.DISABLED)


    def parar_gravacao(self):
        """Para a gravação de áudio, salva e plota os sinais."""
        if not self.is_recording:
            return
        self.is_recording = False
        self.btn_gravar.config(state=tk.NORMAL)
        self.btn_parar.config(state=tk.DISABLED)

        if self.stream: # Garante que o stream existe antes de tentar pará-lo
            self.stream.stop()
            self.stream.close()
            self.stream = None
        else:
            messagebox.showwarning("Aviso", "Nenhuma gravação ativa para parar.")
            return

        if not self.audio_frames:
            messagebox.showwarning("Aviso", "Nenhum dado de áudio foi gravado.")
            return

        audio_data = np.concatenate(self.audio_frames, axis=0)
        audio_data = audio_data.flatten()

        # Normaliza o áudio para o intervalo [-1, 1] para evitar clipping
        # e garantir que a modulação AM seja feita sem sobremodulação indesejada.
        max_abs_audio = np.max(np.abs(audio_data))
        if max_abs_audio > 0:
            audio_data_norm = audio_data / max_abs_audio
        else:
            audio_data_norm = audio_data # Evita divisão por zero se o áudio for silêncio

        audio_data_int16 = np.int16(audio_data_norm * 32767) # Converte para int16 para salvar
        write(self.arquivo_audio, self.fs, audio_data_int16)
        messagebox.showinfo("Sucesso", f"Áudio salvo como {self.arquivo_audio}")
        
        # Passa o áudio normalizado para a função de plotagem e modulação
        self.plotar_audio_e_modulado(audio_data_norm)

    def plotar_audio_e_modulado(self, audio_data):
        """Modula o áudio gravado e plota o áudio original, a portadora e o sinal modulado."""
        try:
            t = np.linspace(0, len(audio_data) / self.fs, len(audio_data), endpoint=False) # Usar endpoint=False para evitar um ponto extra se len for exato
            fc = 10000  # Frequência da portadora: 10 kHz
            carrier = np.sin(2 * np.pi * fc * t)

            # Implementação da Modulação de Amplitude (AM)
            # A amplitude do sinal de mensagem (audio_data) deve estar entre -1 e 1
            # para que (1 + audio_data) esteja entre 0 e 2, evitando sobremodulação.
            # Assumimos que audio_data já está normalizado para [-1, 1] vindo de parar_gravacao.
            modulated = (1 + audio_data) * carrier

            # Normaliza o sinal modulado para o máximo absoluto antes de salvar
            max_abs_modulated = np.max(np.abs(modulated))
            if max_abs_modulated > 0:
                modulated_norm = modulated / max_abs_modulated
            else:
                modulated_norm = modulated

            modulated_int16 = np.int16(modulated_norm * 32767) # Converte para int16
            write(self.arquivo_modulado, self.fs, modulated_int16) # Salva o sinal modulado

            self.fig.clear() # Limpa a figura para desenhar novos gráficos

            # MODIFICAÇÃO AQUI: Criar 3 subplots em 3 linhas e 1 coluna
            ax1 = self.fig.add_subplot(3, 1, 1) # 3 linhas, 1 coluna, primeiro subplot
            ax1.plot(t, audio_data)
            ax1.set_title("Áudio (Mensagem)")
            ax1.set_xlabel("Tempo (s)")
            ax1.set_ylabel("Amplitude")
            ax1.set_ylim([-1.1, 1.1]) # Define limites Y consistentes

            ax2 = self.fig.add_subplot(3, 1, 2) # 3 linhas, 1 coluna, segundo subplot
            ax2.plot(t, carrier)
            ax2.set_title("Sinal Portadora")
            ax2.set_xlabel("Tempo (s)")
            ax2.set_ylabel("Amplitude")
            ax2.set_ylim([-1.1, 1.1]) # Define limites Y consistentes

            ax3 = self.fig.add_subplot(3, 1, 3) # 3 linhas, 1 coluna, terceiro subplot
            ax3.plot(t, modulated)
            ax3.set_title("Sinal Modulado AM")
            ax3.set_xlabel("Tempo (s)")
            ax3.set_ylabel("Amplitude")
            # Para o sinal modulado, os limites Y devem acomodar (1 + audio_data) * carrier
            # Se audio_data está em [-1, 1], então (1 + audio_data) está em [0, 2],
            # então o sinal modulado pode variar entre [-2, 2].
            ax3.set_ylim([-2.2, 2.2])

            self.fig.tight_layout()  # Ajusta os espaçamentos entre os subplots para melhor visualização
            self.canvas.draw() # Desenha a figura no canvas do Tkinter

        except Exception as e:
            messagebox.showerror("Erro", str(e))