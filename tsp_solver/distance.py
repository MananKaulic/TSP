import math
import numpy as np

def euc_2d_distance(c1, c2) -> int:
    """Standard TSPLIB EUC_2D distance rounded to nearest integer."""
    dx = c1[0] - c2[0]
    dy = c1[1] - c2[1]
    return int(round(math.sqrt(dx * dx + dy * dy)))

def euclidean_distance_matrix(coords: np.ndarray) -> np.ndarray:
    """Precompute full n x n integer distance matrix using vectorized numpy operations."""
    diff = coords[:, np.newaxis, :] - coords[np.newaxis, :, :]
    dist = np.sqrt(np.sum(diff ** 2, axis=2))
    # TSPLIB spec specifies round to nearest integer
    return np.rint(dist).astype(np.int64)

def tour_length(tour, dist_matrix: np.ndarray) -> int:
    """Compute total tour length for a closed cycle."""
    n = len(tour)
    if n < 2:
        return 0
    total = 0
    for i in range(n):
        total += dist_matrix[tour[i], tour[(i + 1) % n]]
    return int(total)

def tour_length_fast(tour_arr: np.ndarray, dist_matrix: np.ndarray) -> int:
    """Vectorized tour length."""
    return int(np.sum(dist_matrix[tour_arr, np.roll(tour_arr, -1)]))

