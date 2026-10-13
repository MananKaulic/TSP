import os
import time
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
from tsp_solver.parser import parse_tsp
from tsp_solver.distance import euclidean_distance_matrix, tour_length
from tsp_solver.pipeline import solve, KNOWN_OPTIMALS, DEFAULT_HEURISTICS

st.set_page_config(
    page_title="TSP Solver & Visualizer",
    page_icon="🗺️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Dark theme styling for Streamlit
st.markdown("""
<style>
    .reportview-container, .main {
        background-color: #0b0c10;
        color: #f0f2f8;
    }
    .stMetric {
        background-color: #14161f;
        padding: 12px;
        border-radius: 8px;
        border: 1px solid #232738;
    }
    .metric-value {
        font-family: 'Courier New', monospace;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

st.title("🗺️ Traveling Salesman Problem Solver")
st.caption("Nearest Neighbor Construction & Metaheuristic Improvements (2-Opt, Or-Opt, 3-Opt, LK, SA, ILS)")

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
INSTANCES = ['pr152', 'd198', 'ts225', 'pr226', 'a280', 'lin318', 'fl417', 'pr439', 'pcb442', 'd493']

# Sidebar Controls
st.sidebar.header("Instance Configuration")
selected_instance = st.sidebar.selectbox("Choose Benchmark Instance", INSTANCES, index=0)

st.sidebar.subheader("Optimization Pipeline")
enable_2opt = st.sidebar.checkbox("2-Opt Local Search", value=True)
enable_oropt = st.sidebar.checkbox("Or-Opt Chain Relocation", value=True)
enable_3opt = st.sidebar.checkbox("3-Opt Edge Reconnection", value=True)
enable_lk = st.sidebar.checkbox("Lin-Kernighan Variable-Depth", value=True)
enable_sa = st.sidebar.checkbox("Simulated Annealing", value=True)
enable_ils = st.sidebar.checkbox("Iterated Local Search (Double Bridge)", value=True)

restarts = st.sidebar.slider("ILS Restarts / Kicks", min_value=1, max_value=20, value=8)

heuristics = []
if enable_2opt: heuristics.append('2-opt')
if enable_oropt: heuristics.append('or-opt')
if enable_3opt: heuristics.append('3-opt')
if enable_lk: heuristics.append('lk-opt')
if enable_sa: heuristics.append('simulated_annealing')
if enable_ils: heuristics.append('ils')

file_path = os.path.join(DATA_DIR, f"{selected_instance}.tsp")
data = parse_tsp(file_path)
coords = data['coords']
n = data['dimension']
known_opt = KNOWN_OPTIMALS.get(selected_instance, None)

# Metric layout
col1, col2, col3, col4 = st.columns(4)
col1.metric("Instance Dimension", f"{n} Cities")
col2.metric("Known Optimal", f"{known_opt:,}" if known_opt else "N/A")
metric_curr = col3.empty()
metric_gap = col4.empty()

metric_curr.metric("Current Tour Length", "—")
metric_gap.metric("Optimality Gap", "—")

plot_placeholder = st.empty()
progress_bar = st.progress(0.0)
status_text = st.empty()

def render_plot(tour, stage_name, dist):
    fig, ax = plt.subplots(figsize=(10, 6), facecolor='#0b0c10')
    ax.set_facecolor('#14161f')

    # Draw cities
    ax.scatter(coords[:, 0], coords[:, 1], c='#00d2ff', s=16, zorder=3, edgecolors='white', linewidths=0.5)

    # Draw tour edges
    if tour and len(tour) > 1:
        closed_tour = tour + [tour[0]]
        tour_coords = coords[closed_tour]
        ax.plot(tour_coords[:, 0], tour_coords[:, 1], c='#00f0a8', linewidth=1.5, alpha=0.9, zorder=2)

    ax.set_title(f"Instance: {selected_instance} | Stage: {stage_name} | Distance: {dist:,}", color='#f0f2f8', fontsize=12)
    ax.tick_params(colors='#606782')
    for spine in ax.spines.values():
        spine.set_color('#232738')

    plot_placeholder.pyplot(fig)
    plt.close(fig)

# Initial render of points
render_plot([], "Ready", 0)

if st.sidebar.button("🚀 Run Solver & Visualizer", type="primary"):
    status_text.info("Solving... Running heuristics pipeline step by step.")

    start_t = time.time()
    last_update = [0.0]

    def streamlit_callback(stage, current_tour, distance):
        now = time.time()
        if (now - last_update[0] > 0.15) or stage in ('complete', 'nn_complete', '2-opt_complete', 'ils_complete'):
            last_update[0] = now
            render_plot(current_tour, stage, distance)
            metric_curr.metric("Current Tour Length", f"{distance:,}")
            if known_opt:
                gap = ((distance / known_opt) - 1.0) * 100
                metric_gap.metric("Optimality Gap", f"{gap:.2f}%")

    result = solve(file_path, enabled_heuristics=heuristics, callback=streamlit_callback, n_restarts=restarts)

    render_plot(result['best_tour'], "Complete", result['best_distance'])
    metric_curr.metric("Best Tour Length", f"{result['best_distance']:,}")
    if result['gap_percent'] is not None:
        metric_gap.metric("Optimality Gap", f"{result['gap_percent']:.2f}%")

    elapsed = time.time() - start_t
    status_text.success(f"✓ Solved {selected_instance} in {elapsed:.2f}s! Distance: {result['best_distance']:,} (Gap: {result['gap_percent']}%)")

