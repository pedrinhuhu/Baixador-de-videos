import os
import threading
import tkinter as tk
from tkinter import messagebox, filedialog, ttk
import yt_dlp


'''Função de callback de progresso'''
def hook(d):
    if d['status'] == 'downloading':
        total = d.get('total_bytes') or d.get('total_bytes_estimate')
        downloaded = d.get('downloaded_bytes', 0)
        if total:
            porcentagem = int(downloaded * 100 / total)
            progress_var.set(porcentagem)
            janela.update_idletasks()
    elif d['status'] == 'finished':
        progress_var.set(100)
        janela.update_idletasks()


'''Função principal para baixar'''
def baixar():
    urls = entrada_urls.get("1.0", tk.END).strip().splitlines()
    tipo = tipo_var.get()
    qualidade = combo_qualidade.get()
    pasta = filedialog.askdirectory(title="Escolha onde salvar")

    if not urls or not pasta:
        messagebox.showerror("Erro", "Preencha as URLs e escolha uma pasta.")
        return

    progress_var.set(0)

    for url in urls:
        if not url.strip():
            continue

        ydl_opts = {
            'progress_hooks': [hook],
            'outtmpl': os.path.join(pasta, '%(title)s.%(ext)s')
        }

        if playlist_var.get() == 'único':
            ydl_opts['noplaylist'] = True

        if tipo == 'vídeo':
            resolucao = qualidade.replace('p', '')
            ydl_opts['format'] = f'bestvideo[height<={resolucao}]+bestaudio/best[height<={resolucao}]'
        elif tipo == 'áudio':
            bitrate = qualidade.replace('kbps', '')
            ydl_opts.update({
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': bitrate,
                }]
            })

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao baixar {url}:\n{str(e)}")

    messagebox.showinfo("Concluído", "Todos os downloads foram finalizados.")


'''Thread para não travar interface'''
def iniciar_download():
    thread = threading.Thread(target=baixar)
    thread.start()


'''Interface'''
janela = tk.Tk()
janela.title("Baixador de videos")
janela.geometry("500x500")
janela.resizable(False, False)

tk.Label(janela, text="Cole um ou mais LINKS (uma por linha):", font=('Arial', 11)).pack(pady=5)
entrada_urls = tk.Text(janela, height=5, width=60)
entrada_urls.pack(pady=5)

'''Tipo (vídeo ou áudio/ playlist ou video unico)'''
tipo_var = tk.StringVar(value='vídeo')
frame_tipo = tk.Frame(janela)
frame_tipo.pack(pady=5)
tk.Radiobutton(frame_tipo, text="Vídeo", variable=tipo_var, value='vídeo', command=lambda: atualizar_opcoes()).pack(side='left', padx=10)
tk.Radiobutton(frame_tipo, text="Áudio (MP3)", variable=tipo_var, value='áudio', command=lambda: atualizar_opcoes()).pack(side='left')

playlist_var = tk.StringVar(value='único')
frame_playlist = tk.Frame(janela)
frame_playlist.pack(pady=5)
tk.Radiobutton(frame_playlist, text="Baixar video/música", variable=playlist_var, value='único').pack(side='left', padx=10)
tk.Radiobutton(frame_playlist, text="Baixar playlist", variable=playlist_var, value='playlist').pack(side='left')


'''Qualidade'''
tk.Label(janela, text="Qualidade:", font=('Arial', 11)).pack()
combo_qualidade = ttk.Combobox(janela, state='readonly', width=20)
combo_qualidade.pack(pady=5)

def atualizar_opcoes():
    if tipo_var.get() == 'vídeo':
        combo_qualidade['values'] = ['360p', '480p', '720p', '1080p']
        combo_qualidade.set('720p')
    else:
        combo_qualidade['values'] = ['128kbps', '192kbps', '320kbps']
        combo_qualidade.set('192kbps')

atualizar_opcoes()

'''Barra de progresso'''
progress_var = tk.IntVar()
barra_progresso = ttk.Progressbar(janela, variable=progress_var, maximum=100, length=400)
barra_progresso.pack(pady=20)

'''Botão'''
tk.Button(janela, text="Baixar", command=iniciar_download, font=('Arial', 12), bg="green", fg="white").pack(pady=10)

janela.mainloop()

