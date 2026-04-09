#include <iostream>
#include <vector>
#include <queue>
#include <chrono>
#include <random>
#include <fstream>
#include <iomanip>

using namespace std;
using namespace std::chrono;

const long long INF = 1e18; // O valoare suficient de mare pentru infinit

struct Edge {
    int to;
    long long weight;
};

struct Graph {
    int V;
    vector<vector<Edge>> adj;
    vector<vector<long long>> matrix; // Pentru Floyd-Warshall

    Graph(int V) : V(V), adj(V), matrix(V, vector<long long>(V, INF)) {
        for (int i = 0; i < V; i++) {
            matrix[i][i] = 0;
        }
    }

    void addEdge(int u, int v, long long w) {
        adj[u].push_back({v, w});
        matrix[u][v] = min(matrix[u][v], w); // Păstrăm muchia minimă
    }
};

// Generatoare de grafuri
Graph generateGraph(int V, double density, unsigned seed = 42) {
    mt19937 rng(seed);
    uniform_int_distribution<long long> weight_dist(1, 100); // Costuri pozitive 1-100
    uniform_real_distribution<double> prob_dist(0.0, 1.0);

    Graph g(V);
    for (int i = 0; i < V; i++) {
        for (int j = 0; j < V; j++) {
            if (i != j && prob_dist(rng) < density) {
                g.addEdge(i, j, weight_dist(rng));
            }
        }
    }
    return g;
}

// Algoritmul Dijkstra (Single Source)
long long runDijkstra(const Graph& g, int source) {
    auto start = high_resolution_clock::now();

    vector<long long> dist(g.V, INF);
    priority_queue<pair<long long, int>, vector<pair<long long, int>>, greater<pair<long long, int>>> pq;

    dist[source] = 0;
    pq.push({0, source});

    while (!pq.empty()) {
        auto [d, u] = pq.top();
        pq.pop();

        if (d > dist[u]) continue;

        for (const auto& edge : g.adj[u]) {
            if (dist[u] + edge.weight < dist[edge.to]) {
                dist[edge.to] = dist[u] + edge.weight;
                pq.push({dist[edge.to], edge.to});
            }
        }
    }

    auto end = high_resolution_clock::now();
    return duration_cast<microseconds>(end - start).count();
}

// Algoritmul Floyd-Warshall (All Pairs)
long long runFloydWarshall(const Graph& g) {
    auto start = high_resolution_clock::now();

    vector<vector<long long>> dist = g.matrix;

    for (int k = 0; k < g.V; k++) {
        for (int i = 0; i < g.V; i++) {
            for (int j = 0; j < g.V; j++) {
                if (dist[i][k] < INF && dist[k][j] < INF) {
                    dist[i][j] = min(dist[i][j], dist[i][k] + dist[k][j]);
                }
            }
        }
    }

    auto end = high_resolution_clock::now();
    return duration_cast<microseconds>(end - start).count();
}

int main() {
    vector<int> sizes = {50, 100, 150, 200, 300, 400}; // N creste treptat, O(V^3) e costisitor
    double sparse_density = 0.1;
    double dense_density = 0.8;

    ofstream csv("results_lab5.csv");
    csv << "Type,N,Dijkstra_us,FloydWarshall_us\n";

    cout << "Rulare Benchmark pentru Dijkstra si Floyd-Warshall...\n";

    for (int N : sizes) {
        cout << "Procesare N = " << N << "...\n";
        
        // --- SPARSE GRAPH ---
        Graph g_sparse = generateGraph(N, sparse_density);
        // Rulăm Dijkstra din toate nodurile pentru o comparatie cinstita cu All-Pairs FW
        long long d_time_sparse = 0;
        for(int i = 0; i < N; i++) {
            d_time_sparse += runDijkstra(g_sparse, i);
        }
        long long fw_time_sparse = runFloydWarshall(g_sparse);
        csv << "Sparse," << N << "," << d_time_sparse << "," << fw_time_sparse << "\n";

        // --- DENSE GRAPH ---
        Graph g_dense = generateGraph(N, dense_density);
        long long d_time_dense = 0;
        for(int i = 0; i < N; i++) {
            d_time_dense += runDijkstra(g_dense, i);
        }
        long long fw_time_dense = runFloydWarshall(g_dense);
        csv << "Dense," << N << "," << d_time_dense << "," << fw_time_dense << "\n";
    }

    csv.close();
    cout << "Date salvate in 'results_lab5.csv'.\n";
    return 0;
}