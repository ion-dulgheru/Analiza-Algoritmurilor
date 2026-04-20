"""
Laboratory Work #7 – Greedy Algorithms
Animated Visualizer: Prim & Kruskal
Same style as the Sorting Visualizer from the previous lab.

Usage:
    python visualize.py                        # both algorithms, n=10
    python visualize.py --algo kruskal         # only Kruskal
    python visualize.py --algo prim --n 12     # Prim, 12 nodes
    python visualize.py --n 8 --speed 800      # slower animation
    python visualize.py --save                 # save .gif files

Requirements:
    pip install matplotlib networkx numpy
"""

from __future__ import annotations

import argparse
import os
import random
from typing import Generator, List, Tuple, Dict

import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.lines as mlines
import networkx as nx
import numpy as np

# ─────────────────────────────────────────────
#  Colour palette  (same feel as sorting viz)
# ─────────────────────────────────────────────
CLR_BG          = "#1e1e2e"
CLR_TEXT        = "#cdd6f4"
CLR_NODE_DEF    = "#3498db"   # blue   – unvisited
CLR_NODE_VISIT  = "#f1c40f"   # yellow – current / active
CLR_NODE_DONE   = "#2ecc71"   # green  – in MST
CLR_EDGE_DEF    = "#4a4a6a"   # dim    – unprocessed
CLR_EDGE_CMP    = "#e74c3c"   # red    – being considered
CLR_EDGE_ACC    = "#2ecc71"   # green  – accepted into MST
CLR_EDGE_REJ    = "#636380"   # grey   – rejected
CLR_EDGE_FRONT  = "#e67e22"   # orange – frontier (Prim)

# Frame = (state_dict, status_text)
Frame = Tuple[Dict, str]


# ─────────────────────────────────────────────
#  Graph generator
# ─────────────────────────────────────────────

def make_graph(n: int, rng_seed: int = 42) -> Tuple[nx.Graph, Dict]:
    rnd = random.Random(rng_seed)
    G = nx.Graph()
    G.add_nodes_from(range(n))

    nodes = list(range(n))
    rnd.shuffle(nodes)
    for i in range(1, n):
        u, v = nodes[i - 1], nodes[i]
        G.add_edge(u, v, weight=rnd.randint(1, 20))

    extra = max(n, int(n * 1.4))
    for _ in range(extra):
        u = rnd.randint(0, n - 1)
        v = rnd.randint(0, n - 1)
        if u != v and not G.has_edge(u, v):
            G.add_edge(u, v, weight=rnd.randint(1, 20))

    pos = nx.spring_layout(G, seed=rng_seed, k=2.2 / (n ** 0.5))
    return G, pos


# ─────────────────────────────────────────────
#  DSU for Kruskal
# ─────────────────────────────────────────────
def load_graph_from_file(filepath: str) -> Tuple[nx.Graph, Dict]:
    G = nx.Graph()
    with open(filepath, 'r') as f:
        for line in f:
            # Ignorăm liniile goale sau comentariile
            if not line.strip() or line.startswith("#"):
                continue
            parts = line.split()
            if len(parts) >= 3:
                u, v, w = int(parts[0]), int(parts[1]), int(parts[2])
                G.add_edge(u, v, weight=w)
    
    # Generăm pozițiile nodurilor pentru desenare
    pos = nx.spring_layout(G, seed=42)
    return G, pos

class DSU:
    def __init__(self, n: int):
        self.p = list(range(n))
        self.r = [0] * n

    def find(self, x: int) -> int:
        while self.p[x] != x:
            self.p[x] = self.p[self.p[x]]
            x = self.p[x]
        return x

    def union(self, x: int, y: int) -> bool:
        px, py = self.find(x), self.find(y)
        if px == py:
            return False
        if self.r[px] < self.r[py]:
            px, py = py, px
        self.p[py] = px
        if self.r[px] == self.r[py]:
            self.r[px] += 1
        return True


# ─────────────────────────────────────────────
#  KRUSKAL generator
# ─────────────────────────────────────────────

def kruskal_gen(G: nx.Graph) -> Generator[Frame, None, None]:
    n = G.number_of_nodes()
    all_edges = sorted(G.edges(data=True), key=lambda e: e[2]["weight"])

    edge_color = {(min(u, v), max(u, v)): CLR_EDGE_DEF for u, v, _ in G.edges(data=True)}
    node_color = {nd: CLR_NODE_DEF for nd in G.nodes()}
    mst_edges: List[Tuple] = []
    total_weight = 0

    def snap():
        return {"edge_color": dict(edge_color),
                "node_color": dict(node_color),
                "mst_edges": list(mst_edges),
                "total_w": total_weight}

    yield snap(), "Kruskal: all edges sorted by weight — start processing…"

    dsu = DSU(n)

    for idx, (u, v, data) in enumerate(all_edges):
        w = data["weight"]
        key = (min(u, v), max(u, v))

        edge_color[key] = CLR_EDGE_CMP
        node_color[u]   = CLR_NODE_VISIT
        node_color[v]   = CLR_NODE_VISIT
        yield snap(), f"[{idx + 1}/{len(all_edges)}]  Consider ({u} – {v})   w = {w}"

        if dsu.union(u, v):
            total_weight += w
            edge_color[key] = CLR_EDGE_ACC
            node_color[u]   = CLR_NODE_DONE
            node_color[v]   = CLR_NODE_DONE
            mst_edges.append((u, v))
            yield snap(), f"✔  Accept  ({u} – {v})   w = {w}   │  Total = {total_weight}"
        else:
            edge_color[key] = CLR_EDGE_REJ
            # restore node colour based on MST membership
            for nd in (u, v):
                in_mst = any(nd in (a, b) for a, b in mst_edges)
                node_color[nd] = CLR_NODE_DONE if in_mst else CLR_NODE_DEF
            yield snap(), f"✘  Reject  ({u} – {v})   w = {w}   — would form a cycle"

        if len(mst_edges) == n - 1:
            break

    for nd in G.nodes():
        node_color[nd] = CLR_NODE_DONE
    yield snap(), f"✓  Kruskal complete!   MST weight = {total_weight}"


# ─────────────────────────────────────────────
#  PRIM generator
# ─────────────────────────────────────────────

def prim_gen(G: nx.Graph) -> Generator[Frame, None, None]:
    import heapq
    n = G.number_of_nodes()

    edge_color = {(min(u, v), max(u, v)): CLR_EDGE_DEF for u, v in G.edges()}
    node_color = {nd: CLR_NODE_DEF for nd in G.nodes()}
    mst_edges: List[Tuple] = []
    total_weight = 0
    in_mst = [False] * n

    def snap():
        return {"edge_color": dict(edge_color),
                "node_color": dict(node_color),
                "mst_edges": list(mst_edges),
                "total_w": total_weight}

    start = 0
    in_mst[start] = True
    node_color[start] = CLR_NODE_DONE

    heap: List[Tuple[int, int, int]] = []
    for nbr, data in G[start].items():
        w = data["weight"]
        heapq.heappush(heap, (w, start, nbr))
        key = (min(start, nbr), max(start, nbr))
        edge_color[key] = CLR_EDGE_FRONT

    yield snap(), f"Prim: start at node {start}   │  {len(heap)} frontier edges pushed"

    step = 0
    while heap and len(mst_edges) < n - 1:
        w, u, v = heapq.heappop(heap)
        key = (min(u, v), max(u, v))
        step += 1

        edge_color[key] = CLR_EDGE_CMP
        if not in_mst[v]:
            node_color[v] = CLR_NODE_VISIT
        yield snap(), f"[step {step}]  Pop min edge ({u} – {v})   w = {w}"

        if in_mst[v]:
            edge_color[key] = CLR_EDGE_REJ
            yield snap(), f"✘  Skip  ({u} – {v})  — node {v} already in MST"
            continue

        # Accept
        in_mst[v] = True
        total_weight += w
        edge_color[key] = CLR_EDGE_ACC
        node_color[v] = CLR_NODE_DONE
        mst_edges.append((u, v))
        yield snap(), f"✔  Accept  ({u} – {v})   w = {w}   │  Total = {total_weight}"

        new_front = 0
        for nbr, data in G[v].items():
            if not in_mst[nbr]:
                ew = data["weight"]
                heapq.heappush(heap, (ew, v, nbr))
                nkey = (min(v, nbr), max(v, nbr))
                if edge_color[nkey] != CLR_EDGE_ACC:
                    edge_color[nkey] = CLR_EDGE_FRONT
                new_front += 1
        if new_front:
            yield snap(), f"   Added {new_front} frontier edge(s) from node {v}"

    for nd in G.nodes():
        node_color[nd] = CLR_NODE_DONE
    yield snap(), f"✓  Prim complete!   MST weight = {total_weight}"


# ─────────────────────────────────────────────
#  ANIMATION ENGINE
# ─────────────────────────────────────────────

ALGO_MAP = {
    "kruskal": ("Kruskal's Algorithm", kruskal_gen),
    "prim":    ("Prim's Algorithm",    prim_gen),
}


def animate_graph(title: str, gen_fn, G: nx.Graph, pos: Dict,
                  interval: int = 600, save: bool = False) -> None:

    print(f"  Computing frames…", end=" ", flush=True)
    frames: List[Frame] = list(gen_fn(G))
    print(f"{len(frames)} frames.")

    edge_list  = list(G.edges())
    node_list  = list(G.nodes())
    weights    = nx.get_edge_attributes(G, "weight")
    n_nodes    = G.number_of_nodes()

    # ── Figure ──
    fig, ax = plt.subplots(figsize=(13, 8))
    fig.patch.set_facecolor(CLR_BG)
    ax.set_facecolor(CLR_BG)
    ax.axis("off")

    # Static weight labels
    for (u, v), w in weights.items():
        x0, y0 = pos[u]; x1, y1 = pos[v]
        ax.text((x0 + x1) / 2, (y0 + y1) / 2, str(w),
                fontsize=7, ha="center", va="center", color="#aaaaaa", zorder=5,
                bbox=dict(boxstyle="round,pad=0.1", fc=CLR_BG, ec="none", alpha=0.6))

    # Edge line objects (dynamic)
    edge_lines: Dict[Tuple, plt.Line2D] = {}
    for u, v in edge_list:
        key = (min(u, v), max(u, v))
        x0, y0 = pos[u]; x1, y1 = pos[v]
        line, = ax.plot([x0, x1], [y0, y1], color=CLR_EDGE_DEF,
                        linewidth=2, zorder=1, solid_capstyle="round")
        edge_lines[key] = line

    # Node scatter (dynamic)
    xs = np.array([pos[nd][0] for nd in node_list])
    ys = np.array([pos[nd][1] for nd in node_list])
    scatter = ax.scatter(xs, ys,
                         s=480 if n_nodes <= 15 else 280,
                         c=[CLR_NODE_DEF] * n_nodes,
                         zorder=3, linewidths=1.8, edgecolors="#ffffff50")

    # Node ID labels (static)
    for nd in node_list:
        ax.text(pos[nd][0], pos[nd][1], str(nd),
                fontsize=9, ha="center", va="center",
                color="#ffffff", fontweight="bold", zorder=4)

    # ── UI text ──
    ax.set_title(title, fontsize=15, fontweight="bold", color=CLR_TEXT, pad=14)
    status_txt  = ax.text(0.5,  1.033, "", transform=ax.transAxes,
                           ha="center", fontsize=10, color="#f5c211", fontweight="bold")
    counter_txt = ax.text(0.01, 0.97,  "", transform=ax.transAxes,
                           ha="left",   fontsize=9,  color=CLR_TEXT,  alpha=0.7)
    weight_txt  = ax.text(0.99, 0.97,  "", transform=ax.transAxes,
                           ha="right",  fontsize=10, color=CLR_EDGE_ACC, fontweight="bold")

    # ── Legend ──
    legend_items = [
        mlines.Line2D([], [], color=CLR_EDGE_DEF,   lw=2,   label="Unprocessed edge"),
        mlines.Line2D([], [], color=CLR_EDGE_CMP,   lw=2.5, label="Considering"),
        mlines.Line2D([], [], color=CLR_EDGE_ACC,   lw=3,   label="Accepted (MST)"),
        mlines.Line2D([], [], color=CLR_EDGE_REJ,   lw=2,   label="Rejected (cycle)"),
        mlines.Line2D([], [], color=CLR_EDGE_FRONT, lw=2,   label="Frontier (Prim)"),
    ]
    ax.legend(handles=legend_items, loc="lower left",
              facecolor="#2a2a3e", edgecolor="#555", labelcolor=CLR_TEXT,
              fontsize=8, framealpha=0.85)

    plt.tight_layout()

    # ── Update function ──
    def update(fi: int):
        state, msg = frames[fi]
        ec = state["edge_color"]
        nc = state["node_color"]

        for key, line in edge_lines.items():
            c = ec.get(key, CLR_EDGE_DEF)
            line.set_color(c)
            lw = (3.8 if c == CLR_EDGE_ACC   else
                  3.0 if c == CLR_EDGE_CMP   else
                  2.5 if c == CLR_EDGE_FRONT else 1.5)
            line.set_linewidth(lw)
            line.set_alpha(0.30 if c == CLR_EDGE_REJ else 1.0)
            line.set_zorder(3 if c in (CLR_EDGE_ACC, CLR_EDGE_CMP) else 1)

        scatter.set_facecolors([nc.get(nd, CLR_NODE_DEF) for nd in node_list])

        status_txt.set_text(msg)
        counter_txt.set_text(f"Step {fi + 1} / {len(frames)}")
        tw = state.get("total_w", 0)
        if tw:
            weight_txt.set_text(f"MST weight: {tw}")

        return list(edge_lines.values()) + [scatter, status_txt, counter_txt, weight_txt]

    anim = animation.FuncAnimation(
        fig, update,
        frames=len(frames),
        interval=interval,
        blit=False,
        repeat=False,
    )

    if save:
        os.makedirs("plots", exist_ok=True)
        out = f"plots/{title.lower().replace(' ', '_').replace(chr(39), '')}.gif"
        print(f"  Saving {out} …", end=" ", flush=True)
        anim.save(out, writer="pillow", fps=max(1, 1000 // interval))
        print("done.")

    plt.show()


# ─────────────────────────────────────────────
#  CLI  (same pattern as sorting visualizer)
# ─────────────────────────────────────────────
import csv

import os
import csv
import matplotlib.pyplot as plt
import numpy as np

def plot_empirical_data(csv_file: str, save: bool = True):
    if not os.path.exists(csv_file):
        print(f"❌ Fișierul {csv_file} nu a fost găsit!")
        return

    nodes, kruskal_ms, prim_ms = [], [], []

    with open(csv_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            nodes.append(int(row['nodes']))
            kruskal_ms.append(float(row['kruskal_ms']))
            prim_ms.append(float(row['prim_ms']))

    if not nodes:
        return

    if save and not os.path.exists("plots"):
        os.makedirs("plots")

    # ---------------------------------------------------------
    # 1. time_vs_size.png (Graficul clasic liniar)
    # ---------------------------------------------------------
    plt.figure(figsize=(10, 6))
    plt.plot(nodes, kruskal_ms, label='Kruskal', marker='o', color='#e74c3c', linewidth=2)
    plt.plot(nodes, prim_ms, label='Prim', marker='s', color='#3498db', linewidth=2)
    plt.title('Time vs Size (Liniar)', fontsize=14, fontweight='bold')
    plt.xlabel('Număr de Noduri (|V|)')
    plt.ylabel('Timp de execuție (ms)')
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.legend()
    if save:
        plt.savefig("plots/time_vs_size.png", dpi=300, bbox_inches='tight')
        print("✅ Salvat: plots/time_vs_size.png")
    plt.close()

    # ---------------------------------------------------------
    # 2. loglog_average.png (Scară Log-Log pentru complexitate)
    # ---------------------------------------------------------
    plt.figure(figsize=(10, 6))
    plt.loglog(nodes, kruskal_ms, label='Kruskal', marker='o', color='#e74c3c', linewidth=2, base=10)
    plt.loglog(nodes, prim_ms, label='Prim', marker='s', color='#3498db', linewidth=2, base=10)
    plt.title('Time vs Size (Log-Log Scale)', fontsize=14, fontweight='bold')
    plt.xlabel('Număr de Noduri (|V|) - Log10')
    plt.ylabel('Timp de execuție (ms) - Log10')
    plt.grid(True, which="both", linestyle='--', alpha=0.6)
    plt.legend()
    if save:
        plt.savefig("plots/loglog_average.png", dpi=300, bbox_inches='tight')
        print("✅ Salvat: plots/loglog_average.png")
    plt.close()

    # ---------------------------------------------------------
    # 3. bar_comparison.png (Grafic cu bare pentru eșantioane)
    # ---------------------------------------------------------
    # Alegem doar câteva puncte (ex: ultimele 5-6) ca să nu se aglomereze barele
    sample_nodes = nodes[-6:] if len(nodes) >= 6 else nodes
    sample_k = kruskal_ms[-6:] if len(kruskal_ms) >= 6 else kruskal_ms
    sample_p = prim_ms[-6:] if len(prim_ms) >= 6 else prim_ms

    x = np.arange(len(sample_nodes))
    width = 0.35

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar(x - width/2, sample_k, width, label='Kruskal', color='#e74c3c')
    ax.bar(x + width/2, sample_p, width, label='Prim', color='#3498db')

    ax.set_title('Comparație directă pe grafuri mari (Bar Chart)', fontsize=14, fontweight='bold')
    ax.set_xlabel('Număr de Noduri (|V|)')
    ax.set_ylabel('Timp de execuție (ms)')
    ax.set_xticks(x)
    ax.set_xticklabels(sample_nodes)
    ax.legend()
    ax.grid(axis='y', linestyle='--', alpha=0.6)
    
    if save:
        plt.savefig("plots/bar_comparison.png", dpi=300, bbox_inches='tight')
        print("✅ Salvat: plots/bar_comparison.png")
    plt.close()

    print("\nToate graficele din suită au fost generate în folderul 'plots/'.")

def main() -> None:
    parser = argparse.ArgumentParser(description="MST Animated Visualizer & Plotter – Lab 7")
    parser.add_argument("--algo", nargs="*", default=list(ALGO_MAP.keys()),
                        choices=list(ALGO_MAP.keys()),
                        help="Algorithms to animate (default: both)")
    parser.add_argument("--n",     type=int, default=10,
                        help="Number of nodes (default 10)")
    parser.add_argument("--speed", type=int, default=600,
                        help="Frame interval ms (lower = faster, default 600)")
    parser.add_argument("--save",  action="store_true",
                        help="Save animations/plots to ./plots/")
    parser.add_argument("--seed",  type=int, default=42,
                        help="Random seed (default 42)")
    parser.add_argument("--file",  type=str, default=None,
                        help="Path to a custom graph file")
                        
    # -------- ARGUMENT NOU --------
    parser.add_argument("--plot",  action="store_true",
                        help="Generates the empirical analysis plot from results.csv")
    # ------------------------------

    args = parser.parse_args()

    # Dacă utilizatorul vrea doar graficul, rulăm graficul și ne oprim:
    if args.plot:
        print("=" * 50)
        print("  Generare Grafic Analiză Empirică")
        print("=" * 50)
        plot_empirical_data("results.csv", args.save)
        return  # Oprim execuția aici, nu mai rulăm animația

    # ... restul codului din main() (partea cu G, pos = ... și animate_graph rămâne la fel)

if __name__ == "__main__":
    main()