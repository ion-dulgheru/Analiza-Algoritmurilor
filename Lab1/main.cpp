#include <iostream>
#include <chrono>
#include <iomanip>
#include <cmath>
#include <utility>
using namespace std;

const long long MOD = 1000000007;

long long fib_recursive(int n) {
    if (n <= 1) {
        return n;
    }
    return fib_recursive(n - 1) + fib_recursive(n - 2);
}

long long fib_iterative(int n) {
    if (n <= 1) return n;
    long long a = 0, b = 1, c;
    
    for (int i = 2; i <= n; i++) {
        c = (a + b) % MOD;
        a = b;
        b = c;
    }
    return b;
}

void multiply(long long F[2][2], long long M[2][2]) {
    long long x = (F[0][0] * M[0][0] + F[0][1] * M[1][0]) % MOD;
    long long y = (F[0][0] * M[0][1] + F[0][1] * M[1][1]) % MOD;
    long long z = (F[1][0] * M[0][0] + F[1][1] * M[1][0]) % MOD;
    long long w = (F[1][0] * M[0][1] + F[1][1] * M[1][1]) % MOD;

    F[0][0] = x; F[0][1] = y;
    F[1][0] = z; F[1][1] = w;
}

void power(long long F[2][2], int n) {
    if (n == 0 || n == 1) return;
    long long M[2][2] = {{1, 1}, {1, 0}};

    power(F, n / 2);
    multiply(F, F);

    if (n % 2 != 0) multiply(F, M);
}

long long fib_matrix(int n) {
    if (n <= 1) return n;
    long long F[2][2] = {{1, 1}, {1, 0}};
    power(F, n - 1);
    return F[0][0];
}

long long fib_binet(int n) {
    double phi = (1 + sqrt(5)) / 2;
    return round((pow(phi, n) - pow(1 - phi, n)) / sqrt(5));
}

pair<long long, long long> fib_fast_doubling_helper(int n) {
    if (n == 0) return {0, 1};

    auto p = fib_fast_doubling_helper(n / 2);
    long long c = p.first;  
    long long d = p.second; 
    
    long long next_c = (c * ((2 * d % MOD - c + MOD) % MOD)) % MOD;
    long long next_d = ((c * c) % MOD + (d * d) % MOD) % MOD;

    if (n % 2 == 0) {
        return {next_c, next_d};
    } else {
        return {next_d, (next_c + next_d) % MOD};
    }
}

long long fib_fast_doubling(int n) {
    return fib_fast_doubling_helper(n).first;
}

int main()
{


    
    int series1[] = {5, 7, 10, 12, 15, 17, 20, 22, 25, 27, 30, 32, 35, 37, 40, 42, 45};
    int size1 = 17;
    
    double t1_recursive[17], t1_iterative[17], t1_matrix[17], t1_binet[17], t1_fast[17];
    
    cout << "========== SERIA 1: Teste cu toate metodele ==========\n\n";
    cout << fixed << setprecision(8);

    
    for(int i = 0; i < size1; i++) {
        int n = series1[i];
        
        auto start = chrono::high_resolution_clock::now();
        long long result1 = fib_recursive(n);
        auto end = chrono::high_resolution_clock::now();
        t1_recursive[i] = chrono::duration<double>(end - start).count();
        
        start = chrono::high_resolution_clock::now();
        long long result2 = fib_iterative(n);
        end = chrono::high_resolution_clock::now();
        t1_iterative[i] = chrono::duration<double>(end - start).count();
        
        start = chrono::high_resolution_clock::now();
        long long result3 = fib_matrix(n);
        end = chrono::high_resolution_clock::now();
        t1_matrix[i] = chrono::duration<double>(end - start).count();
        
        start = chrono::high_resolution_clock::now();
        long long result4 = fib_binet(n);
        end = chrono::high_resolution_clock::now();
        t1_binet[i] = chrono::duration<double>(end - start).count();

        start = chrono::high_resolution_clock::now();
        long long result5 = fib_fast_doubling(n);
        end = chrono::high_resolution_clock::now();
        t1_fast[i] = chrono::duration<double>(end - start).count();
    }
    
    cout << "n:          ";
    for(int i = 0; i < size1; i++) {
        cout << setw(12) << series1[i];
    }
    cout << "\n\n";
    
    cout << "Recursive:  ";
    for(int i = 0; i < size1; i++) {
        cout << setw(12) << t1_recursive[i];
    }
    cout << "\n";
    
    cout << "Iterative:  ";
    for(int i = 0; i < size1; i++) {
        cout << setw(12) << t1_iterative[i];
    }
    cout << "\n";
    
    cout << "Matrix:     ";
    for(int i = 0; i < size1; i++) {
        cout << setw(12) << t1_matrix[i];
    }
    cout << "\n";
    
    cout << "Binet:      ";
    for(int i = 0; i < size1; i++) {
        cout << setw(12) << t1_binet[i];
    }
    cout << "\n";

    cout << "Fast Dbl:   ";
    for(int i = 0; i < size1; i++) {
        cout << setw(12) << t1_fast[i];
    }
    cout << "\n\n";
    
    
    int series2[] = {501, 631, 794, 1000, 1259, 1585, 1995, 2512, 3162, 3981, 5012, 6310, 7943, 10000, 12589, 15849};
    int size2 = 16;
    
    double t2_iterative[16], t2_matrix[16], t2_binet[16], t2_fast[16];
    
    cout << "\n========== SERIA 2: Teste cu metode rapide ==========\n\n";
    
    for(int i = 0; i < size2; i++) {
        int n = series2[i];
        
        auto start = chrono::high_resolution_clock::now();
        long long result2 = fib_iterative(n);
        auto end = chrono::high_resolution_clock::now();
        t2_iterative[i] = chrono::duration<double>(end - start).count();
        
        start = chrono::high_resolution_clock::now();
        long long result3 = fib_matrix(n);
        end = chrono::high_resolution_clock::now();
        t2_matrix[i] = chrono::duration<double>(end - start).count();
        
        start = chrono::high_resolution_clock::now();
        long long result4 = fib_binet(n);
        end = chrono::high_resolution_clock::now();
        t2_binet[i] = chrono::duration<double>(end - start).count();

        start = chrono::high_resolution_clock::now();
        long long result5 = fib_fast_doubling(n);
        end = chrono::high_resolution_clock::now();
        t2_fast[i] = chrono::duration<double>(end - start).count();
    }
    
    cout << "n:          ";
    for(int i = 0; i < size2; i++) {
        cout << setw(12) << series2[i];
    }
    cout << "\n\n";
    
    cout << "Iterative:  ";
    for(int i = 0; i < size2; i++) {
        cout << setw(12) << t2_iterative[i];
    }
    cout << "\n";
    
    cout << "Matrix:     ";
    for(int i = 0; i < size2; i++) {
        cout << setw(12) << t2_matrix[i];
    }
    cout << "\n";
    
    cout << "Binet:      ";
    for(int i = 0; i < size2; i++) {
        cout << setw(12) << t2_binet[i];
    }
    cout << "\n";

    cout << "Fast Dbl:   ";
    for(int i = 0; i < size2; i++) {
        cout << setw(12) << t2_fast[i];
    }
    cout << "\n\n";
    
    return 0;
}