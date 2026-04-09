from __future__ import annotations

import argparse
import math
import os
import sys
from collections import deque
from typing import Dict, Generator, List, Optional, Tuple

import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.patches as mpatches
from matplotlib.lines import Line2D
import numpy as np

from main import Graph

CLR_DEFAULT   = "#3498db"
CLR_FRONTIER  = "#e74c3c"
CLR_VISITING  = "#f1c40f"
CLR_VISITED   = "#2ecc71"
CLR_START     = "#ffffff"
CLR_EDGE_DEF  = "#95a5a6"
CLR_EDGE_TREE = "#e67e22"
CLR_BG        = "#1e1e2e"
CLR_TEXT      = "#cdd6f4"
CLR_DEPTH     = "#9b59b6"

Frame = Tuple[Dict[int, str], Dict[Tuple[int, int], str], str, str]

def input_from_terminal() -> Graph:
    print("\n" + "═" * 50)
    print("  INTRODUCERE GRAF MANUAL")
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

    g = Graph(n)
    print(f"\nNoduri: 0 … {n - 1}")
    print("Introdu muchii ca 'u v' (ex: 0 1).")
    print("Apasă Enter pe o linie goală pentru a termina.\n")

    edge_count = 0
    while True:
        raw = input(f"  Muchie {edge_count + 1}: ").strip()
        if raw == "":
            break
        parts = raw.split()
        if len(parts) != 2:
            print("  ✗ Format greșit. Exemplu: 0 1")
            continue
        try:
            u, v = int(parts[0]), int(parts[1])
        except ValueError:
            print("  ✗ Nodurile trebuie să fie numere întregi.")
            continue
        if not (0 <= u < n and 0 <= v < n):
            print(f"  ✗ Nodurile trebuie între 0 și {n - 1}.")
            continue
        if u == v:
            print("  ✗ Bucle auto-referențiale nu sunt permise.")
            continue
        g.add_edge(u, v)
        edge_count += 1
        print(f"  ✓ Adăugat: {u} — {v}")

    print(f"\n  Graf creat: {n} noduri, {g.m} muchii.")
    return g


def input_from_file(path: str) -> Graph:
    if not os.path.exists(path):
        print(f"✗ Fișierul '{path}' nu a fost găsit.")
        sys.exit(1)

    with open(path) as f:
        lines = [l.strip() for l in f if l.strip() and not l.startswith("#")]

    if not lines:
        print("✗ Fișierul este gol.")
        sys.exit(1)

    n = int(lines[0])
    g = Graph(n)
    for line in lines[1:]:
        parts = line.split()
        if len(parts) >= 2:
            u, v = int(parts[0]), int(parts[1])
            g.add_edge(u, v)

    print(f"  ✓ Încărcat din '{path}': {n} noduri, {g.m} muchii.")
    return g


def input_from_args(arg: str) -> Graph:
    try:
        head, body = arg.split(":", 1)
        n = int(head.strip())
        g = Graph(n)
        for token in body.split(","):
            token = token.strip()
            if not token:
                continue
            parts = token.replace("-", " ").split()
            u, v  = int(parts[0]), int(parts[1])
            g.add_edge(u, v)
        print(f"  ✓ Graf din --custom: {n} noduri, {g.m} muchii.")
        return g
    except Exception as e:
        print(f"✗ Format --custom greșit: {e}")
        print("  Exemplu corect: --custom \"6: 0-1, 1-2, 2-3, 0-4, 4-5\"")
        sys.exit(1)

def spring_layout(g: Graph, iterations: int = 150) -> Dict[int, Tuple[float, float]]:
    rng = np.random.default_rng(42)
    pos = {i: rng.uniform(-1, 1, 2) for i in range(g.n)}
    k   = 1.0 / math.sqrt(max(g.n, 1))

    for _ in range(iterations):
        disp = {i: np.zeros(2) for i in range(g.n)}
        nodes = list(range(g.n))
        for i in nodes:
            for j in nodes:
                if i == j:
                    continue
                delta = pos[i] - pos[j]
                dist  = max(np.linalg.norm(delta), 1e-6)
                disp[i] += (delta / dist) * (k * k / dist)
        for u in range(g.n):
            for v in g.adj[u]:
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
        pos[i] = (
            2 * (pos[i][0] - min(xs)) / max(mx, 1e-6) - 1,
            2 * (pos[i][1] - min(ys)) / max(mn, 1e-6) - 1,
        )
    return pos


def circle_layout(n: int) -> Dict[int, Tuple[float, float]]:
    return {
        i: (math.cos(2 * math.pi * i / n - math.pi / 2),
            math.sin(2 * math.pi * i / n - math.pi / 2))
        for i in range(n)
    }


def grid_layout(rows: int, cols: int) -> Dict[int, Tuple[float, float]]:
    return {
        r * cols + c: (2 * c / max(cols - 1, 1) - 1,
                       1 - 2 * r / max(rows - 1, 1))
        for r in range(rows)
        for c in range(cols)
    }


def bfs_gen(g: Graph, start: int = 0) -> Generator[Frame, None, None]:
    n_colors = {i: CLR_DEFAULT for i in range(g.n)}
    e_colors = {(min(u, v), max(u, v)): CLR_EDGE_DEF
                for u in range(g.n) for v in g.adj[u] if u < v}
    visited  = [False] * g.n

    n_colors[start] = CLR_START
    yield dict(n_colors), dict(e_colors), "queue: []", f"Start BFS din nodul {start}"

    visited[start] = True
    queue: deque = deque([start])
    n_colors[start] = CLR_FRONTIER

    while queue:
        u = queue.popleft()
        n_colors[u] = CLR_VISITING
        yield dict(n_colors), dict(e_colors), f"queue: {list(queue)}", f"Procesez nodul {u}"

        for v in g.adj[u]:
            edge = (min(u, v), max(u, v))
            if not visited[v]:
                visited[v] = True
                n_colors[v] = CLR_FRONTIER
                e_colors[edge] = CLR_EDGE_TREE
                queue.append(v)
                yield (dict(n_colors), dict(e_colors),
                       f"queue: {list(queue)}", f"  {u} → {v}  (adaug {v} în coadă)")

        n_colors[u] = CLR_VISITED
        yield dict(n_colors), dict(e_colors), f"queue: {list(queue)}", f"Nodul {u} vizitat ✓"

    yield dict(n_colors), dict(e_colors), "queue: []", "✓ BFS complet!"


def dfs_gen(g: Graph, start: int = 0) -> Generator[Frame, None, None]:
    n_colors = {i: CLR_DEFAULT for i in range(g.n)}
    e_colors = {(min(u, v), max(u, v)): CLR_EDGE_DEF
                for u in range(g.n) for v in g.adj[u] if u < v}
    visited  = [False] * g.n

    n_colors[start] = CLR_START
    yield dict(n_colors), dict(e_colors), "stack: []", f"Start DFS din nodul {start}"

    stack = [start]
    n_colors[start] = CLR_FRONTIER
    yield dict(n_colors), dict(e_colors), f"stack: {stack}", f"Push {start} în stivă"

    while stack:
        u = stack.pop()
        if visited[u]:
            yield (dict(n_colors), dict(e_colors),
                   f"stack: {stack}", f"Sar peste {u} (deja vizitat)")
            continue

        visited[u] = True
        n_colors[u] = CLR_VISITING
        yield dict(n_colors), dict(e_colors), f"stack: {stack}", f"Vizitez nodul {u}"

        for v in g.adj[u]:
            edge = (min(u, v), max(u, v))
            if not visited[v]:
                n_colors[v] = CLR_FRONTIER
                e_colors[edge] = CLR_EDGE_TREE
                stack.append(v)
                yield (dict(n_colors), dict(e_colors),
                       f"stack: {stack}", f"  {u} → {v}  (push {v})")

        n_colors[u] = CLR_VISITED
        yield dict(n_colors), dict(e_colors), f"stack: {stack}", f"Nodul {u} vizitat ✓"

    yield dict(n_colors), dict(e_colors), "stack: []", "✓ DFS complet!"


def iddfs_gen(g: Graph, start: int = 0) -> Generator[Frame, None, None]:
    n_colors = {i: CLR_DEFAULT for i in range(g.n)}
    e_colors = {(min(u, v), max(u, v)): CLR_EDGE_DEF
                for u in range(g.n) for v in g.adj[u] if u < v}
    visited  = [False] * g.n

    n_colors[start] = CLR_START
    yield dict(n_colors), dict(e_colors), "limită adâncime: 0", f"Start IDDFS din nodul {start}"

    depth_limit   = 0
    total_visited = 0

    while True:
        found_deeper = False
        for i in range(g.n):
            if not visited[i]:
                n_colors[i] = CLR_DEFAULT

        yield (dict(n_colors), dict(e_colors),
               f"limită adâncime: {depth_limit}",
               f"── Iterația nouă — limită adâncime = {depth_limit} ──")

        iter_vis = [False] * g.n
        stack: List[Tuple[int, int]] = [(start, 0)]

        while stack:
            u, d = stack.pop()
            if iter_vis[u]:
                continue
            if d > depth_limit:
                found_deeper = True
                n_colors[u] = CLR_DEPTH
                yield (dict(n_colors), dict(e_colors),
                       f"limită adâncime: {depth_limit}",
                       f"  Nodul {u} la adâncime {d} > limită {depth_limit} — skip")
                n_colors[u] = CLR_DEFAULT if not visited[u] else CLR_VISITED
                continue

            iter_vis[u] = True
            if not visited[u]:
                visited[u] = True
                total_visited += 1
            n_colors[u] = CLR_VISITING
            yield (dict(n_colors), dict(e_colors),
                   f"limită adâncime: {depth_limit}",
                   f"  Vizitez nodul {u} la adâncime {d}")

            for v in g.adj[u]:
                edge = (min(u, v), max(u, v))
                if not iter_vis[v]:
                    if e_colors[edge] != CLR_EDGE_TREE:
                        e_colors[edge] = CLR_EDGE_TREE
                    stack.append((v, d + 1))

            n_colors[u] = CLR_VISITED
            yield (dict(n_colors), dict(e_colors),
                   f"limită adâncime: {depth_limit}",
                   f"  Nodul {u} marcat vizitat (total: {total_visited})")

        if not found_deeper:
            break
        depth_limit += 1

    yield dict(n_colors), dict(e_colors), "gata", f"✓ IDDFS complet! ({depth_limit} iterații)"

ALGO_MAP = {
    "bfs":   ("BFS — Breadth-First Search",       bfs_gen),
    "dfs":   ("DFS — Depth-First Search",         dfs_gen),
    "iddfs": ("IDDFS — Iterative Deepening DFS",  iddfs_gen),
}


def animate_traversal(name, generator_fn, g, pos, interval=400, save=False):
    frames: List[Frame] = list(generator_fn(g))
    if not frames:
        return

    node_ids = list(range(g.n))
    edges    = [(min(u, v), max(u, v)) for u in range(g.n) for v in g.adj[u] if u < v]

    xs = np.array([pos[i][0] for i in node_ids])
    ys = np.array([pos[i][1] for i in node_ids])

    fig, ax = plt.subplots(figsize=(13, 7))
    fig.patch.set_facecolor(CLR_BG)
    ax.set_facecolor(CLR_BG)
    ax.set_aspect("equal")
    ax.axis("off")

    node_size = max(250, 1200 // max(g.n, 1))
    font_size = max(7, 13 - g.n // 8)

    edge_lines: Dict[Tuple[int, int], Line2D] = {}
    for (u, v) in edges:
        line, = ax.plot(
            [pos[u][0], pos[v][0]], [pos[u][1], pos[v][1]],
            color=CLR_EDGE_DEF, linewidth=1.5, zorder=1, alpha=0.55,
        )
        edge_lines[(u, v)] = line

    scat = ax.scatter(xs, ys, s=node_size,
                      c=[frames[0][0][i] for i in node_ids],
                      zorder=3, edgecolors="#00000060", linewidths=1.0)

    label_texts = []
    for i in node_ids:
        t = ax.text(pos[i][0], pos[i][1], str(i),
                    ha="center", va="center",
                    fontsize=font_size, color="black",
                    fontweight="bold", zorder=4)
        label_texts.append(t)

    ax.set_title(name, fontsize=14, fontweight="bold", color=CLR_TEXT, pad=10)
    status_text  = ax.text(0.5, -0.04, "", transform=ax.transAxes,
                           ha="center", fontsize=10, color="#f5c211", fontweight="bold")
    frontier_txt = ax.text(0.01, 1.02, "", transform=ax.transAxes,
                           ha="left", fontsize=9, color=CLR_TEXT, alpha=0.85)
    counter_txt  = ax.text(0.99, 1.02, "", transform=ax.transAxes,
                           ha="right", fontsize=9, color=CLR_TEXT, alpha=0.6)

    legend_items = [
        mpatches.Patch(color=CLR_DEFAULT,  label="Nevizitat"),
        mpatches.Patch(color=CLR_FRONTIER, label="Frontieră (coadă/stivă)"),
        mpatches.Patch(color=CLR_VISITING, label="Se procesează"),
        mpatches.Patch(color=CLR_VISITED,  label="Vizitat"),
        mpatches.Patch(color=CLR_START,    label="Nod start"),
        Line2D([0], [0], color=CLR_EDGE_TREE, linewidth=2, label="Muchie arbore"),
    ]
    ax.legend(handles=legend_items, loc="upper right", fontsize=8,
              framealpha=0.3, labelcolor=CLR_TEXT, facecolor=CLR_BG)

    def update(fi: int):
        n_cols, e_cols, frontier, msg = frames[fi]
        for (u, v), line in edge_lines.items():
            c = e_cols.get((u, v), CLR_EDGE_DEF)
            line.set_color(c)
            line.set_linewidth(2.5 if c == CLR_EDGE_TREE else 1.5)
            line.set_alpha(0.9 if c == CLR_EDGE_TREE else 0.45)
        scat.set_facecolor([n_cols[i] for i in node_ids])
        status_text.set_text(msg)
        frontier_txt.set_text(frontier)
        counter_txt.set_text(f"pas {fi + 1}/{len(frames)}")
        return [scat, status_text, frontier_txt, counter_txt] + list(edge_lines.values())

    anim = animation.FuncAnimation(
        fig, update, frames=len(frames),
        interval=interval, blit=False, repeat=False,
    )

    if save:
        os.makedirs("plots", exist_ok=True)
        out = f"plots/{name.split('—')[0].strip().lower().replace(' ', '_')}.gif"
        print(f"  Salvez {out} …", end=" ", flush=True)
        anim.save(out, writer="pillow", fps=max(1, 1000 // interval))
        print("gata.")

    plt.tight_layout()
    plt.show()

def make_random_graph(n: int, extra: int = 4, rseed: int = 42) -> Graph:
    from random import Random
    r = Random(rseed)
    g = Graph(n)
    perm = list(range(n))
    r.shuffle(perm)
    for i in range(1, n):
        p = r.randint(0, i - 1)
        g.add_edge(perm[i], perm[p])
    for _ in range(extra):
        u, v = r.randint(0, n - 1), r.randint(0, n - 1)
        if u != v:
            g.add_edge(u, v)
    return g


def make_grid_graph(rows: int, cols: int) -> Graph:
    g = Graph(rows * cols)
    for r in range(rows):
        for c in range(cols):
            node = r * cols + c
            if c + 1 < cols: g.add_edge(node, node + 1)
            if r + 1 < rows: g.add_edge(node, node + cols)
    return g

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Vizualizator traversare graf — BFS / DFS / IDDFS",
        formatter_class=argparse.RawTextHelpFormatter,
        epilog="""
EXEMPLE:
  # Graf random (implicit)
  python animate.py

  # Introduci singur noduri și muchii în terminal
  python animate.py --input terminal

  # Citire din fișier (vezi format mai jos)
  python animate.py --input fisier --file graful_meu.txt

  # Specifici graful direct în comandă
  python animate.py --custom "6: 0-1, 1-2, 2-3, 0-4, 4-5"

  # Grid 4x5
  python animate.py --grid 4x5

  # Doar BFS, mai lent, start din nodul 3
  python animate.py --input terminal --algo bfs --start 3 --speed 600

FORMAT FIȘIER (graful_meu.txt):
  # comentariu (ignorat)
  6          <- numărul de noduri
  0 1        <- muchie între 0 și 1
  1 2
  2 3
  0 4
  4 5
""")

    parser.add_argument(
        "--input", choices=["random", "terminal", "fisier"], default="random",
        help="Sursa grafului:\n"
             "  random   — generat automat (implicit)\n"
             "  terminal — introduci tu nodurile și muchiile\n"
             "  fisier   — citit dintr-un fișier .txt")
    parser.add_argument("--file",   type=str, default=None,
                        help="Calea fișierului (folosit cu --input fisier)")
    parser.add_argument("--custom", type=str, default=None,
                        help="Graf direct în linie de comandă: \"N: u-v, u-v, ...\"")
    parser.add_argument("--grid",   type=str, default=None,
                        help="Graf grid: --grid ROWSxCOLS  (ex: --grid 4x5)")
    parser.add_argument("--n",      type=int, default=12,
                        help="Noduri pentru --input random (default 12)")
    parser.add_argument("--extra",  type=int, default=4,
                        help="Muchii extra pentru --input random (default 4)")
    parser.add_argument("--algo",   nargs="*", default=list(ALGO_MAP.keys()),
                        choices=list(ALGO_MAP.keys()),
                        help="Algoritmi de animat (default: toți)")
    parser.add_argument("--start",  type=int, default=0,
                        help="Nodul de start (default 0)")
    parser.add_argument("--layout", choices=["spring", "circle"], default="spring",
                        help="Layout noduri: spring (default) sau circle")
    parser.add_argument("--speed",  type=int, default=400,
                        help="Interval cadre în ms (mai mic = mai rapid, default 400)")
    parser.add_argument("--save",   action="store_true",
                        help="Salvează animațiile ca .gif în plots/")
    parser.add_argument("--seed",   type=int, default=42)
    args = parser.parse_args()

    if args.custom:
        g = input_from_args(args.custom)
    elif args.grid:
        rows, cols = map(int, args.grid.lower().split("x"))
        g = make_grid_graph(rows, cols)
        print(f"  Grid {rows}×{cols}: {g.n} noduri, {g.m} muchii.")
    elif args.input == "terminal":
        g = input_from_terminal()
    elif args.input == "fisier":
        if not args.file:
            print("✗ Specifică fișierul cu --file <cale>")
            sys.exit(1)
        g = input_from_file(args.file)
    else:
        g = make_random_graph(args.n, args.extra, args.seed)
        print(f"  Graf random: {g.n} noduri, {g.m} muchii.")

    if not (0 <= args.start < g.n):
        print(f"✗ Nodul de start {args.start} nu există (noduri: 0 … {g.n - 1}).")
        sys.exit(1)

    if args.grid:
        rows, cols = map(int, args.grid.lower().split("x"))
        pos = grid_layout(rows, cols)
    elif args.layout == "circle":
        pos = circle_layout(g.n)
    else:
        pos = spring_layout(g)

    print("\n  Structura grafului:")
    for u in range(g.n):
        neighbors = g.adj[u]
        print(f"    Nod {u}: {neighbors}")

    print(f"\n  Nod start: {args.start}  |  viteză: {args.speed}ms/cadru")
    print("=" * 50)

    for key in args.algo:
        name, gen_fn = ALGO_MAP[key]
        print(f"\n▶  {name}")

        def make_gen(graph, _fn=gen_fn, _s=args.start):
            return _fn(graph, _s)

        animate_traversal(name, make_gen, g, pos,
                          interval=args.speed, save=args.save)

    print("\nToate animațiile gata.")


if __name__ == "__main__":
    main()