from __future__ import annotations

import argparse
import math
import os
import sys
import random
import heapq
from typing import Dict, Generator, List, Tuple

import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.patches as mpatches
from matplotlib.lines import Line2D
import numpy as np

# --- CULORI TEMA ---
CLR_DEFAULT   = "#3498db" 
CLR_ACTIVE    = "#f1c40f" 
CLR_TARGET    = "#e74c3c" 
CLR_INTERMED  = "#9b59b6" 
CLR_VISITED   = "#2ecc71" 
CLR_START     = "#ffffff" 
CLR_EDGE_DEF  = "#95a5a6" 
CLR_EDGE_TREE = "#e67e22" 
CLR_BG        = "#1e1e2e" 
CLR_TEXT      = "#cdd6f4"

INF = float('inf')
Frame = Tuple[Dict[int, str], Dict[Tuple[int, int], str], str, str, Dict[int, float]]

# --- STRUCTURA GRAF PONDERAT ---
class WeightedGraph:
    def __init__(self, n: int):
        self.n = n
        self.m = 0
        self.adj: Dict[int, List[Tuple[int, float]]] = {i: [] for i in range(n)}

    def add_edge(self, u: int, v: int, weight: float, directed: bool = False):
        self.adj[u].append((v, weight))
        if not directed:
            self.adj[v].append((u, weight))
        self.m += 1

# --- CITIRE CUSTOM ---

def input_from_terminal() -> WeightedGraph:
    print("\n" + "═" * 50)
    print("  INTRODUCERE GRAF PONDERAT MANUAL")
    print("═" * 50)
    while True:
        try:
            n = int(input("\nNumăr de noduri: "))
            if n < 1:
                print("  ✗ Trebuie cel puțin 1 nod.")
                continue
            break
        except ValueError:
            print("  ✗ Introdu un număr întreg.")

    g = WeightedGraph(n)
    print(f"\nNoduri: 0 … {n - 1}")
    print("Introdu muchii ca 'u v cost' (ex: 0 1 15).")
    print("Apasă Enter pe o linie goală pentru a termina.\n")

    edge_count = 0
    while True:
        raw = input(f"  Muchie {edge_count + 1}: ").strip()
        if raw == "": break
        parts = raw.split()
        if len(parts) != 3:
            print("  ✗ Format greșit. Exemplu: 0 1 15")
            continue
        try:
            u, v, w = int(parts[0]), int(parts[1]), float(parts[2])
        except ValueError:
            print("  ✗ Date invalide. Introdu numere.")
            continue
        if not (0 <= u < n and 0 <= v < n):
            print(f"  ✗ Nodurile trebuie între 0 și {n - 1}.")
            continue
        if u == v:
            print("  ✗ Buclele nu sunt permise în această vizualizare.")
            continue
        g.add_edge(u, v, w)
        edge_count += 1
        print(f"  ✓ Adăugat: {u} — {v} (cost {w})")
    return g

def input_from_file(path: str) -> WeightedGraph:
    if not os.path.exists(path):
        print(f"✗ Fișierul '{path}' nu a fost găsit.")
        sys.exit(1)
    with open(path) as f:
        lines = [l.strip() for l in f if l.strip() and not l.startswith("#")]
    if not lines:
        print("✗ Fișierul este gol.")
        sys.exit(1)
    n = int(lines[0])
    g = WeightedGraph(n)
    for line in lines[1:]:
        parts = line.split()
        if len(parts) >= 3:
            u, v, w = int(parts[0]), int(parts[1]), float(parts[2])
            g.add_edge(u, v, w)
    print(f"  ✓ Încărcat din '{path}': {n} noduri, {g.m} muchii.")
    return g

def input_from_args(arg: str) -> WeightedGraph:
    try:
        head, body = arg.split(":", 1)
        n = int(head.strip())
        g = WeightedGraph(n)
        for token in body.split(","):
            token = token.strip()
            if not token: continue
            parts = token.replace("-", " ").split()
            u, v, w  = int(parts[0]), int(parts[1]), float(parts[2])
            g.add_edge(u, v, w)
        print(f"  ✓ Graf din --custom: {n} noduri, {g.m} muchii.")
        return g
    except Exception as e:
        print(f"✗ Format --custom greșit: {e}")
        print("  Exemplu corect: --custom \"4: 0-1-10, 1-2-5, 0-2-3\"")
        sys.exit(1)

# --- GENERATOARE DE ANIMATIE ---

def dijkstra_gen(g: WeightedGraph, start: int = 0) -> Generator[Frame, None, None]:
    n_colors = {i: CLR_DEFAULT for i in range(g.n)}
    e_colors = {}
    for u in range(g.n):
        for v, w in g.adj[u]: e_colors[(min(u, v), max(u, v))] = CLR_EDGE_DEF
            
    distances = {i: INF for i in range(g.n)}
    distances[start] = 0
    pq = [(0, start)]
    visited = set()
    
    n_colors[start] = CLR_START
    yield dict(n_colors), dict(e_colors), "Inițializare", f"Start Dijkstra din nodul {start}", dict(distances)

    while pq:
        d, u = heapq.heappop(pq)
        if u in visited: continue
            
        n_colors[u] = CLR_ACTIVE
        yield dict(n_colors), dict(e_colors), "Se extrage minimul", f"Procesez nodul {u} (dist: {d})", dict(distances)

        for v, weight in g.adj[u]:
            edge = (min(u, v), max(u, v))
            if v not in visited:
                n_colors[v] = CLR_TARGET
                e_colors[edge] = CLR_ACTIVE
                yield dict(n_colors), dict(e_colors), "Verificare muchie", f"Verific {u} → {v} (cost: {weight})", dict(distances)
                
                if distances[u] + weight < distances[v]:
                    distances[v] = distances[u] + weight
                    heapq.heappush(pq, (distances[v], v))
                    e_colors[edge] = CLR_EDGE_TREE
                    yield dict(n_colors), dict(e_colors), "Relaxare", f"✓ Distanță actualizată pentru {v}: {distances[v]}", dict(distances)
                else:
                    e_colors[edge] = CLR_EDGE_DEF
                
                if v != start and v not in visited:
                    n_colors[v] = CLR_DEFAULT

        visited.add(u)
        n_colors[u] = CLR_VISITED
        yield dict(n_colors), dict(e_colors), "Finalizat", f"Nodul {u} a fost finalizat", dict(distances)

    yield dict(n_colors), dict(e_colors), "Gata", "✓ Dijkstra complet!", dict(distances)

def fw_gen(g: WeightedGraph, start: int = 0) -> Generator[Frame, None, None]:
    n_colors = {i: CLR_DEFAULT for i in range(g.n)}
    e_colors = {}
    for u in range(g.n):
        for v, w in g.adj[u]: e_colors[(min(u, v), max(u, v))] = CLR_EDGE_DEF
            
    dist = [[INF] * g.n for _ in range(g.n)]
    for i in range(g.n): dist[i][i] = 0
    for u in range(g.n):
        for v, w in g.adj[u]: dist[u][v] = w
            
    yield dict(n_colors), dict(e_colors), "Inițializare", "Construiesc matricea inițială", {}
    updates = 0
    
    for k in range(g.n):
        n_colors = {x: CLR_DEFAULT for x in range(g.n)}
        n_colors[k] = CLR_INTERMED
        yield dict(n_colors), dict(e_colors), f"Faza k={k}", f"Fixăm nodul intermediar k={k}", {}
        
        for i in range(g.n):
            for j in range(g.n):
                if dist[i][k] != INF and dist[k][j] != INF and dist[i][k] + dist[k][j] < dist[i][j]:
                    dist[i][j] = dist[i][k] + dist[k][j]
                    updates += 1
                    n_colors[i], n_colors[j] = CLR_START, CLR_TARGET
                    
                    e1, e2 = (min(i, k), max(i, k)), (min(k, j), max(k, j))
                    if e1 in e_colors: e_colors[e1] = CLR_ACTIVE
                    if e2 in e_colors: e_colors[e2] = CLR_ACTIVE
                    
                    yield dict(n_colors), dict(e_colors), f"Relaxare k={k}", f"Drum mai scurt găsit: {i} → {k} → {j} (Nou: {dist[i][j]})", {}
                    
                    if e1 in e_colors: e_colors[e1] = CLR_EDGE_TREE
                    if e2 in e_colors: e_colors[e2] = CLR_EDGE_TREE
                    n_colors[i], n_colors[j] = CLR_DEFAULT, CLR_DEFAULT
        n_colors[k] = CLR_DEFAULT

    for i in range(g.n): n_colors[i] = CLR_VISITED
    yield dict(n_colors), dict(e_colors), "Gata", f"✓ Floyd-Warshall complet! {updates} actualizări.", {}

ALGO_MAP = {
    "dijkstra": ("Dijkstra — Single Source", dijkstra_gen),
    "fw":       ("Floyd-Warshall — All Pairs", fw_gen),
}

# --- RENDERER ANIMATIE ---

def spring_layout(g: WeightedGraph, iterations: int = 150) -> Dict[int, Tuple[float, float]]:
    rng = np.random.default_rng(42)
    pos = {i: rng.uniform(-1, 1, 2) for i in range(g.n)}
    k   = 1.0 / math.sqrt(max(g.n, 1))

    for _ in range(iterations):
        disp = {i: np.zeros(2) for i in range(g.n)}
        nodes = list(range(g.n))
        for i in nodes:
            for j in nodes:
                if i == j: continue
                delta = pos[i] - pos[j]
                dist  = max(np.linalg.norm(delta), 1e-6)
                disp[i] += (delta / dist) * (k * k / dist)
        for u in range(g.n):
            for v, w in g.adj[u]:
                if u < v:
                    delta = pos[u] - pos[v]
                    dist  = max(np.linalg.norm(delta), 1e-6)
                    force = delta / dist * dist * dist / k
                    disp[u] -= force
                    disp[v] += force
        for i in nodes:
            d = np.linalg.norm(disp[i])
            if d > 0:
                pos[i] += disp[i] / d * min(d, 0.05)

    xs = [p[0] for p in pos.values()]
    ys = [p[1] for p in pos.values()]
    mx, mn = max(xs) - min(xs), max(ys) - min(ys)
    for i in pos:
        pos[i] = (2 * (pos[i][0] - min(xs)) / max(mx, 1e-6) - 1, 2 * (pos[i][1] - min(ys)) / max(mn, 1e-6) - 1)
    return pos

def circle_layout(n: int) -> Dict[int, Tuple[float, float]]:
    return {i: (math.cos(2 * math.pi * i / n - math.pi / 2), math.sin(2 * math.pi * i / n - math.pi / 2)) for i in range(n)}

def animate_traversal(name, generator_fn, g, pos, interval=600, save=False):
    frames: List[Frame] = list(generator_fn(g))
    if not frames: return

    node_ids = list(range(g.n))
    edges = []
    edge_weights = {}
    for u in range(g.n):
        for v, w in g.adj[u]:
            if u < v:
                edges.append((u, v))
                edge_weights[(u, v)] = w

    xs = np.array([pos[i][0] for i in node_ids])
    ys = np.array([pos[i][1] for i in node_ids])

    fig, ax = plt.subplots(figsize=(13, 7))
    fig.patch.set_facecolor(CLR_BG)
    ax.set_facecolor(CLR_BG)
    ax.set_aspect("equal")
    ax.axis("off")

    node_size = 800
    font_size = 11

    edge_lines: Dict[Tuple[int, int], Line2D] = {}
    for (u, v) in edges:
        line, = ax.plot([pos[u][0], pos[v][0]], [pos[u][1], pos[v][1]], color=CLR_EDGE_DEF, linewidth=1.5, zorder=1, alpha=0.55)
        edge_lines[(u, v)] = line
        mx, my = (pos[u][0] + pos[v][0]) / 2, (pos[u][1] + pos[v][1]) / 2
        ax.text(mx, my, str(edge_weights[(u, v)]), color="#a6adc8", fontsize=9, fontweight="bold", 
                ha='center', va='center', bbox=dict(facecolor=CLR_BG, edgecolor='none', pad=1), zorder=2)

    scat = ax.scatter(xs, ys, s=node_size, c=[frames[0][0][i] for i in node_ids], zorder=3, edgecolors="#00000060", linewidths=1.0)

    label_texts, dist_texts = [], []
    for i in node_ids:
        t = ax.text(pos[i][0], pos[i][1], str(i), ha="center", va="center", fontsize=font_size, color="black", fontweight="bold", zorder=4)
        label_texts.append(t)
        dt = ax.text(pos[i][0], pos[i][1] + 0.15, "", ha="center", va="center", fontsize=10, color="#a6e3a1", fontweight="bold", zorder=4)
        dist_texts.append(dt)

    ax.set_title(name, fontsize=14, fontweight="bold", color=CLR_TEXT, pad=20)
    status_text  = ax.text(0.5, -0.05, "", transform=ax.transAxes, ha="center", fontsize=11, color="#f5c211", fontweight="bold")
    step_txt = ax.text(0.01, 1.02, "", transform=ax.transAxes, ha="left", fontsize=10, color=CLR_TEXT, alpha=0.85)

    legend_items = [
        mpatches.Patch(color=CLR_DEFAULT,  label="Necunoscut"),
        mpatches.Patch(color=CLR_ACTIVE,   label="Procesat/Sursă"),
        mpatches.Patch(color=CLR_INTERMED, label="Nod intermediar (k)"),
        mpatches.Patch(color=CLR_VISITED,  label="Finalizat"),
        Line2D([0], [0], color=CLR_EDGE_TREE, linewidth=2, label="Drum actualizat"),
    ]
    ax.legend(handles=legend_items, loc="upper right", fontsize=9, framealpha=0.3, labelcolor=CLR_TEXT, facecolor=CLR_BG)

    def update(fi: int):
        n_cols, e_cols, step, msg, dists = frames[fi]
        for (u, v), line in edge_lines.items():
            c = e_cols.get((u, v), CLR_EDGE_DEF)
            line.set_color(c)
            line.set_linewidth(3 if c == CLR_EDGE_TREE else (2.5 if c == CLR_ACTIVE else 1.5))
            line.set_alpha(1.0 if c != CLR_EDGE_DEF else 0.45)
            
        scat.set_facecolor([n_cols[i] for i in node_ids])
        status_text.set_text(msg)
        step_txt.set_text(f"{step}  |  cadru {fi + 1}/{len(frames)}")
        
        for i, dt in enumerate(dist_texts):
            if dists and i in dists:
                val = "∞" if dists[i] == INF else str(dists[i])
                dt.set_text(f"d={val}")
            else:
                dt.set_text("")
        return [scat, status_text, step_txt] + list(edge_lines.values()) + dist_texts

    anim = animation.FuncAnimation(fig, update, frames=len(frames), interval=interval, blit=False, repeat=False)

    if save:
        os.makedirs("plots", exist_ok=True)
        out = f"plots/{name.split('—')[0].strip().lower().replace(' ', '_')}.gif"
        anim.save(out, writer="pillow", fps=max(1, 1000 // interval))

    plt.tight_layout()
    plt.show()

# --- RUNNER ---

def make_random_weighted_graph(n: int, rseed: int = 42) -> WeightedGraph:
    r = random.Random(rseed)
    g = WeightedGraph(n)
    perm = list(range(n))
    r.shuffle(perm)
    for i in range(1, n):
        p = r.randint(0, i - 1)
        g.add_edge(perm[i], perm[p], r.randint(1, 15))
    for _ in range(n):
        u, v = r.randint(0, n - 1), r.randint(0, n - 1)
        if u != v and not any(edge[0] == v for edge in g.adj[u]):
            g.add_edge(u, v, r.randint(1, 20))
    return g

def main() -> None:
    parser = argparse.ArgumentParser(description="Animatii Lab 5 - Dijkstra si Floyd-Warshall")
    parser.add_argument("--input", choices=["random", "terminal", "fisier"], default="random")
    parser.add_argument("--file", type=str, default=None)
    parser.add_argument("--custom", type=str, default=None)
    parser.add_argument("--algo", choices=list(ALGO_MAP.keys()), default="dijkstra")
    parser.add_argument("--n", type=int, default=6)
    parser.add_argument("--start", type=int, default=0)
    parser.add_argument("--layout", choices=["spring", "circle"], default="circle")
    parser.add_argument("--speed", type=int, default=600)
    parser.add_argument("--save", action="store_true")
    args = parser.parse_args()

    if args.custom:
        g = input_from_args(args.custom)
    elif args.input == "terminal":
        g = input_from_terminal()
    elif args.input == "fisier":
        if not args.file:
            print("✗ Specifică fișierul cu --file <cale>")
            sys.exit(1)
        g = input_from_file(args.file)
    else:
        if args.algo == "fw" and args.n > 8:
            print("  [!] Floyd-Warshall generează multe cadre. Limităm random la N=6 pt siguranță.")
            args.n = 6
        g = make_random_weighted_graph(args.n)
        print(f"  ✓ Graf random: {g.n} noduri, {g.m} muchii.")

    if not (0 <= args.start < g.n):
        print(f"✗ Nodul de start {args.start} nu există (0 … {g.n - 1}).")
        sys.exit(1)

    pos = circle_layout(g.n) if args.layout == "circle" else spring_layout(g)
    
    name, gen_fn = ALGO_MAP[args.algo]
    print(f"\n▶ Rulare {name} (Viteză: {args.speed}ms/cadru)...")

    animate_traversal(name, lambda graph: gen_fn(graph, args.start), g, pos, interval=args.speed, save=args.save)

if __name__ == "__main__":
    main()