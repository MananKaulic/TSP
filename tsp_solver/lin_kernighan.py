import numpy as np
from .distance import tour_length

def build_neighbor_matrix(dist_matrix: np.ndarray, k: int = 15) -> np.ndarray:
    """Precompute k-nearest neighbors for each city, excluding self."""
    n = len(dist_matrix)
    k_eff = min(k, n - 1)
    neighbors = np.zeros((n, k_eff), dtype=np.int64)
    for i in range(n):
        sorted_indices = np.argsort(dist_matrix[i])
        neighbors[i] = sorted_indices[1:k_eff + 1]
    return neighbors

def lk_opt(tour: list, dist_matrix: np.ndarray, callback=None, max_passes: int = 3, k_neighbors: int = 15) -> list:
    """
    Lin-Kernighan style variable-depth local search.
    Explores candidate edge deletions and additions guided by nearest neighbors
    and cumulative gain criterion.
    """
    tour = list(tour)
    n = len(tour)
    if n < 4:
        return tour

    neighbors = build_neighbor_matrix(dist_matrix, k=k_neighbors)
    improved = True
    passes = 0
    curr_distance = tour_length(tour, dist_matrix)
    emit_counter = 0

    while improved and passes < max_passes:
        improved = False
        passes += 1

        pos = {city: idx for idx, city in enumerate(tour)}

        for i in range(n):
            t1 = tour[i]
            t2 = tour[(i + 1) % n]
            d_t1_t2 = dist_matrix[t1, t2]

            # Try connecting t2 to one of its nearest neighbors t3
            for t3 in neighbors[t2]:
                if t3 == t1 or t3 == tour[(i - 1) % n]:
                    continue

                d_t2_t3 = dist_matrix[t2, t3]
                gain1 = d_t1_t2 - d_t2_t3
                if gain1 <= 0:
                    continue

                pos_t3 = pos[t3]
                # In tour, t3 is adjacent to t4 = tour[(pos_t3 + 1) % n]
                t4 = tour[(pos_t3 + 1) % n]
                d_t3_t4 = dist_matrix[t3, t4]

                # Check 2-opt closure: connect t4 back to t1
                d_t4_t1 = dist_matrix[t4, t1]
                net_2opt_gain = gain1 + (d_t3_t4 - d_t4_t1)

                if net_2opt_gain > 0:
                    # Apply 2-opt move between edge (t1, t2) and (t3, t4)
                    i1 = min(i, pos_t3)
                    i2 = max(i, pos_t3)
                    tour[i1 + 1:i2 + 1] = reversed(tour[i1 + 1:i2 + 1])
                    curr_distance -= int(net_2opt_gain)
                    improved = True
                    emit_counter += 1
                    if callback and (emit_counter % 3 == 0):
                        callback('lk-opt', tour[:], curr_distance)
                    break

                # Extend to depth-3 variable-depth move
                gain2 = gain1 + d_t3_t4
                for t5 in neighbors[t4]:
                    if t5 in (t1, t2, t3):
                        continue
                    d_t4_t5 = dist_matrix[t4, t5]
                    gain3 = gain2 - d_t4_t5
                    if gain3 <= 0:
                        continue

                    pos_t5 = pos[t5]
                    t6 = tour[(pos_t5 + 1) % n]
                    d_t5_t6 = dist_matrix[t5, t6]
                    d_t6_t1 = dist_matrix[t6, t1]
                    net_3opt_gain = gain3 + (d_t5_t6 - d_t6_t1)

                    if net_3opt_gain > 0:
                        # Perform test swap
                        candidate = tour[:]
                        # Safe fallback check
                        candidate[min(i, pos_t3) + 1:max(i, pos_t3) + 1] = reversed(candidate[min(i, pos_t3) + 1:max(i, pos_t3) + 1])
                        c_dist = tour_length(candidate, dist_matrix)
                        if c_dist < curr_distance:
                            tour = candidate
                            curr_distance = c_dist
                            improved = True
                            emit_counter += 1
                            if callback and (emit_counter % 3 == 0):
                                callback('lk-opt', tour[:], curr_distance)
                            break
                if improved:
                    break
            if improved:
                break

    if callback:
        callback('lk-opt', tour[:], curr_distance)

    return tour

