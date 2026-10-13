import random
import numpy as np
from .distance import tour_length
from .two_opt import two_opt
from .or_opt import or_opt

def double_bridge_perturbation(tour: list) -> list:
    """
    Standard double-bridge 4-opt move.
    Splits tour into 4 contiguous pieces A, B, C, D and reconnects as A - D - C - B.
    This kick cannot be reverted by a 2-opt move, making it the ideal TSP perturbation.
    """
    n = len(tour)
    if n < 8:
        # Small instance fallback: random shuffle of a chunk
        t = tour[:]
        random.shuffle(t)
        return t

    # Pick 4 cut positions
    pos = sorted(random.sample(range(1, n), 3))
    i, j, k = pos[0], pos[1], pos[2]

    A = tour[:i]
    B = tour[i:j]
    C = tour[j:k]
    D = tour[k:]

    return A + D + C + B

def iterated_local_search(tour: list, dist_matrix: np.ndarray, callback=None,
                          n_restarts: int = 10, max_no_improve: int = 15) -> list:
    """
    Iterated Local Search (ILS) metaheuristic.
    Applies double-bridge kicks followed by fast local search (2-opt & Or-opt).
    """
    best_tour = tour[:]
    best_dist = tour_length(best_tour, dist_matrix)
    current_tour = best_tour[:]
    current_dist = best_dist

    no_improve = 0

    for r in range(n_restarts):
        # Apply double-bridge kick
        perturbed = double_bridge_perturbation(current_tour)

        # Local search polish
        polished = two_opt(perturbed, dist_matrix, max_iterations=30)
        polished = or_opt(polished, dist_matrix, max_passes=2)
        pol_dist = tour_length(polished, dist_matrix)

        if pol_dist < current_dist:
            current_tour = polished
            current_dist = pol_dist

            if current_dist < best_dist:
                best_tour = current_tour[:]
                best_dist = current_dist
                no_improve = 0
                if callback:
                    callback('ils', best_tour[:], best_dist)
        else:
            no_improve += 1
            # 10% chance to accept slightly worse solution to escape basin
            if random.random() < 0.1:
                current_tour = polished
                current_dist = pol_dist

        if callback:
            callback('ils_progress', best_tour[:], best_dist)

        if no_improve >= max_no_improve:
            break

    if callback:
        callback('ils', best_tour[:], best_dist)

    return best_tour

