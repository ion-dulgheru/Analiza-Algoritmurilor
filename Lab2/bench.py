from __future__ import annotations
import os
import sys
from random import randint, seed
from timeit import repeat
from typing import Callable, Dict, List, Tuple
sys.setrecursionlimit(200_000)

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from main import merge_sort, quick_sort, heap_sort, patience_sort

ALGORITHMS: Dict[str, Callable] = {
    "Quick Sort":     quick_sort,
    "Merge Sort":     merge_sort,
    "Heap Sort":      heap_sort,
    "Patience Sort":  patience_sort,
    "Python sorted":  sorted,            
}

SIZES: List[int] = [500, 1_000, 2_500, 5_000, 10_000, 25_000]

REPEATS = 3        # timeit repeats  (take min)
NUMBER  = 1        # executions per repeat



def _nearly_sorted(n: int) -> List[int]:
    a = list(range(n))
    swaps = max(1, n // 100)
    for _ in range(swaps):
        i, j = randint(0, n - 1), randint(0, n - 1)
        a[i], a[j] = a[j], a[i]
    return a


DISTRIBUTIONS: Dict[str, Callable[[int], List[int]]] = {
    "random":        lambda n: [randint(0, 10**6) for _ in range(n)],
    "sorted":        lambda n: list(range(n)),
    "reversed":      lambda n: list(range(n, 0, -1)),
    "nearly_sorted": _nearly_sorted,
    "many_dupes":    lambda n: [randint(0, max(1, n // 10)) for _ in range(n)],
}

COLORS = {
    "Quick Sort":    "#e74c3c",
    "Merge Sort":    "#27ae60",
    "Heap Sort":     "#2980b9",
    "Patience Sort": "#8e44ad",
    "Python sorted": "#7f8c8d",
}
MARKERS = {
    "Quick Sort":    "o",
    "Merge Sort":    "s",
    "Heap Sort":     "^",
    "Patience Sort": "D",
    "Python sorted": "x",
}


def time_algorithm(func: Callable, arr: List[int]) -> float:
    glb = {"func": func, "arr": arr}
    times = repeat("func(arr[:])", repeat=REPEATS, number=NUMBER, globals=glb)
    return min(times) / NUMBER


def run_benchmarks() -> Dict[Tuple[str, str, int], float]:
    seed(42)
    results: Dict[Tuple[str, str, int], float] = {}

    total = len(DISTRIBUTIONS) * len(SIZES)
    done  = 0

    for dist_name, gen_fn in DISTRIBUTIONS.items():
  
        print(f"\n  Distribution: {dist_name}")
       

        for n in SIZES:
            arr = gen_fn(n)
            ref = sorted(arr)
            done += 1
            pct = done / total * 100
            print(f"\n  n = {n:>7,d}   ({pct:5.1f} % done)")

            for algo_name, algo_fn in ALGORITHMS.items():
                out = algo_fn(arr[:])
                assert out == ref, f"FAIL: {algo_name} on {dist_name}, n={n}"

                t = time_algorithm(algo_fn, arr)
                results[(algo_name, dist_name, n)] = t
                print(f"    {algo_name:<16s}  {t:>10.6f} s")

    return results


def print_summary_table(results: dict) -> None:
    largest = max(SIZES)
    algo_names = list(ALGORITHMS.keys())
    dist_names = list(DISTRIBUTIONS.keys())

  
    print(f"  SUMMARY TABLE — n = {largest:,d}")
   
    header = f"{'Distribution':<16s}" + "".join(f"{a:>16s}" for a in algo_names)
    print(header)
    print("─" * len(header))
    for d in dist_names:
        row = f"{d:<16s}"
        for a in algo_names:
            t = results.get((a, d, largest), 0)
            row += f"{t:>16.6f}"
        print(row)
    print()

    print("  RANKING (fastest → slowest):")
    print("─" * 64)
    for d in dist_names:
        pairs = [(a, results.get((a, d, largest), 0)) for a in algo_names]
        pairs.sort(key=lambda p: p[1])
        ranking = "  >  ".join(f"{a} ({t:.4f}s)" for a, t in pairs)
        print(f"  {d:<16s}: {ranking}")
    print()


def plot_results(results: dict, out_dir: str = "plots") -> None:
    os.makedirs(out_dir, exist_ok=True)
    algo_names = list(ALGORITHMS.keys())
    dist_names = list(DISTRIBUTIONS.keys())

    n_dist = len(dist_names)
    cols = 3
    rows = (n_dist + cols - 1) // cols
    fig, axes = plt.subplots(rows, cols, figsize=(18, 5 * rows))
    axes = axes.flatten()

    for idx, dist in enumerate(dist_names):
        ax = axes[idx]
        for algo in algo_names:
            times = [results.get((algo, dist, n), 0) for n in SIZES]
            ax.plot(SIZES, times,
                    marker=MARKERS[algo], color=COLORS[algo],
                    label=algo, linewidth=2, markersize=6)
        ax.set_title(dist.replace("_", " ").title(),
                     fontsize=13, fontweight="bold")
        ax.set_xlabel("Input size (n)")
        ax.set_ylabel("Time (seconds)")
        ax.legend(fontsize=8)
        ax.grid(True, alpha=0.3)

    for i in range(n_dist, len(axes)):
        axes[i].set_visible(False)

    fig.suptitle("Sorting Algorithms — Time vs Input Size",
                 fontsize=16, fontweight="bold", y=1.01)
    fig.tight_layout()
    path = os.path.join(out_dir, "time_vs_size.png")
    fig.savefig(path, dpi=150, bbox_inches="tight")
    print(f"  ✓ {path}")
    plt.close(fig)

    largest = max(SIZES)
    fig, ax = plt.subplots(figsize=(14, 7))
    x = np.arange(len(dist_names))
    width = 0.15

    for i, algo in enumerate(algo_names):
        times = [results.get((algo, d, largest), 0) for d in dist_names]
        ax.bar(x + i * width, times, width,
               label=algo, color=COLORS[algo])

    ax.set_xlabel("Distribution", fontsize=12)
    ax.set_ylabel("Time (seconds)", fontsize=12)
    ax.set_title(f"Algorithm Comparison — n = {largest:,d}",
                 fontsize=14, fontweight="bold")
    ax.set_xticks(x + width * (len(algo_names) - 1) / 2)
    ax.set_xticklabels([d.replace("_", " ").title() for d in dist_names])
    ax.legend()
    ax.grid(True, axis="y", alpha=0.3)
    fig.tight_layout()
    path = os.path.join(out_dir, "bar_comparison.png")
    fig.savefig(path, dpi=150, bbox_inches="tight")
    print(f"  ✓ {path}")
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(10, 7))
    for algo in algo_names:
        avg_times = []
        for n in SIZES:
            ts = [results.get((algo, d, n), 0) for d in dist_names]
            avg_times.append(sum(ts) / len(ts))
        ax.loglog(SIZES, avg_times,
                  marker=MARKERS[algo], color=COLORS[algo],
                  label=algo, linewidth=2, markersize=7)

    ref_n = np.array(SIZES, dtype=float)
    first_avg = sum(results.get((algo_names[0], d, SIZES[0]), 0)
                    for d in dist_names) / len(dist_names)
    scale = first_avg / (ref_n[0] * np.log2(ref_n[0]))
    ax.loglog(SIZES, scale * ref_n * np.log2(ref_n),
              "--", color="gray", alpha=0.5, label="O(n log n) ref")

    ax.set_xlabel("Input size (n)", fontsize=12)
    ax.set_ylabel("Time (seconds)", fontsize=12)
    ax.set_title("Average Time Across Distributions (Log-Log Scale)",
                 fontsize=14, fontweight="bold")
    ax.legend()
    ax.grid(True, alpha=0.3, which="both")
    fig.tight_layout()
    path = os.path.join(out_dir, "loglog_average.png")
    fig.savefig(path, dpi=150, bbox_inches="tight")
    print(f"  ✓ {path}")
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(12, 5))
    pure_algos = [a for a in algo_names if a != "Python sorted"]
    matrix = []
    for algo in pure_algos:
        row = []
        for d in dist_names:
            t_algo = results.get((algo, d, largest), 1)
            t_ref  = results.get(("Python sorted", d, largest), 1)
            row.append(t_algo / t_ref)   # ratio (>1 = slower than Timsort)
        matrix.append(row)

    matrix_np = np.array(matrix)
    im = ax.imshow(matrix_np, cmap="RdYlGn_r", aspect="auto")
    ax.set_xticks(range(len(dist_names)))
    ax.set_xticklabels([d.replace("_", " ").title() for d in dist_names])
    ax.set_yticks(range(len(pure_algos)))
    ax.set_yticklabels(pure_algos)
    for i in range(len(pure_algos)):
        for j in range(len(dist_names)):
            ax.text(j, i, f"{matrix_np[i, j]:.1f}×",
                    ha="center", va="center", fontsize=11, fontweight="bold")
    plt.colorbar(im, ax=ax, label="Slowdown vs Python sorted (Timsort)")
    ax.set_title(f"Slowdown Factor vs Built-in Timsort — n = {largest:,d}",
                 fontsize=13, fontweight="bold")
    fig.tight_layout()
    path = os.path.join(out_dir, "heatmap_slowdown.png")
    fig.savefig(path, dpi=150, bbox_inches="tight")
    print(f"  ✓ {path}")
    plt.close(fig)

if __name__ == "__main__":
    print("=" * 64)
    print("  Laboratory Nr 2 – Empirical Analysis of Sorting Algorithms")
    print("=" * 64)


    results = run_benchmarks()
    print_summary_table(results)

    print("\nGenerating plots …")
    plot_results(results)

