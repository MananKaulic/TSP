import os
import time
from tsp_solver.pipeline import solve, KNOWN_OPTIMALS

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')

INSTANCES = [
    'pr152', 'd198', 'ts225', 'pr226', 'a280',
    'lin318', 'fl417', 'pr439', 'pcb442', 'd493'
]

def run_benchmarks():
    print("=" * 75)
    print("  TRAVELING SALESMAN PROBLEM - BENCHMARK HALL OF FAME EVALUATION")
    print("=" * 75)
    print(f"{'Instance':<10} | {'Cities':<8} | {'Best Distance':<15} | {'Known Optimal':<15} | {'Gap (%)':<8} | {'Time (s)':<8}")
    print("-" * 75)

    results = []

    for name in INSTANCES:
        path = os.path.join(DATA_DIR, f"{name}.tsp")
        if not os.path.exists(path):
            print(f"Skipping {name}: file not found.")
            continue

        t0 = time.time()
        res = solve(path, n_restarts=8)
        elapsed = time.time() - t0

        dist = res['best_distance']
        optimal = res['known_optimal']
        gap = res['gap_percent']
        dim = res['dimension']

        print(f"{name:<10} | {dim:<8} | {dist:<15,d} | {optimal:<15,d} | {gap:<7.2f}% | {elapsed:<8.2f}")
        results.append({
            'name': name,
            'dim': dim,
            'dist': dist,
            'optimal': optimal,
            'gap': gap,
            'time': elapsed
        })

    print("=" * 75)
    avg_gap = sum(r['gap'] for r in results if r['gap'] is not None) / len(results)
    print(f"Average Optimality Gap across all {len(results)} instances: {avg_gap:.2f}%")
    print("=" * 75)

    # Save summary report
    report_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'BENCHMARK_RESULTS.md')
    with open(report_file, 'w') as f:
        f.write("# TSP Challenge Benchmark - Hall of Fame Submission\n\n")
        f.write("| Instance | Dimension (Cities) | Our Result (Distance / km) | Known TSPLIB Optimal | Optimality Gap (%) | Computation Time |\n")
        f.write("| :--- | :--- | :--- | :--- | :--- | :--- |\n")
        for r in results:
            f.write(f"| **{r['name']}** | {r['dim']} | **{r['dist']:,}** | {r['optimal']:,} | **{r['gap']:.2f}%** | {r['time']:.2f}s |\n")
        f.write(f"\n**Average Gap:** {avg_gap:.2f}%\n")
    print(f"Report saved to {report_file}")

if __name__ == '__main__':
    run_benchmarks()

