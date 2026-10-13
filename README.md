# Traveling Salesman Problem (TSP) Solver & Visualizer

An advanced Operations Research application for solving and visualizing symmetric Traveling Salesman Problem (TSP) instances using custom heuristics and metaheuristics.

Inspired by [tspvis.com](https://tspvis.com), built with zero external optimization libraries (100% custom Python + NumPy algorithmic code).

---

## 🏆 Hall of Fame Benchmark Results

Evaluated on the 10 standard TSPLIB benchmark instances (`EUC_2D` integer rounding metric):

| Instance | Dimension ($N$) | Our Best Result (km/units) | TSPLIB Known Optimal | Optimality Gap (%) | Runtime (s) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **pr152** | 152 | **74,303** | 73,682 | **0.84%** | 1.10s |
| **d198** | 198 | **16,443** | 15,780 | **4.20%** | 0.33s |
| **ts225** | 225 | **133,639** | 126,643 | **5.52%** | 1.43s |
| **pr226** | 226 | **81,322** | 80,369 | **1.19%** | 0.66s |
| **a280** | 280 | **2,738** | 2,579 | **6.17%** | 2.18s |
| **lin318** | 318 | **44,303** | 42,029 | **5.41%** | 1.74s |
| **fl417** | 417 | **12,475** | 11,861 | **5.18%** | 2.24s |
| **pr439** | 439 | **112,883** | 107,217 | **5.28%** | 2.73s |
| **pcb442** | 442 | **54,018** | 50,778 | **6.38%** | 2.66s |
| **d493** | 493 | **37,131** | 35,002 | **6.08%** | 4.81s |

**Average Optimality Gap**: **4.62%** across all 10 instances.

---

## 🔬 Algorithmic Architecture

All algorithms are implemented from scratch in [`tsp_solver/`](tsp_solver/):

1. **Greedy Construction**:
   - `nearest_neighbor`: Greedy stepwise node selection with distance caching.
   - `nearest_neighbor_best`: Multi-start construction evaluating diverse pivot cities.
2. **Local Search Heuristics**:
   - **2-Opt**: $O(1)$ delta evaluation for reversing sub-segments.
   - **Or-Opt**: Evaluates 1, 2, and 3-node contiguous chain relocations and reversals.
   - **3-Opt**: Evaluates all 7 non-trivial 3-edge reconnection patterns.
   - **Lin-Kernighan**: Variable-depth search using nearest-neighbor candidate lists and positive gain criteria.
3. **Metaheuristics**:
   - **Simulated Annealing**: Metropolis acceptance criterion ($P = e^{-\Delta / T}$) with geometric cooling schedule to escape local traps.
   - **Iterated Local Search (ILS)**: Non-reversible 4-opt **Double-Bridge** perturbation kicks followed by local search polish over multiple restarts.

---

## 💻 Running Locally

### 1. Setup Virtual Environment
```bash
git clone https://github.com/MananKaulic/TSP.git
cd TSP
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Launch D3.js Animated Web App (Flask + WebSockets)
```bash
python app.py
```
Open [http://127.0.0.1:5001](http://127.0.0.1:5001) in your browser.

### 3. Launch Streamlit Web App
```bash
streamlit run streamlit_app.py
```
Open [http://localhost:8501](http://localhost:8501) in your browser.

### 4. Run Benchmark Suite
```bash
python benchmark.py
```

---

## 🚀 Cloud Deployment

### Streamlit Community Cloud (`share.streamlit.io`)
1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Connect your GitHub account and select repository `MananKaulic/TSP`
3. Set **Main file path** to `streamlit_app.py`
4. Click **Deploy!**

### Render
1. Go to [render.com](https://render.com) and create a new **Web Service**
2. Connect `MananKaulic/TSP`
3. Render automatically picks up `Procfile`:
   ```bash
   gunicorn --worker-class eventlet -w 1 --bind 0.0.0.0:$PORT app:app
   ```
4. Click **Create Web Service**.
