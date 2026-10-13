import numpy as np
from .distance import tour_length

def two_opt(tour: list, dist_matrix: np.ndarray, callback=None, max_iterations: int = 150) -> list:
    """
    2-opt local search heuristic with delta evaluation.
    Reverses segment tour[i+1:j+1] when an improving edge swap is identified.
    """
    n = len(tour)
    tour = list(tour)
    improved = True
    iteration = 0
    curr_distance = tour_length(tour, dist_matrix)

    emit_interval = 2

    while improved and iteration < max_iterations:
        improved = False
        iteration += 1

        for i in range(n - 1):
            c_i = tour[i]
            c_i1 = tour[i + 1]
            dist_i_i1 = dist_matrix[c_i, c_i1]

            for j in range(i + 2, n):
                if i == 0 and j == n - 1:
                    continue  # adjacent wrap-around edge

                c_j = tour[j]
                c_j1 = tour[(j + 1) % n]

                delta = (dist_matrix[c_i, c_j] + dist_matrix[c_i1, c_j1]) - (dist_i_i1 + dist_matrix[c_j, c_j1])
                if delta < 0:
                    tour[i + 1:j + 1] = reversed(tour[i + 1:j + 1])
                    curr_distance += int(delta)
                    improved = True

                    if callback and (iteration % emit_interval == 0):
                        callback('2-opt', tour[:], curr_distance)
                    break
            if improved:
                break

    if callback:
        callback('2-opt', tour[:], curr_distance)

    return tour

