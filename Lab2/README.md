# Laborator Nr. 2 — Analiza Empirică a Algoritmilor de Sortare

## Structura Fișierelor

| Fișier | Descriere |
|--------|-----------|
| `main.py` | Implementările celor 4 algoritmi de sortare |
| `bench.py` | Benchmark-uri + grafice + concluzii |
| `visualize.py` | Animație în timp real a sortării |

## Algoritmi Implementați

1. **Quick Sort** — pivot aleator, partiționare 3-way
2. **Merge Sort** — recursiv, top-down
3. **Heap Sort** — in-place, max-heap
4. **Patience Sort** — inspirat din jocul de cărți Solitaire (algoritmul „surpriză")

---

## Cerințe

- **Python 3.10+**
- Biblioteci necesare: `matplotlib`, `numpy`

### Instalare dependențe

```bash
pip install matplotlib numpy
```

---

## Cum se Rulează

### 1. Benchmark complet (grafice + tabel + concluzii)

```bash
cd Lab2
python bench.py
```

**Ce face:**
- Rulează toți 4 algoritmii pe 5 tipuri de date (random, sortat, inversat, aproape sortat, multe duplicate)
- Testează pe 6 dimensiuni: 500, 1000, 2500, 5000, 10000, 25000
- Afișează tabel cu proprietățile algoritmilor
- Afișează timpii de execuție pentru fiecare combinație
- Generează 4 grafice în folderul `plots/`
- Afișează concluziile finale

**Grafice generate (în `plots/`):**

| Fișier | Ce arată |
|--------|----------|
| `time_vs_size.png` | Timp vs dimensiune, câte un subplot per distribuție |
| `bar_comparison.png` | Bare grupate la cel mai mare n |
| `loglog_average.png` | Scala log-log cu linia de referință O(n log n) |
| `heatmap_slowdown.png` | Harta de căldură — încetinire față de Timsort |

---

### 2. Animație în timp real

```bash
cd Lab2
python visualize.py
```

Aceasta va deschide o fereastră cu o animație care arată cum fiecare algoritm sortează un array pas cu pas.

**Opțiuni:**

```bash
# Toate cele 4 algoritme, 50 elemente (implicit)
python visualize.py

# Doar un singur algoritm
python visualize.py --algo quick
python visualize.py --algo merge
python visualize.py --algo heap
python visualize.py --algo patience

# Mai multe elemente
python visualize.py --n 80

# Viteza animației (ms per cadru, mai mic = mai rapid)
python visualize.py --speed 10     # rapid
python visualize.py --speed 100    # lent

# Salvează animația ca GIF
python visualize.py --save

# Combini mai multe opțiuni
python visualize.py --algo quick merge --n 40 --speed 20
```

**Codurile de culoare în animație:**

| Culoare | Semnificație |
|---------|-------------|
| Albastru | Element normal |
| Roșu | Se compară |
| Portocaliu | Se face swap |
| Verde | Element în poziția finală |
| Galben | Pivot (Quick Sort) |
| Mov | Regiune de merge |

**Navigare:** Închide fereastra curentă → se deschide următorul algoritm.

---

## Exemplu de Utilizare Rapidă

```bash
# Pas 1: Instalează dependențele
pip install matplotlib numpy

# Pas 2: Intră în folder
cd Lab2

# Pas 3: Rulează benchmark-ul complet
python bench.py

# Pas 4: Vezi animația pentru Quick Sort
python visualize.py --algo quick --n 40 --speed 30
```

---

## Despre Patience Sort (algoritmul surpriză)

Patience Sort este un algoritm inspirat din jocul de cărți **Patience** (Solitaire):

1. **Distribuire:** Elementele se „distribuie" pe grămezi, ca niște cărți pe masă. Pentru fiecare element se caută (prin căutare binară) prima grămadă al cărei vârf este ≥ elementul curent.
2. **Interclasare:** Toate grămezile se interclasează cu un min-heap (k-way merge).

**Proprietate interesantă:** Numărul de grămezi = lungimea celui mai lung **subșir crescător** (LIS — Longest Increasing Subsequence), o consecință a **teoremei lui Dilworth** despre mulțimi parțial ordonate.

- Complexitate: **O(n log n)** garantat
- Spațiu: **O(n)**
- Stabil: **Da**
