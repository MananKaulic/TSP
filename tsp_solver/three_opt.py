import numpy as np
from .distance import tour_length

def three_opt(tour: list, dist_matrix: np.ndarray, callback=None, max_iterations: int = 3, sample_step: int = 1) -> list:
    """
    3-opt heuristic evaluating 3-edge reconnection patterns.
    Uses bounded iterations and step sampling for fast execution on larger instances.
    """
    tour = list(tour)
    n = len(tour)
    if n < 6:
        return tour

    improved = True
    iteration = 0
    curr_distance = tour_length(tour, dist_matrix)
    emit_counter = 0

    # Adjust step size based on dimension for interactive responsiveness
    stride = max(1, n // 100) if n > 250 else 1

    while improved and iteration < max_iterations:
        improved = False
        iteration += 1

        for i in range(0, n - 4, stride):
            A, B = tour[i], tour[i + 1]

            for j in range(i + 2, n - 2, stride):
                C, D = tour[j], tour[j + 1]

                for k in range(j + 2, n, stride):
                    if i == 0 and k == n - 1:
                        continue

                    E, F = tour[k], tour[(k + 1) % n]

                    d0 = dist_matrix[A, B] + dist_matrix[C, D] + dist_matrix[E, F]

                    # 7 reconnection options
                    # Option 1 (2-opt on i, j): reverse seg1
                    d1 = dist_matrix[A, C] + dist_matrix[B, D] + dist_matrix[E, F]
                    # Option 2 (2-opt on j, k): reverse seg2
                    d2 = dist_matrix[A, B] + dist_matrix[C, E] + dist_matrix[D, F]
                    # Option 3 (2-opt on i, k): reverse both (seg1 + seg2)
                    d3 = dist_matrix[A, E] + dist_matrix[D, C] + dist_matrix[B, F]
                    # Option 4 (pure 3-opt): swap seg1 and seg2
                    d4 = dist_matrix[A, D] + dist_matrix[E, B] + dist_matrix[C, F]
                    # Option 5: swap and reverse seg1
                    d5 = dist_matrix[A, D] + dist_matrix[E, C] + dist_matrix[B, F]
                    # Option 6: swap and reverse seg2
                    d6 = dist_matrix[A, E] + dist_matrix[D, B] + dist_matrix[C, F]
                    # Option 7: reverse seg1, reverse seg2
                    d7 = dist_matrix[A, C] + dist_matrix[B, E] + dist_matrix[D, F]

                    deltas = [
                        (d1 - d0, 1),
                        (d2 - d0, 2),
                        (d3 - d0, 3),
                        (d4 - d0, 4),
                        (d5 - d0, 5),
                        (d6 - d0, 6),
                        (d7 - d0, 7)
                    ]

                    best_delta, best_move = min(deltas, key=lambda x: x[0])

                    if best_delta < 0:
                        seg1 = tour[i + 1:j + 1]
                        seg2 = tour[j + 1:k + 1]

                        if best_move == 1:
                            tour[i + 1:j + 1] = seg1[::-1]
                        elif best_move == 2:
                            tour[j + 1:k + 1] = seg2[::-1]
                        elif best_move == 3:
                            tour[i + 1:k + 1] = tour[i + 1:k + 1][::-1]
                        elif best_move == 4:
                            tour[i + 1:k + 1] = seg2 + seg1
                        elif best_move == 5:
                            tour[i + 1:k + 1] = seg2 + seg1[::-1]
                        elif best_move == 6:
                            tour[i + 1:k + 1] = seg2[::-1] + seg1
                        elif best_move == 7:
                            tour[i + 1:k + 1] = seg1[::-1] + seg2[::-1]

                        curr_distance += int(best_delta)
                        improved = True
                        emit_counter += 1
                        if callback and (emit_counter % 3 == 0):
                            callback('3-opt', tour[:], curr_distance)
                        break
                if improved:
                    break
            if improved:
                break

    if callback:
        callback('3-opt', tour[:], curr_distance)

    return tour

