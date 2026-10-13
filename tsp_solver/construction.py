import numpy as np
from .distance import tour_length

def nearest_neighbor(dist_matrix: np.ndarray, start: int = 0, callback=None) -> list:
    """
    Greedy nearest neighbor construction from a given start city.
    Invokes callback(stage, tour, distance) periodically during construction.
    """
    n = len(dist_matrix)
    visited = np.zeros(n, dtype=bool)
    tour = [start]
    visited[start] = True
    current_length = 0

    emit_interval = max(1, n // 30)

    for step in range(n - 1):
        last = tour[-1]
        distances = dist_matrix[last].copy()
        distances[visited] = 9223372036854775807  # infinity for int64
        nearest = int(np.argmin(distances))
        current_length += int(dist_matrix[last, nearest])
        tour.append(nearest)
        visited[nearest] = True

        if callback and (step % emit_interval == 0):
            callback('nearest_neighbor', tour[:], current_length)

    # Return edge to start
    current_length += int(dist_matrix[tour[-1], tour[0]])
    if callback:
        callback('nearest_neighbor', tour[:], current_length)

    return tour

def nearest_neighbor_best(dist_matrix: np.ndarray, callback=None, max_starts=None) -> list:
    """
    Evaluates multiple start cities for nearest neighbor and selects the best one.
    """
    n = len(dist_matrix)
    num_starts = min(max_starts or n, n)
    step_stride = max(1, n // num_starts)
    starts = [i * step_stride for i in range(num_starts)]

    best_tour = None
    best_length = float('inf')

    for s in starts:
        tour = nearest_neighbor(dist_matrix, start=s)
        length = tour_length(tour, dist_matrix)
        if length < best_length:
            best_length = length
            best_tour = tour[:]

    if callback and best_tour is not None:
        callback('nearest_neighbor_best', best_tour[:], best_length)

    return best_tour

