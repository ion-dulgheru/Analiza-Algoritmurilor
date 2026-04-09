from __future__ import annotations

from collections import deque
from typing import Dict, Generator, List, Optional, Set, Tuple

class Graph:

    def __init__(self, n: int) -> None:
        self.n: int = n
        self.adj: Dict[int, List[int]] = {i: [] for i in range(n)}
        self.m: int = 0

    def add_edge(self, u: int, v: int) -> None:
        self.adj[u].append(v)
        self.adj[v].append(u)
        self.m += 1

    def __repr__(self) -> str:
        return f"Graph(n={self.n}, m={self.m})"

class TraversalResult:
    def __init__(self, order, nodes_visited, edges_checked, peak_memory, components):
        self.order          = order
        self.nodes_visited  = nodes_visited
        self.edges_checked  = edges_checked
        self.peak_memory    = peak_memory
        self.components     = components

    def __repr__(self):
        return (f"TraversalResult(visited={self.nodes_visited}, "
                f"edges_checked={self.edges_checked}, "
                f"peak_mem={self.peak_memory}, components={self.components})")

def bfs(g: Graph, start: int = 0) -> TraversalResult:
    visited = [False] * g.n
    order   = []
    edges_checked = 0
    peak_memory   = 0
    components    = 0

    for s in range(g.n):
        if visited[s]:
            continue
        components += 1
        visited[s] = True
        queue: deque = deque([s])

        while queue:
            peak_memory = max(peak_memory, len(queue))
            u = queue.popleft()
            order.append(u)
            for v in g.adj[u]:
                edges_checked += 1
                if not visited[v]:
                    visited[v] = True
                    queue.append(v)

    return TraversalResult(order, len(order), edges_checked, peak_memory, components)

def dfs(g: Graph, start: int = 0) -> TraversalResult:
    visited = [False] * g.n
    order   = []
    edges_checked = 0
    peak_memory   = 0
    components    = 0

    for s in range(g.n):
        if visited[s]:
            continue
        components += 1
        stack = [s]

        while stack:
            peak_memory = max(peak_memory, len(stack))
            u = stack.pop()
            if visited[u]:
                continue
            visited[u] = True
            order.append(u)
            for v in g.adj[u]:
                edges_checked += 1
                if not visited[v]:
                    stack.append(v)

    return TraversalResult(order, len(order), edges_checked, peak_memory, components)

def iddfs(g: Graph, start: int = 0) -> TraversalResult:
    discovered = [False] * g.n   # globally found — for output dedup
    order      = []
    edges_checked = 0
    peak_memory   = 0
    components    = 0

    for s in range(g.n):
        if discovered[s]:
            continue
        components += 1
        depth_limit = 0

        while True:
            found_deeper  = False
            iter_visited  = [False] * g.n   # cycle guard within this pass
            stack: List[Tuple[int, int]] = [(s, 0)]

            while stack:
                peak_memory = max(peak_memory, len(stack))
                u, d = stack.pop()

                if iter_visited[u]:
                    continue
                if d > depth_limit:
                    found_deeper = True
                    continue

                iter_visited[u] = True
                if not discovered[u]:
                    discovered[u] = True
                    order.append(u)

                for v in g.adj[u]:
                    edges_checked += 1
                    if not iter_visited[v]:
                        stack.append((v, d + 1))

            if not found_deeper:
                break
            depth_limit += 1

    return TraversalResult(order, len(order), edges_checked, peak_memory, components)

def bfs_opt(g: Graph, start: int = 0) -> TraversalResult:
    visited = [False] * g.n
    order   = []
    edges_checked = 0
    peak_memory   = 0
    components    = 0

    for s in range(g.n):
        if visited[s]:
            continue
        components += 1
        visited[s] = True
        queue: deque = deque([s])

        while queue:
            peak_memory = max(peak_memory, len(queue))
            u = queue.popleft()
            order.append(u)
            for v in g.adj[u]:
                edges_checked += 1
                if not visited[v]:
                    visited[v] = True   # mark on enqueue — prevents duplicates
                    queue.append(v)

    return TraversalResult(order, len(order), edges_checked, peak_memory, components)


def dfs_opt(g: Graph, start: int = 0) -> TraversalResult:
    import sys
    sys.setrecursionlimit(200_000)

    visited = [False] * g.n
    order   = []
    ec      = [0]
    depth   = [0]
    components = 0

    def _dfs(u: int, d: int) -> None:
        visited[u] = True
        order.append(u)
        depth[0] = max(depth[0], d)
        for v in g.adj[u]:
            ec[0] += 1
            if not visited[v]:
                _dfs(v, d + 1)

    for s in range(g.n):
        if not visited[s]:
            components += 1
            _dfs(s, 0)

    return TraversalResult(order, len(order), ec[0], depth[0], components)


def iddfs_opt(g: Graph, start: int = 0) -> TraversalResult:
    discovered  = [False] * g.n
    order       = []
    edges_checked = 0
    peak_memory   = 0
    components    = 0
    total_found   = 0

    for s in range(g.n):
        if discovered[s]:
            continue
        components += 1
        depth_limit = 0

        while True:
            found_deeper = False
            iter_vis     = [False] * g.n
            stack: List[Tuple[int, int]] = [(s, 0)]

            while stack:
                peak_memory = max(peak_memory, len(stack))
                u, d = stack.pop()

                if iter_vis[u]:
                    continue
                if d > depth_limit:
                    found_deeper = True
                    continue

                iter_vis[u] = True
                if not discovered[u]:
                    discovered[u] = True
                    order.append(u)
                    total_found += 1

                for v in g.adj[u]:
                    edges_checked += 1
                    if not iter_vis[v]:
                        stack.append((v, d + 1))

            if not found_deeper or total_found == g.n:
                break
            depth_limit += 1

    return TraversalResult(order, len(order), edges_checked, peak_memory, components)
