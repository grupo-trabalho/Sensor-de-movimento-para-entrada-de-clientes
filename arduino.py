import tkinter as tk
from tkinter import messagebox
import threading
import time
import csv
from datetime import datetime
import socket
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import os
import re
import pandas as pd
import plotly.express as px

# Configurações de rede
arduino_ip = '192.168.1.177'  # IP do Arduino
arduino_port = 80             # Porta do servidor Arduino

# Variáveis Globais
running = False
timer_thread = None
data_collection_thread = None
data = []
last_entry = None  # Para armazenar a última entrada e evitar repetições
options_window = None  # Variável para armazenar a janela de opções de gráfico

def update_timer_label(seconds):
    while seconds > 0 and running:
        minutes, secs = divmod(seconds, 60)
        hours, minutes = divmod(minutes, 60)
        time_format = '{:02d}:{:02d}:{:02d}'.format(hours, minutes, secs)
        timer_label.config(text="Tempo Restante: " + time_format)
        root.update()
        time.sleep(1)
        seconds -= 1
    if running:
        timer_label.config(text="Tempo Restante: 00:00:00")
        stop_data_collection()
    else:
        timer_label.config(text="Tempo Interrompido")

def start_data_collection():
    global running, data_collection_thread, timer_thread
    if running:
        messagebox.showinfo("Informação", "A coleta de dados já está em andamento.")
        return
    running = True
    total_time = int(hours_spinbox.get()) * 3600 + int(minutes_spinbox.get()) * 60
    timer_thread = threading.Thread(target=update_timer_label, args=(total_time,), daemon=True)
    data_collection_thread = threading.Thread(target=collect_data, args=(total_time,), daemon=True)
    timer_thread.start()
    data_collection_thread.start()

def stop_data_collection():
    global running
    if running:
        running = False
        status_label.config(text="Coleta interrompida pelo usuário.")
        generate_csv()

def collect_data(duration):
    global data, last_entry
    start_time = time.time()
    while time.time() - start_time < duration and running:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((arduino_ip, arduino_port))
                s.sendall(b'GET / HTTP/1.1\r\nHost: arduino\r\nConnection: close\r\n\r\n')
                response = ''
                while True:
                    part = s.recv(1024).decode('utf-8')
                    if not part:
                        break
                    response += part
                body = response.split('\r\n\r\n')[1]
                entries_match = re.search(r'Entrada: (\d+)', body)
                exits_match = re.search(r'Saída: (\d+)', body)
                if entries_match and exits_match:
                    entries = int(entries_match.group(1))
                    exits = int(exits_match.group(1))
                    current_datetime = datetime.now()
                    new_data = [entries, exits, current_datetime.strftime('%Y-%m-%d %H:%M:%S')]
                    if not last_entry or (entries != last_entry[0] or exits != last_entry[1]):
                        data.append(new_data)
                        last_entry = new_data
                        print(f"Entrada: {entries}, Saída: {exits} - Dados adicionados ao CSV")
                    else:
                        print("Dados repetidos, não adicionados")
                else:
                    print("Números não encontrados ou formato inesperado")
        except Exception as e:
            print(f"Erro na conexão: {e}")
        time.sleep(1)
    if not running:
        status_label.config(text="Coleta de dados concluída automaticamente.")
        generate_csv()

def generate_csv():
    if data:
        try:
            file_path = 'D:\\projeto\\workspace\\Iot\\contador2_dados_contagem.csv'
            file_exists = os.path.isfile(file_path)
            with open(file_path, 'a', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                if not file_exists:
                    writer.writerow(['Entradas', 'Saídas', 'Data e Hora'])
                for row in data:
                    writer.writerow(row)
            print(f"Arquivo CSV atualizado em: {file_path}")
            graph_options(file_path)  # Chama a função para apresentar as opções de gráfico
        except Exception as e:
            print(f"Erro ao atualizar o arquivo CSV: {e}")
    else:
        print("Nenhum dado disponível para salvar.")

def graph_options(csv_path):
    global options_window
    # Verifica se a janela já está aberta
    if options_window and options_window.winfo_exists():
        options_window.lift()
        return

    # Cria uma nova janela para escolher o tipo de gráfico
    options_window = tk.Toplevel(root)
    options_window.title("Escolher Tipo de Gráfico")
    options_window.geometry("300x150")
    options_window.configure(bg='#f0f0f0')

    label_style = {'font': ('Helvetica', 12), 'bg': '#f0f0f0'}
    button_style = {'font': ('Helvetica', 12), 'bg': '#4caf50', 'fg': 'white', 'activebackground': '#45a049'}

    tk.Label(options_window, text="Escolha o tipo de gráfico:", **label_style).pack(pady=10)
    
    basic_graph_btn = tk.Button(options_window, text="Gráfico Básico", command=lambda: generate_basic_graph(csv_path), **button_style)
    basic_graph_btn.pack(pady=5)
    
    interactive_graph_btn = tk.Button(options_window, text="Gráfico Interativo", command=lambda: generate_interactive_graph(csv_path), **button_style)
    interactive_graph_btn.pack(pady=5)

def generate_basic_graph(csv_path):
    df = pd.read_csv(csv_path)
    df['Data e Hora'] = pd.to_datetime(df['Data e Hora'])

    fig, ax = plt.subplots()
    ax.plot(df['Data e Hora'], df['Entradas'], label='Entradas')
    ax.plot(df['Data e Hora'], df['Saídas'], label='Saídas')
    ax.set_xlabel('Data e Hora')
    ax.set_ylabel('Contagem')
    ax.set_title('Contagem de Entradas e Saídas')
    ax.legend()
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M:%S'))
    ax.xaxis.set_major_locator(mdates.AutoDateLocator())
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

def generate_interactive_graph(csv_path):
    df = pd.read_csv(csv_path)
    df['Data e Hora'] = pd.to_datetime(df['Data e Hora'])

    fig_interactive = px.line(df, x='Data e Hora', y=['Entradas', 'Saídas'], labels={'value': 'Contagem', 'variable': 'Legenda'}, title='Contagem de Entradas e Saídas')
    fig_interactive.show()

# Interface Gráfica com Tkinter
root = tk.Tk()
root.title("Coleta de Dados de Contagem")

# Estilos
root.geometry("300x200")
root.configure(bg='#f0f0f0')

label_style = {'font': ('Helvetica', 12), 'bg': '#f0f0f0'}
spinbox_style = {'font': ('Helvetica', 12), 'width': 5}
button_style = {'font': ('Helvetica', 12), 'bg': '#4caf50', 'fg': 'white', 'activebackground': '#45a049'}

tk.Label(root, text="Horas:", **label_style).grid(row=0, column=0, pady=10, padx=10)
hours_spinbox = tk.Spinbox(root, from_=0, to=23, **spinbox_style)
hours_spinbox.grid(row=0, column=1, pady=10, padx=10)

tk.Label(root, text="Minutos:", **label_style).grid(row=1, column=0, pady=10, padx=10)
minutes_spinbox = tk.Spinbox(root, from_=0, to=59, **spinbox_style)
minutes_spinbox.grid(row=1, column=1, pady=10, padx=10)

start_button = tk.Button(root, text="Iniciar Coleta", command=start_data_collection, **button_style)
start_button.grid(row=2, column=0, pady=10, padx=10)

stop_button = tk.Button(root, text="Parar Coleta", command=stop_data_collection, **button_style)
stop_button.grid(row=2, column=1, pady=10, padx=10)

timer_label = tk.Label(root, text="Tempo Restante: 00:00:00", **label_style)
timer_label.grid(row=3, column=0, columnspan=2, pady=10, padx=10)

status_label = tk.Label(root, text="Status: Aguardando início da coleta.", **label_style)
status_label.grid(row=4, column=0, columnspan=2, pady=10, padx=10)

root.mainloop()
