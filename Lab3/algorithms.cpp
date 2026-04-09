#include <iostream>
#include <fstream>
#include <vector>
#include <queue>
#include <stack>
#include <chrono>
#include <random>
#include <algorithm>
#include <numeric>
#include <functional>
#include <iomanip>
#include <string>
#include <cmath>

using namespace std;
using namespace std::chrono;


struct Graph {
    int n, m;
    vector<vector<int>> adj;
    Graph(int n) : n(n), m(0), adj(n) {}
    void addEdge(int u, int v) {
        adj[u].push_back(v);
        adj[v].push_back(u);
        m++;
    }
};


struct Result {
    long long time_us;
    long long nodes_visited;
    long long edges_checked;
    long long peak_memory;
    int       components;
};


Result bfs(const Graph& g) {
    vector<bool> visited(g.n, false);
    long long edges_checked = 0, peak = 0;
    int components = 0;
    auto t0 = high_resolution_clock::now();

    for (int s = 0; s < g.n; s++) {
        if (visited[s]) continue;
        components++;
        visited[s] = true;
        queue<int> q;
        q.push(s);
        while (!q.empty()) {
            peak = max(peak, (long long)q.size());
            int u = q.front(); q.pop();
            for (int v : g.adj[u]) {
                edges_checked++;
                if (!visited[v]) { visited[v] = true; q.push(v); }
            }
        }
    }

    auto t1 = high_resolution_clock::now();
    return { duration_cast<microseconds>(t1-t0).count(), g.n, edges_checked, peak, components };
}

Result dfs(const Graph& g) {
    vector<bool> visited(g.n, false);
    long long edges_checked = 0, peak = 0;
    int components = 0;
    auto t0 = high_resolution_clock::now();

    for (int s = 0; s < g.n; s++) {
        if (visited[s]) continue;
        components++;
        stack<int> stk;
        stk.push(s);
        while (!stk.empty()) {
            peak = max(peak, (long long)stk.size());
            int u = stk.top(); stk.pop();
            if (visited[u]) continue;
            visited[u] = true;
            for (int v : g.adj[u]) {
                edges_checked++;
                if (!visited[v]) stk.push(v);
            }
        }
    }

    auto t1 = high_resolution_clock::now();
    return { duration_cast<microseconds>(t1-t0).count(), g.n, edges_checked, peak, components };
}

Result iddfs(const Graph& g) {
    vector<bool> discovered(g.n, false);
    long long edges_checked = 0, peak = 0;
    int components = 0, total_found = 0;
    auto t0 = high_resolution_clock::now();

    for (int s = 0; s < g.n; s++) {
        if (discovered[s]) continue;
        components++;
        int depth_limit = 0;

        while (true) {
            bool found_deeper = false;
            vector<bool> iter_vis(g.n, false);
            stack<pair<int,int>> stk;
            stk.push({s, 0});

            while (!stk.empty()) {
                peak = max(peak, (long long)stk.size());
                int u = stk.top().first;
                int d = stk.top().second;
                stk.pop();

                if (iter_vis[u]) continue;
                if (d > depth_limit) { found_deeper = true; continue; }

                iter_vis[u] = true;
                if (!discovered[u]) { discovered[u] = true; total_found++; }

                for (int v : g.adj[u]) {
                    edges_checked++;
                    if (!iter_vis[v]) stk.push({v, d+1});
                }
            }

            if (!found_deeper || total_found == g.n) break;
            depth_limit++;
        }
    }

    auto t1 = high_resolution_clock::now();
    return { duration_cast<microseconds>(t1-t0).count(), g.n, edges_checked, peak, components };
}

Result bfs_opt(const Graph& g) {
    vector<bool> visited(g.n, false);
    long long edges_checked = 0, peak = 0;
    int components = 0;
    auto t0 = high_resolution_clock::now();

    for (int s = 0; s < g.n; s++) {
        if (visited[s]) continue;
        components++;
        visited[s] = true;
        queue<int> q;
        q.push(s);
        while (!q.empty()) {
            peak = max(peak, (long long)q.size());
            int u = q.front(); q.pop();
            for (int v : g.adj[u]) {
                edges_checked++;
                if (!visited[v]) { visited[v] = true; q.push(v); }
            }
        }
    }

    auto t1 = high_resolution_clock::now();
    return { duration_cast<microseconds>(t1-t0).count(), g.n, edges_checked, peak, components };
}

namespace rec_state {
    long long edges = 0, peak_depth = 0;
    vector<bool>* vis = nullptr;
    const Graph*  g   = nullptr;
}

void dfs_rec_helper(int u, int depth) {
    (*rec_state::vis)[u] = true;
    rec_state::peak_depth = max(rec_state::peak_depth, (long long)depth);
    for (int v : rec_state::g->adj[u]) {
        rec_state::edges++;
        if (!(*rec_state::vis)[v])
            dfs_rec_helper(v, depth + 1);
    }
}

Result dfs_opt(const Graph& g) {
    vector<bool> visited(g.n, false);
    rec_state::vis        = &visited;
    rec_state::g          = &g;
    rec_state::edges      = 0;
    rec_state::peak_depth = 0;
    int components        = 0;
    auto t0 = high_resolution_clock::now();

    for (int s = 0; s < g.n; s++) {
        if (!visited[s]) { components++; dfs_rec_helper(s, 0); }
    }

    auto t1 = high_resolution_clock::now();
    return { duration_cast<microseconds>(t1-t0).count(),
             g.n, rec_state::edges, rec_state::peak_depth, components };
}

Graph genSparse(int n, unsigned seed = 42) {
    mt19937 rng(seed);
    Graph g(n);
    vector<int> perm(n); iota(perm.begin(), perm.end(), 0);
    shuffle(perm.begin(), perm.end(), rng);
    for (int i = 1; i < n; i++) {
        uniform_int_distribution<int> d(0, i-1);
        g.addEdge(perm[i], perm[d(rng)]);
    }
    uniform_int_distribution<int> rd(0, n-1);
    for (int i = 0; i < n/2; i++) {
        int u = rd(rng), v = rd(rng);
        if (u != v) g.addEdge(u, v);
    }
    return g;
}

Graph genDense(int n, unsigned seed = 42) {
    mt19937 rng(seed);
    Graph g(n);
    vector<int> perm(n); iota(perm.begin(), perm.end(), 0);
    shuffle(perm.begin(), perm.end(), rng);
    for (int i = 1; i < n; i++) {
        uniform_int_distribution<int> d(0, i-1);
        g.addEdge(perm[i], perm[d(rng)]);
    }
    uniform_int_distribution<int> rd(0, n-1);
    int extra = (int)(0.5 * n * log2(max(n, 2)));
    for (int i = 0; i < extra; i++) {
        int u = rd(rng), v = rd(rng);
        if (u != v) g.addEdge(u, v);
    }
    return g;
}

Graph genTree(int n, unsigned seed = 42) {
    mt19937 rng(seed);
    Graph g(n);
    for (int i = 1; i < n; i++) {
        uniform_int_distribution<int> d(0, i-1);
        g.addEdge(i, d(rng));
    }
    return g;
}

Graph genPath(int n) {
    Graph g(n);
    for (int i = 0; i < n-1; i++) g.addEdge(i, i+1);
    return g;
}

Graph genDisconnected(int n, unsigned seed = 42) {
    mt19937 rng(seed);
    Graph g(n);
    int num = max(2, (int)sqrt((double)n));
    vector<int> bounds;
    uniform_int_distribution<int> bd(1, n-1);
    while ((int)bounds.size() < num-1) {
        int b = bd(rng);
        if (find(bounds.begin(), bounds.end(), b) == bounds.end())
            bounds.push_back(b);
    }
    sort(bounds.begin(), bounds.end());
    bounds.push_back(n);
    int prev = 0;
    for (int end : bounds) {
        vector<int> comp;
        for (int i = prev; i < end; i++) comp.push_back(i);
        shuffle(comp.begin(), comp.end(), rng);
        for (int i = 1; i < (int)comp.size(); i++) {
            uniform_int_distribution<int> d(0, i-1);
            g.addEdge(comp[i], comp[d(rng)]);
        }
        prev = end;
    }
    return g;
}

const int REPEATS = 3;

template<typename Fn>
Result bestOf(Fn fn) {
    Result best = fn();
    for (int i = 1; i < REPEATS; i++) {
        Result r = fn();
        if (r.time_us < best.time_us) best = r;
    }
    return best;
}

void exportCSV(const vector<tuple<string,int,int,Result,Result,Result,Result,Result>>& rows,
               const string& path) {
    ofstream f(path);
    f << "dist,n,m,"
      << "bfs_us,bfs_nodes,bfs_edges,bfs_mem,"
      << "dfs_us,dfs_nodes,dfs_edges,dfs_mem,"
      << "iddfs_us,iddfs_nodes,iddfs_edges,iddfs_mem,"
      << "bfs_opt_us,bfs_opt_nodes,bfs_opt_edges,bfs_opt_mem,"
      << "dfs_opt_us,dfs_opt_nodes,dfs_opt_edges,dfs_opt_mem\n";

    auto wRes = [&](ofstream& ff, const Result& r) {
        ff << r.time_us << "," << r.nodes_visited << ","
           << r.edges_checked << "," << r.peak_memory << ",";
    };

    for (auto& [dist, n, m, rb, rd_, ri, rbo, rdo] : rows) {
        f << dist << "," << n << "," << m << ",";
        wRes(f, rb); wRes(f, rd_); wRes(f, ri); wRes(f, rbo); wRes(f, rdo);
        f << "\n";
    }
    cout << "\nCSV saved → " << path << "\n";
}

int main() {
    cout << "  Laboratory Nr. 3  C++ Benchmark: BFS / DFS / IDDFS\n";

    struct DistDef {
        string name;
        function<Graph(int)> gen;
        vector<int> sizes;
    };

    vector<DistDef> dists = {
        {"sparse",       [](int n){ return genSparse(n); },       {200,500,1000,2500,5000,10000}},
        {"dense",        [](int n){ return genDense(n); },        {200,500,1000,2500,5000,10000}},
        {"tree",         [](int n){ return genTree(n); },         {200,500,1000,2500,5000,10000}},
        {"path",         [](int n){ return genPath(n); },         {200,500,1000,2500,5000,10000}},
        {"disconnected", [](int n){ return genDisconnected(n); }, {200,500,1000,2500,5000,10000}},
    };

    int total = 0;
    for (auto& d : dists) total += (int)d.sizes.size();
    int done = 0;

    using RowTuple = tuple<string,int,int,Result,Result,Result,Result,Result>;
    vector<RowTuple> allRows;

    for (auto& dist : dists) {
        cout << "\n  Distribution: " << dist.name << "\n";
        for (int n : dist.sizes) {
            done++;
            double pct = 100.0 * done / total;
            Graph g = dist.gen(n);
            cout << "\n  n = " << setw(7) << n
                 << "   (" << fixed << setprecision(1) << pct << " % done)"
                 << "   [m=" << g.m << "]\n";

            Result rb  = bestOf([&]{ return bfs(g); });
            Result rd  = bestOf([&]{ return dfs(g); });
            Result ri  = bestOf([&]{ return iddfs(g); });
            Result rbo = bestOf([&]{ return bfs_opt(g); });
            Result rdo = bestOf([&]{ return dfs_opt(g); });

            cout << "    BFS        " << setw(8) << rb.time_us  << " us\n"
                 << "    DFS        " << setw(8) << rd.time_us  << " us\n"
                 << "    IDDFS      " << setw(8) << ri.time_us  << " us\n"
                 << "    BFS (opt)  " << setw(8) << rbo.time_us << " us\n"
                 << "    DFS (opt)  " << setw(8) << rdo.time_us << " us\n";

            allRows.emplace_back(dist.name, n, g.m, rb, rd, ri, rbo, rdo);
        }
    }

    // Summary
    int largestN = dists[0].sizes.back();
    cout << "\n\n  SUMMARY TABLEmn = " << largestN << "\n";
    cout << left  << setw(16) << "Distribution"
         << right << setw(10) << "BFS"
         << setw(10) << "DFS"
         << setw(10) << "IDDFS"
         << setw(10) << "BFS(opt)"
         << setw(10) << "DFS(opt)" << "\n";
    cout << string(66, '-') << "\n";

    for (auto& dist : dists) {
        for (auto it = allRows.rbegin(); it != allRows.rend(); ++it) {
            if (get<0>(*it) == dist.name) {
                cout << left << setw(16) << dist.name
                     << right
                     << setw(8) << get<3>(*it).time_us << "us"
                     << setw(8) << get<4>(*it).time_us << "us"
                     << setw(8) << get<5>(*it).time_us << "us"
                     << setw(8) << get<6>(*it).time_us << "us"
                     << setw(8) << get<7>(*it).time_us << "us"
                     << "\n";
                break;
            }
        }
    }

    exportCSV(allRows, "results.csv");
    cout << "All done.\n";
    return 0;
}
