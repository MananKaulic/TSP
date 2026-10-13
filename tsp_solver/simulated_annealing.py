import math
import random
import numpy as np
from .distance import tour_length

def simulated_annealing(tour: list, dist_matrix: np.ndarray, callback=None,
                        T_start: float = None, T_end: float = 0.5, cooling_rate: float = 0.9995,
                        max_iterations: int = None) -> list:
    """
    Simulated Annealing metaheuristic for escaping local optima.
    Utilizes 2-opt transitions with Metropolis acceptance probability exp(-delta / T).
    """
    tour = list(tour)
    n = len(tour)
    if n < 4:
        return tour

    curr_dist = tour_length(tour, dist_matrix)
    best_tour = tour[:]
    best_dist = curr_dist

    # Auto-calibrate initial temperature based on average edge cost
    if T_start is None:
        sample_indices = np.random.choice(n, size=min(n, 50), replace=False)
        sample_dists = dist_matrix[sample_indices, (sample_indices + 1) % n]
        avg_edge = float(np.mean(sample_dists)) if len(sample_dists) > 0 else 100.0
        T_start = max(10.0, avg_edge * 0.3)

    if max_iterations is None:
        max_iterations = min(30000, n * 80)

    T = T_start
    emit_interval = max(1, max_iterations // 50)

    for step in range(max_iterations):
        # Sample random pair for 2-opt move
        i = random.randint(0, n - 3)
        j = random.randint(i + 2, n - 1)
        if i == 0 and j == n - 1:
            continue

        c_i = tour[i]
        c_i1 = tour[i + 1]
        c_j = tour[j]
        c_j1 = tour[(j + 1) % n]

        delta = (dist_matrix[c_i, c_j] + dist_matrix[c_i1, c_j1]) - (dist_matrix[c_i, c_i1] + dist_matrix[c_j, c_j1])

        # Metropolis acceptance criterion
        if delta < 0 or (T > 1e-6 and random.random() < math.exp(-delta / T)):
            tour[i + 1:j + 1] = reversed(tour[i + 1:j + 1])
            curr_dist += int(delta)

            if curr_dist < best_dist:
                best_dist = curr_dist
                best_tour = tour[:]

        T *= cooling_rate
        if T < T_end:
            break

        if callback and (step % emit_interval == 0):
            callback('simulated_annealing', best_tour[:], best_dist)

    if callback:
        callback('simulated_annealing', best_tour[:], best_dist)

    return best_tour

