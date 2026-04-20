/*
 * Laboratory Work #7 - Greedy Algorithms
 * Subject: Prim's and Kruskal's Algorithms
 * Implementation in C++
 */

#include <iostream>
#include <vector>
#include <queue>
#include <algorithm>
#include <chrono>
#include <fstream>
#include <random>
#include <climits>
#include <iomanip>

using namespace std;
using namespace std::chrono;

// ─────────────────────────────────────────────
//  Data Structures
// ─────────────────────────────────────────────

struct Edge {
    int u, v, weight;
    bool operator<(const Edge& other) const {
        return weight < other.weight;
    }
};

// Union-Find (Disjoint Set Union) for Kruskal
struct DSU {
    vector<int> parent, rank_;

    DSU(int n) : parent(n), rank_(n, 0) {
        for (int i = 0; i < n; i++) parent[i] = i;
    }

    int find(int x) {
        if (parent[x] != x)
            parent[x] = find(parent[x]); // path compression
        return parent[x];
    }

    bool unite(int x, int y) {
        int px = find(x), py = find(y);
        if (px == py) return false;
        if (rank_[px] < rank_[py]) swap(px, py);
        parent[py] = px;
        if (rank_[px] == rank_[py]) rank_[px]++;
        return true;
    }
};

// ─────────────────────────────────────────────
//  Graph Generator (random connected graph)
// ─────────────────────────────────────────────

vector<Edge> generateGraph(int n, int maxWeight = 100) {
    mt19937 rng(42);
    uniform_int_distribution<int> weightDist(1, maxWeight);

    vector<Edge> edges;

    // Spanning tree to guarantee connectivity
    vector<int> nodes(n);
    iota(nodes.begin(), nodes.end(), 0);
    shuffle(nodes.begin(), nodes.end(), rng);

    for (int i = 1; i < n; i++) {
        int u = nodes[i - 1];
        int v = nodes[i];
        edges.push_back({u, v, weightDist(rng)});
    }

    // Add extra random edges (~1.5x nodes)
    int extra = n * 3 / 2;
    for (int i = 0; i < extra; i++) {
        int u = rng() % n;
        int v = rng() % n;
        if (u != v)
            edges.push_back({u, v, weightDist(rng)});
    }

    return edges;
}

// ─────────────────────────────────────────────
//  KRUSKAL'S ALGORITHM
// ─────────────────────────────────────────────

pair<vector<Edge>, long long> kruskal(int n, vector<Edge> edges) {
    auto start = high_resolution_clock::now();

    sort(edges.begin(), edges.end());

    DSU dsu(n);
    vector<Edge> mst;
    int totalWeight = 0;

    for (auto& e : edges) {
        if (dsu.unite(e.u, e.v)) {
            mst.push_back(e);
            totalWeight += e.weight;
            if ((int)mst.size() == n - 1) break;
        }
    }

    auto end = high_resolution_clock::now();
    long long duration = duration_cast<nanoseconds>(end - start).count();

    return {mst, duration};
}

// ─────────────────────────────────────────────
//  PRIM'S ALGORITHM
// ─────────────────────────────────────────────

pair<vector<Edge>, long long> prim(int n, const vector<Edge>& edges) {
    auto start = high_resolution_clock::now();

    // Build adjacency list
    vector<vector<pair<int,int>>> adj(n);
    for (auto& e : edges) {
        adj[e.u].push_back({e.v, e.weight});
        adj[e.v].push_back({e.u, e.weight});
    }

    // Min-heap: {weight, node, parent}
    priority_queue<tuple<int,int,int>,
                   vector<tuple<int,int,int>>,
                   greater<>> pq;

    vector<bool> inMST(n, false);
    vector<Edge> mst;

    pq.push({0, 0, -1});

    while (!pq.empty() && (int)mst.size() < n - 1) {
        auto [w, u, parent] = pq.top();
        pq.pop();

        if (inMST[u]) continue;
        inMST[u] = true;

        if (parent != -1)
            mst.push_back({parent, u, w});

        for (auto [v, weight] : adj[u]) {
            if (!inMST[v])
                pq.push({weight, v, u});
        }
    }

    auto end = high_resolution_clock::now();
    long long duration = duration_cast<nanoseconds>(end - start).count();

    return {mst, duration};
}

// ─────────────────────────────────────────────
//  PRINT MST
// ─────────────────────────────────────────────

void printMST(const string& name, const vector<Edge>& mst) {
    int total = 0;
    cout << "\n── " << name << " MST Edges ──\n";
    cout << left << setw(6) << "From"
         << setw(6) << "To"
         << setw(10) << "Weight" << "\n";
    cout << string(22, '-') << "\n";
    for (auto& e : mst) {
        cout << setw(6) << e.u
             << setw(6) << e.v
             << setw(10) << e.weight << "\n";
        total += e.weight;
    }
    cout << "Total MST Weight: " << total << "\n";
}

// ─────────────────────────────────────────────
//  EMPIRICAL ANALYSIS
// ─────────────────────────────────────────────

void empiricalAnalysis(const vector<int>& sizes, const string& csvFile) {
    ofstream csv(csvFile);
    csv << "nodes,kruskal_ns,prim_ns,kruskal_ms,prim_ms\n";

    cout << "\n╔══════════════════════════════════════════════════════╗\n";
    cout << "║           EMPIRICAL ANALYSIS RESULTS                ║\n";
    cout << "╠══════════════════════════════════════════════════════╣\n";
    cout << "║ " << left
         << setw(8)  << "Nodes"
         << setw(16) << "Kruskal (ms)"
         << setw(16) << "Prim (ms)"
         << setw(14) << "Faster"
         << " ║\n";
    cout << "╠══════════════════════════════════════════════════════╣\n";

    for (int n : sizes) {
        // Average over 3 runs
        long long kTotal = 0, pTotal = 0;
        int runs = 3;
        for (int r = 0; r < runs; r++) {
            auto edges = generateGraph(n);
            auto [kMST, kTime] = kruskal(n, edges);
            auto [pMST, pTime] = prim(n, edges);
            kTotal += kTime;
            pTotal += pTime;
        }
        long long kAvg = kTotal / runs;
        long long pAvg = pTotal / runs;

        double kMs = kAvg / 1e6;
        double pMs = pAvg / 1e6;
        string faster = (kAvg < pAvg) ? "Kruskal" : "Prim";

        csv << n << "," << kAvg << "," << pAvg << ","
            << fixed << setprecision(4) << kMs << ","
            << fixed << setprecision(4) << pMs << "\n";

        cout << "║ " << left
             << setw(8)  << n
             << setw(16) << fixed << setprecision(4) << kMs
             << setw(16) << fixed << setprecision(4) << pMs
             << setw(14) << faster
             << " ║\n";
    }

    cout << "╚══════════════════════════════════════════════════════╝\n";
    cout << "\nData saved to: " << csvFile << "\n";
    csv.close();
}

// ─────────────────────────────────────────────
//  MAIN
// ─────────────────────────────────────────────

int main() {
    cout << "==============================================\n";
    cout << "  Lab 7 – Greedy Algorithms: Prim & Kruskal  \n";
    cout << "==============================================\n";

    // ── Demo on small graph ──
    int demoN = 7;
    auto demoEdges = generateGraph(demoN);

    cout << "\n[ DEMO – Graph with " << demoN << " nodes ]\n";

    auto [kMST, kTime] = kruskal(demoN, demoEdges);
    auto [pMST, pTime] = prim(demoN, demoEdges);

    printMST("Kruskal", kMST);
    cout << "Time: " << kTime / 1000 << " µs\n";

    printMST("Prim", pMST);
    cout << "Time: " << pTime / 1000 << " µs\n";

    // ── Empirical analysis ──
    vector<int> sizes = {
        10, 50, 100, 250, 500,
        750, 1000, 1500, 2000, 3000,
        5000, 7500, 10000
    };

    empiricalAnalysis(sizes, "results.csv");

    cout << "\nRun visualize.py to generate plots.\n";
    return 0;
}
