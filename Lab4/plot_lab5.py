import os
import subprocess
import pandas as pd
import matplotlib.pyplot as plt

# 1. Asigurăm compilarea și rularea C++
CPP_SRC = "lab5.cpp"
EXE = "lab5.exe" if os.name == "nt" else "./lab5"
CSV_FILE = "results_lab5.csv"

if not os.path.exists(CSV_FILE):
    print("Compilez codul C++...")
    subprocess.run(f"g++ -O3 -std=c++17 {CPP_SRC} -o lab5", shell=True, check=True)
    print("Rulez executabilul...")
    subprocess.run(EXE, shell=True, check=True)

# 2. Încărcare date
df = pd.read_csv(CSV_FILE)

# Separăm datele pentru Sparse și Dense
df_sparse = df[df['Type'] == 'Sparse']
df_dense = df[df['Type'] == 'Dense']

# 3. Funcție pentru plotare
def plot_graph(data, title, filename):
    plt.figure(figsize=(10, 6))
    
    # Dijkstra este convertit în milisecunde pentru a fi lizibil pe grafic
    plt.plot(data['N'], data['Dijkstra_us'] / 1000, marker='o', color='#2980b9', 
             linewidth=2, label='N x Dijkstra (All-Pairs)')
    plt.plot(data['N'], data['FloydWarshall_us'] / 1000, marker='s', color='#e74c3c', 
             linewidth=2, label='Floyd-Warshall')
    
    plt.title(title, fontsize=14, fontweight='bold')
    plt.xlabel('Număr de Noduri (N)', fontsize=12)
    plt.ylabel('Timp de execuție (milisecunde)', fontsize=12)
    plt.legend(fontsize=11)
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig(filename, dpi=200)
    print(f"Salvata diagrama: {filename}")
    plt.close()

# 4. Generare ploturi
plot_graph(df_sparse, "Analiză Empirică: Dijkstra vs Floyd-Warshall (Graf Rar/Sparse)", "sparse_comparison.png")
plot_graph(df_dense, "Analiză Empirică: Dijkstra vs Floyd-Warshall (Graf Dens/Dense)", "dense_comparison.png")

print("Gata! Ai graficele pregătite pentru raport.")