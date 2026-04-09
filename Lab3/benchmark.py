from __future__ import annotations

import os
import subprocess
import sys
import platform
from typing import Dict, List, Tuple

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

CSV_FILE   = "results.csv"
CPP_SRC    = "algorithms.cpp"
EXECUTABLE = "algorithms.exe" if platform.system() == "Windows" else "./algorithms"
OUT_DIR    = "plots"

ALGO_COLS = {
    "BFS":       ("bfs_us",     "bfs_nodes",     "bfs_edges",     "bfs_mem"),
    "DFS":       ("dfs_us",     "dfs_nodes",     "dfs_edges",     "dfs_mem"),
    "IDDFS":     ("iddfs_us",   "iddfs_nodes",   "iddfs_edges",   "iddfs_mem"),
    "BFS (opt)": ("bfs_opt_us", "bfs_opt_nodes", "bfs_opt_edges", "bfs_opt_mem"),
    "DFS (opt)": ("dfs_opt_us", "dfs_opt_nodes", "dfs_opt_edges", "dfs_opt_mem"),
}

COLORS = {
    "BFS":       "#2980b9",
    "DFS":       "#e74c3c",
    "IDDFS":     "#8e44ad",
    "BFS (opt)": "#27ae60",
    "DFS (opt)": "#e67e22",
}
MARKERS = {
    "BFS":       "o",
    "DFS":       "s",
    "IDDFS":     "D",
    "BFS (opt)": "^",
    "DFS (opt)": "x",
}


def ensure_csv() -> None:
    if os.path.exists(CSV_FILE):
        print(f"  ✓ {CSV_FILE} găsit — sar compilarea C++.")
        return

    print("  CSV lipsește — compilez și rulez C++...")

    # Compilare
    compile_cmd = f"g++ -O2 -std=c++17 -o algorithms {CPP_SRC}"
    print(f"  $ {compile_cmd}")
    ret = subprocess.run(compile_cmd, shell=True)
    if ret.returncode != 0:
        print("✗ Compilare eșuată. Asigură-te că g++ e instalat.")
        sys.exit(1)
    print("  ✓ Compilat.")

    # Rulare
    exe = "algorithms.exe" if platform.system() == "Windows" else "./algorithms"
    print(f"  $ {exe}")
    ret = subprocess.run(exe, shell=True)
    if ret.returncode != 0:
        print("✗ Executabilul a eșuat.")
        sys.exit(1)
    print("  ✓ C++ rulat, CSV generat.")


# ─────────────────────────────────────────────────────────────
#  Step 2: parsare CSV
# ─────────────────────────────────────────────────────────────

def load_csv(path: str) -> List[dict]:
    rows = []
    with open(path) as f:
        header = f.readline().strip().split(",")
        for line in f:
            line = line.strip()
            if not line:
                continue
            parts = line.split(",")
            row = {}
            for key, val in zip(header, parts):
                try:
                    row[key] = int(val)
                except ValueError:
                    row[key] = val
            rows.append(row)
    return rows


def group_by_dist(rows: List[dict]) -> Dict[str, List[dict]]:
    groups: Dict[str, List[dict]] = {}
    for r in rows:
        groups.setdefault(r["dist"], []).append(r)
    return groups


def print_summary(rows: List[dict]) -> None:
    groups = group_by_dist(rows)
    largest_n = max(r["n"] for r in rows)

    print(f"\n  SUMMARY TABLE — n = {largest_n:,d}")
    algo_names = list(ALGO_COLS.keys())
    header = f"{'Distribution':<16s}" + "".join(f"{a:>14s}" for a in algo_names)
    print(header)
    print("─" * len(header))

    for dist, dist_rows in groups.items():
        last = max(dist_rows, key=lambda r: r["n"])
        row_str = f"{dist:<16s}"
        for algo, (col_us, *_) in ALGO_COLS.items():
            t_us = last.get(col_us, 0)
            row_str += f"{t_us / 1e6:>14.6f}"
        print(row_str)

    print("\n  RANKING (fastest → slowest) la n mai mare:")
    print("─" * 70)
    for dist, dist_rows in groups.items():
        last = max(dist_rows, key=lambda r: r["n"])
        pairs = [(algo, last.get(ALGO_COLS[algo][0], 0)) for algo in algo_names]
        pairs.sort(key=lambda p: p[1])
        ranking = "  >  ".join(f"{a}({t/1e6:.4f}s)" for a, t in pairs)
        print(f"  {dist:<14s}: {ranking}")
    print()


def plot_results(rows: List[dict]) -> None:
    os.makedirs(OUT_DIR, exist_ok=True)
    groups     = group_by_dist(rows)
    dist_names = list(groups.keys())
    algo_names = list(ALGO_COLS.keys())

    def get_times(dist: str, algo: str) -> Tuple[List[int], List[float]]:
        col = ALGO_COLS[algo][0]
        data = sorted(groups[dist], key=lambda r: r["n"])
        return [r["n"] for r in data], [r.get(col, 0) / 1e6 for r in data]

    def get_mem(dist: str, algo: str) -> Tuple[List[int], List[int]]:
        col = ALGO_COLS[algo][3]
        data = sorted(groups[dist], key=lambda r: r["n"])
        return [r["n"] for r in data], [r.get(col, 0) for r in data]

    n_dist = len(dist_names)
    cols   = 3
    rws    = (n_dist + cols - 1) // cols
    fig, axes = plt.subplots(rws, cols, figsize=(18, 5 * rws))
    axes = axes.flatten()

    for idx, dist in enumerate(dist_names):
        ax = axes[idx]
        for algo in algo_names:
            ns, ts = get_times(dist, algo)
            ax.plot(ns, ts, marker=MARKERS[algo], color=COLORS[algo],
                    label=algo, linewidth=2, markersize=6)
        ax.set_title(dist.replace("_", " ").title(), fontsize=13, fontweight="bold")
        ax.set_xlabel("Input size (n)")
        ax.set_ylabel("Timp (secunde)")
        ax.legend(fontsize=8)
        ax.grid(True, alpha=0.3)

    for i in range(n_dist, len(axes)):
        axes[i].set_visible(False)

    fig.suptitle("Traversare Graf — Timp vs Dimensiune Input  [C++ timings]",
                 fontsize=16, fontweight="bold", y=1.01)
    fig.tight_layout()
    path = os.path.join(OUT_DIR, "time_vs_size.png")
    fig.savefig(path, dpi=150, bbox_inches="tight")
    print(f"  ✓ {path}")
    plt.close(fig)

    largest_n = max(r["n"] for r in rows)
    fig, ax = plt.subplots(figsize=(14, 7))
    x     = np.arange(len(dist_names))
    width = 0.15

    for i, algo in enumerate(algo_names):
        col = ALGO_COLS[algo][0]
        times = []
        for dist in dist_names:
            last = max(groups[dist], key=lambda r: r["n"])
            times.append(last.get(col, 0) / 1e6)
        ax.bar(x + i * width, times, width,
               label=algo, color=COLORS[algo], alpha=0.85)

    ax.set_xlabel("Distribuție", fontsize=12)
    ax.set_ylabel("Timp (secunde)", fontsize=12)
    ax.set_title(f"Comparație Algoritmi — n = {largest_n:,d}  [C++]",
                 fontsize=14, fontweight="bold")
    ax.set_xticks(x + width * (len(algo_names) - 1) / 2)
    ax.set_xticklabels([d.replace("_", " ").title() for d in dist_names])
    ax.legend()
    ax.grid(True, axis="y", alpha=0.3)
    fig.tight_layout()
    path = os.path.join(OUT_DIR, "bar_comparison.png")
    fig.savefig(path, dpi=150, bbox_inches="tight")
    print(f"  ✓ {path}")
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(10, 7))
    all_sizes = sorted(set(r["n"] for r in rows))

    for algo in algo_names:
        col = ALGO_COLS[algo][0]
        avg_times = []
        for n in all_sizes:
            vals = [r.get(col, 0) / 1e6
                    for r in rows if r["n"] == n]
            avg_times.append(sum(vals) / max(len(vals), 1))
        ax.loglog(all_sizes, avg_times,
                  marker=MARKERS[algo], color=COLORS[algo],
                  label=algo, linewidth=2, markersize=7)

    ref_n  = np.array(all_sizes, dtype=float)
    first_col = ALGO_COLS["BFS"][0]
    first_t   = [r.get(first_col, 0) / 1e6 for r in rows if r["n"] == all_sizes[0]]
    scale     = (sum(first_t) / len(first_t)) / all_sizes[0]
    ax.loglog(all_sizes, scale * ref_n, "--", color="gray", alpha=0.5, label="O(n) ref")

    ax.set_xlabel("Input size (n)", fontsize=12)
    ax.set_ylabel("Timp (secunde)", fontsize=12)
    ax.set_title("Timp Mediu — Scară Log-Log  [C++]",
                 fontsize=14, fontweight="bold")
    ax.legend()
    ax.grid(True, alpha=0.3, which="both")
    fig.tight_layout()
    path = os.path.join(OUT_DIR, "loglog_average.png")
    fig.savefig(path, dpi=150, bbox_inches="tight")
    print(f"  ✓ {path}")
    plt.close(fig)

    cmp_algos = [a for a in algo_names if a != "BFS"]
    ref_col   = ALGO_COLS["BFS"][0]
    fig, ax   = plt.subplots(figsize=(12, 5))
    matrix    = []

    for algo in cmp_algos:
        col = ALGO_COLS[algo][0]
        row_vals = []
        for dist in dist_names:
            last     = max(groups[dist], key=lambda r: r["n"])
            t_algo   = max(last.get(col, 1), 1)
            t_ref    = max(last.get(ref_col, 1), 1)
            row_vals.append(t_algo / t_ref)
        matrix.append(row_vals)

    matrix_np = np.array(matrix)
    im = ax.imshow(matrix_np, cmap="RdYlGn_r", aspect="auto")
    ax.set_xticks(range(len(dist_names)))
    ax.set_xticklabels([d.replace("_"," ").title() for d in dist_names])
    ax.set_yticks(range(len(cmp_algos)))
    ax.set_yticklabels(cmp_algos)
    for i in range(len(cmp_algos)):
        for j in range(len(dist_names)):
            ax.text(j, i, f"{matrix_np[i,j]:.1f}×",
                    ha="center", va="center", fontsize=11, fontweight="bold")
    plt.colorbar(im, ax=ax, label="Slowdown față de BFS")
    ax.set_title(f"Factor Încetinire față de BFS — n = {largest_n:,d}  [C++]",
                 fontsize=13, fontweight="bold")
    fig.tight_layout()
    path = os.path.join(OUT_DIR, "heatmap_slowdown.png")
    fig.savefig(path, dpi=150, bbox_inches="tight")
    print(f"  ✓ {path}")
    plt.close(fig)

    fig, axes2 = plt.subplots(1, 2, figsize=(16, 6))
    for ax_i, dist in enumerate(["sparse", "dense"]):
        ax = axes2[ax_i]
        for algo in algo_names:
            ns, mems = get_mem(dist, algo)
            ax.plot(ns, mems, marker=MARKERS[algo], color=COLORS[algo],
                    label=algo, linewidth=2, markersize=6)
        ax.set_title(f"Memorie de Vârf — {dist.title()}  [C++]",
                     fontsize=12, fontweight="bold")
        ax.set_xlabel("Input size (n)")
        ax.set_ylabel("Vârf coadă / stivă (elemente)")
        ax.legend(fontsize=9)
        ax.grid(True, alpha=0.3)

    fig.suptitle("Utilizare Memorie în Traversare  [C++]",
                 fontsize=14, fontweight="bold")
    fig.tight_layout()
    path = os.path.join(OUT_DIR, "memory_usage.png")
    fig.savefig(path, dpi=150, bbox_inches="tight")
    print(f"  ✓ {path}")
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(12, 6))
    for algo in ["BFS", "DFS", "IDDFS"]:
        col = ALGO_COLS[algo][2]
        ns, edges = zip(*sorted(
            [(r["n"], r.get(col, 0)) for r in rows if r["dist"] == "sparse"],
            key=lambda x: x[0]
        ))
        ax.plot(ns, edges, marker=MARKERS[algo], color=COLORS[algo],
                label=algo, linewidth=2, markersize=6)

    theory_ns  = sorted(set(r["n"] for r in rows if r["dist"] == "sparse"))
    theory_vals = [next(r["m"] + r["n"] for r in rows
                        if r["dist"] == "sparse" and r["n"] == n)
                   for n in theory_ns]
    ax.plot(theory_ns, theory_vals, "--", color="gray", alpha=0.6, label="O(V+E) teoretic")

    ax.set_xlabel("Input size (n)", fontsize=12)
    ax.set_ylabel("Muchii verificate", fontsize=12)
    ax.set_title("Muchii Verificate vs n  (graf rar)  [C++]",
                 fontsize=13, fontweight="bold")
    ax.legend()
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    path = os.path.join(OUT_DIR, "edge_checks.png")
    fig.savefig(path, dpi=150, bbox_inches="tight")
    print(f"  ✓ {path}")
    plt.close(fig)


if __name__ == "__main__":
    print("=" * 64)
    print("  Laboratory Nr. 3 – Plots din date C++")
    print("=" * 64)

    ensure_csv()

    print(f"\n  Citesc {CSV_FILE} …")
    rows = load_csv(CSV_FILE)
    print(f"  ✓ {len(rows)} rânduri încărcate.")

    print_summary(rows)

    print("\nGenerez ploturi …")
    plot_results(rows)
    print("\nGata!")
