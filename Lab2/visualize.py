
from __future__ import annotations

import argparse
import sys
from random import seed, shuffle
from typing import Generator, List, Tuple

import matplotlib
matplotlib.use("TkAgg")  # interactive backend
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.patches import FancyBboxPatch
import numpy as np

#  Colour palette 
CLR_DEFAULT  = "#3498db"   # blue  – normal bar
CLR_COMPARE  = "#e74c3c"   # red   – being compared
CLR_SWAP     = "#e67e22"   # orange – being swapped
CLR_SORTED   = "#2ecc71"   # green – in final position
CLR_PIVOT    = "#f1c40f"   # yellow – pivot element
CLR_MERGE    = "#9b59b6"   # purple – merge region
CLR_BG       = "#1e1e2e"   # dark background
CLR_TEXT     = "#cdd6f4"   # light text


#  GENERATOR-BASED SORTING ALGORITHMS
#  Each yields (array_snapshot, color_array, status_text) per step
Frame = Tuple[List[int], List[str], str]


#QUICK SORT 
def quick_sort_gen(a: List[int]) -> Generator[Frame, None, None]:
    n = len(a)
    colors = [CLR_DEFAULT] * n
    final = [False] * n

    def qs(lo: int, hi: int) -> Generator[Frame, None, None]:
        if lo >= hi:
            if 0 <= lo < n:
                final[lo] = True
                colors[lo] = CLR_SORTED
                yield a[:], colors[:], f"Element {lo} in final position"
            return

        # Lomuto partition with last element as pivot
        pivot = a[hi]
        colors[hi] = CLR_PIVOT
        yield a[:], colors[:], f"Pivot = {pivot} (index {hi})"

        i = lo
        for j in range(lo, hi):
            colors[j] = CLR_COMPARE
            yield a[:], colors[:], f"Compare a[{j}]={a[j]} with pivot={pivot}"

            if a[j] <= pivot:
                # swap
                colors[j] = CLR_SWAP
                colors[i] = CLR_SWAP
                yield a[:], colors[:], f"Swap a[{i}]={a[i]} ↔ a[{j}]={a[j]}"
                a[i], a[j] = a[j], a[i]
                yield a[:], colors[:], f"After swap"
                colors[i] = CLR_SORTED if final[i] else CLR_DEFAULT
                i += 1

            colors[j] = CLR_SORTED if final[j] else CLR_DEFAULT

        # place pivot
        colors[i] = CLR_SWAP
        colors[hi] = CLR_SWAP
        yield a[:], colors[:], f"Place pivot: swap a[{i}]={a[i]} ↔ a[{hi}]={a[hi]}"
        a[i], a[hi] = a[hi], a[i]
        final[i] = True
        colors[i] = CLR_SORTED
        colors[hi] = CLR_SORTED if final[hi] else CLR_DEFAULT
        yield a[:], colors[:], f"Pivot {pivot} placed at index {i}"

        yield from qs(lo, i - 1)
        yield from qs(i + 1, hi)

    yield from qs(0, n - 1)
    colors[:] = [CLR_SORTED] * n
    yield a[:], colors[:], "✓ Quick Sort complete!"


# MERGE SORT 
def merge_sort_gen(a: List[int]) -> Generator[Frame, None, None]:
    n = len(a)
    colors = [CLR_DEFAULT] * n

    def ms(lo: int, hi: int) -> Generator[Frame, None, None]:
        if lo >= hi:
            return
        mid = (lo + hi) // 2
        yield from ms(lo, mid)
        yield from ms(mid + 1, hi)

        # merge step
        merged: List[int] = []
        i, j = lo, mid + 1

        for k in range(lo, hi + 1):
            colors[k] = CLR_MERGE
        yield a[:], colors[:], f"Merging [{lo}..{mid}] and [{mid+1}..{hi}]"

        while i <= mid and j <= hi:
            colors[i] = CLR_COMPARE
            colors[j] = CLR_COMPARE
            yield a[:], colors[:], f"Compare a[{i}]={a[i]} vs a[{j}]={a[j]}"

            if a[i] <= a[j]:
                merged.append(a[i])
                colors[i] = CLR_MERGE
                i += 1
            else:
                merged.append(a[j])
                colors[j] = CLR_MERGE
                j += 1

        while i <= mid:
            merged.append(a[i]); i += 1
        while j <= hi:
            merged.append(a[j]); j += 1

        for k, val in enumerate(merged):
            a[lo + k] = val
            colors[lo + k] = CLR_SWAP
        yield a[:], colors[:], f"Merged result placed at [{lo}..{hi}]"

        for k in range(lo, hi + 1):
            colors[k] = CLR_DEFAULT
        yield a[:], colors[:], ""

    yield from ms(0, n - 1)
    colors[:] = [CLR_SORTED] * n
    yield a[:], colors[:], "✓ Merge Sort complete!"


# HEAP SORT 
def heap_sort_gen(a: List[int]) -> Generator[Frame, None, None]:
    n = len(a)
    colors = [CLR_DEFAULT] * n
    heap_end = n  # tracks the shrinking heap boundary

    def sift_down(start: int, end: int) -> Generator[Frame, None, None]:
        root = start
        while True:
            child = 2 * root + 1
            if child > end:
                break
            colors[root] = CLR_COMPARE
            colors[child] = CLR_COMPARE
            if child + 1 <= end:
                colors[child + 1] = CLR_COMPARE
            yield a[:], colors[:], f"Sift down: root={root}, children={child},{min(child+1,end)}"

            if child + 1 <= end and a[child] < a[child + 1]:
                child += 1

            if a[root] < a[child]:
                colors[root] = CLR_SWAP
                colors[child] = CLR_SWAP
                yield a[:], colors[:], f"Swap a[{root}]={a[root]} ↔ a[{child}]={a[child]}"
                a[root], a[child] = a[child], a[root]
                # reset colors
                colors[root] = CLR_DEFAULT
                if child + 1 <= end:
                    colors[child + 1] = CLR_DEFAULT
                root = child
            else:
                colors[root] = CLR_DEFAULT
                colors[child] = CLR_DEFAULT
                if child + 1 <= end:
                    colors[child + 1] = CLR_DEFAULT
                break
        # clean up
        for k in range(min(start, n), min(heap_end + 1, n)):
            if colors[k] != CLR_SORTED:
                colors[k] = CLR_DEFAULT

    # Build heap
    yield a[:], colors[:], "Building max-heap…"
    for start in range((n - 2) // 2, -1, -1):
        yield from sift_down(start, n - 1)
    yield a[:], colors[:], "Max-heap built!"

    # Extract
    for end in range(n - 1, 0, -1):
        heap_end = end
        colors[0] = CLR_SWAP
        colors[end] = CLR_SWAP
        yield a[:], colors[:], f"Extract max: swap a[0]={a[0]} ↔ a[{end}]={a[end]}"
        a[0], a[end] = a[end], a[0]
        colors[end] = CLR_SORTED
        colors[0] = CLR_DEFAULT
        yield a[:], colors[:], f"a[{end}] = {a[end]} sorted"
        yield from sift_down(0, end - 1)

    colors[0] = CLR_SORTED
    yield a[:], colors[:], "✓ Heap Sort complete!"


# PATIENCE SORT 
def patience_sort_gen(a: List[int]) -> Generator[Frame, None, None]:
    """
    Patience sort visualized: dealing phase shows which pile each
    element goes to, then merging phase lights up as merged.
    """
    from bisect import bisect_left
    from heapq import merge as hmerge

    n = len(a)
    colors = [CLR_DEFAULT] * n

    piles: List[List[int]] = []
    tops: List[int] = []
    pile_idx: List[int] = [0] * n        # which pile each original index went to

    # Dealing phase
    yield a[:], colors[:], "Patience Sort — Dealing elements onto piles…"

    for idx in range(n):
        x = a[idx]
        colors[idx] = CLR_COMPARE
        pos = bisect_left(tops, x)

        if pos == len(piles):
            piles.append([x])
            tops.append(x)
            pile_idx[idx] = pos
            yield a[:], colors[:], f"a[{idx}]={x} → new pile #{pos+1}  (total piles: {len(piles)})"
        else:
            piles[pos].append(x)
            tops[pos] = x
            pile_idx[idx] = pos
            yield a[:], colors[:], f"a[{idx}]={x} → pile #{pos+1}  (top was {tops[pos] if pos < len(tops) else '?'})"

        colors[idx] = CLR_PIVOT  # dealt

    yield a[:], colors[:], f"Dealing done — {len(piles)} piles (= LIS length!)"

    # Reverse each pile for ascending order
    for p in piles:
        p.reverse()

    # Merge phase – write back
    merged = list(hmerge(*piles))
    for idx in range(n):
        a[idx] = merged[idx]
        colors[idx] = CLR_SORTED
        if idx % max(1, n // 30) == 0 or idx == n - 1:
            yield a[:], colors[:], f"Merging piles… {idx+1}/{n}"

    yield a[:], colors[:], f"✓ Patience Sort complete!  ({len(piles)} piles = LIS length)"



#  ANIMATION ENGINE
ALGO_MAP = {
    "quick":     ("Quick Sort",     quick_sort_gen),
    "merge":     ("Merge Sort",     merge_sort_gen),
    "heap":      ("Heap Sort",      heap_sort_gen),
    "patience":  ("Patience Sort",  patience_sort_gen),
}


def animate_sort(name: str, generator_fn, arr: List[int],
                 interval: int = 50, save: bool = False) -> None:

    a = arr[:]
    gen = generator_fn(a)

    # Precompute all frames (so we know total count for progress bar)
    frames: List[Frame] = []
    for frame in gen:
        frames.append(frame)

    if not frames:
        return

    n = len(arr)
    x = np.arange(n)

    fig, ax = plt.subplots(figsize=(14, 6))
    fig.patch.set_facecolor(CLR_BG)
    ax.set_facecolor(CLR_BG)
    ax.tick_params(colors=CLR_TEXT)
    for spine in ax.spines.values():
        spine.set_color(CLR_TEXT)
        spine.set_linewidth(0.5)

    bar_container = ax.bar(x, frames[0][0], color=frames[0][1],
                           edgecolor="#00000030", linewidth=0.5,
                           width=0.6 if n <= 20 else 0.85)
    ax.set_xlim(-0.5, n - 0.5)
    ax.set_ylim(0, max(arr) * 1.18)

    # Value labels on top of bars (only for small arrays)
    value_texts = []
    if n <= 30:
        for i in range(n):
            t = ax.text(i, frames[0][0][i], str(frames[0][0][i]),
                        ha="center", va="bottom", fontsize=max(7, 14 - n // 4),
                        color=CLR_TEXT, fontweight="bold")
            value_texts.append(t)

    title = ax.set_title(name, fontsize=16, fontweight="bold",
                         color=CLR_TEXT, pad=12)
    status_text = ax.text(0.5, 1.02, "", transform=ax.transAxes,
                          ha="center", fontsize=10, color="#f5c211",
                          fontweight="bold")
    counter_text = ax.text(0.01, 0.96, "", transform=ax.transAxes,
                           ha="left", fontsize=9, color=CLR_TEXT, alpha=0.7)
    ax.set_xlabel("Index", color=CLR_TEXT, fontsize=10)
    ax.set_ylabel("Value", color=CLR_TEXT, fontsize=10)

    def update(frame_idx: int):
        vals, cols, msg = frames[frame_idx]
        for bar, val, col in zip(bar_container, vals, cols):
            bar.set_height(val)
            bar.set_color(col)
        for t, val in zip(value_texts, vals):
            t.set_position((t.get_position()[0], val))
            t.set_text(str(val))
        status_text.set_text(msg)
        counter_text.set_text(f"Step {frame_idx + 1} / {len(frames)}")
        return list(bar_container) + [status_text, counter_text] + value_texts

    anim = animation.FuncAnimation(
        fig, update,
        frames=len(frames),
        interval=interval,
        blit=False,
        repeat=False,
    )

    if save:
        out = f"plots/{name.lower().replace(' ', '_')}_animation.gif"
        import os; os.makedirs("plots", exist_ok=True)
        print(f"  Saving {out} ({len(frames)} frames) …", end=" ", flush=True)
        anim.save(out, writer="pillow", fps=max(1, 1000 // interval))
        print("done.")

    plt.tight_layout()
    plt.show()

#  CLI
def main() -> None:
    parser = argparse.ArgumentParser(
        description="Real-time sorting animation")
    parser.add_argument("--algo", nargs="*", default=list(ALGO_MAP.keys()),
                        choices=list(ALGO_MAP.keys()),
                        help="Which algorithms to animate")
    parser.add_argument("--n", type=int, default=50,
                        help="Number of elements (default 50)")
    parser.add_argument("--speed", type=int, default=50,
                        help="Frame interval in ms (lower = faster)")
    parser.add_argument("--save", action="store_true",
                        help="Save animations as .gif")
    parser.add_argument("--seed", type=int, default=42,
                        help="Random seed")
    parser.add_argument("--custom", type=str, default=None,
                        help="Custom comma-separated list of numbers, "
                             "e.g. --custom 5,3,8,1,4,9,2")
    args = parser.parse_args()

    if args.custom:
        arr = [int(x.strip()) for x in args.custom.split(",")]
    else:
        seed(args.seed)
        arr = list(range(1, args.n + 1))
        shuffle(arr)

    print("=" * 50)
    print("  Sorting Visualizer")
    if args.custom:
        print(f"  Custom list: {arr}")
    else:
        print(f"  Elements: {args.n}")
    print(f"  Speed: {args.speed}ms/frame")
    print("=" * 50)

    for key in args.algo:
        name, gen_fn = ALGO_MAP[key]
        print(f"\n▶ {name}")
        animate_sort(name, gen_fn, arr,
                     interval=args.speed, save=args.save)

    print("\nAll animations done.")


if __name__ == "__main__":
    main()
