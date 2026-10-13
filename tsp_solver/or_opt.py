import numpy as np
from .distance import tour_length

def or_opt(tour: list, dist_matrix: np.ndarray, callback=None, max_passes: int = 5) -> list:
    """
    Or-opt local search: relocates chains of length 3, 2, and 1 to better insertion points.
    """
    tour = list(tour)
    n = len(tour)
    improved = True
    passes = 0
    curr_distance = tour_length(tour, dist_matrix)
    emit_counter = 0

    while improved and passes < max_passes:
        improved = False
        passes += 1

        for seg_len in [3, 2, 1]:
            if n <= seg_len + 3:
                continue

            for i in range(n):
                # We extract segment of length seg_len starting at i
                # For simplicity, avoid wrap-around by circular rolling if needed
                if i + seg_len >= n:
                    continue  # skip edge cases for wrap-around

                c_prev = tour[i - 1]
                c_start = tour[i]
                c_end = tour[i + seg_len - 1]
                c_next = tour[(i + seg_len) % n]

                removal_delta = (dist_matrix[c_prev, c_next] -
                                 dist_matrix[c_prev, c_start] -
                                 dist_matrix[c_end, c_next])

                # Segment items
                seg = tour[i:i + seg_len]

                # Find candidate insertion points j (between tour[j] and tour[j+1])
                # j must not be inside or directly adjacent to the segment
                for j in range(n - 1):
                    if i - 1 <= j <= i + seg_len - 1:
                        continue

                    c_j = tour[j]
                    c_j1 = tour[j + 1]

                    # Standard insertion
                    insert_delta = (dist_matrix[c_j, c_start] +
                                    dist_matrix[c_end, c_j1] -
                                    dist_matrix[c_j, c_j1])

                    total_delta = removal_delta + insert_delta
                    if total_delta < 0:
                        # Perform relocation
                        rem = tour[:i] + tour[i + seg_len:]
                        # Find where c_j ended up in rem
                        j_new = rem.index(c_j)
                        tour = rem[:j_new + 1] + seg + rem[j_new + 1:]
                        curr_distance += int(total_delta)
                        improved = True
                        emit_counter += 1
                        if callback and (emit_counter % 5 == 0):
                            callback('or-opt', tour[:], curr_distance)
                        break

                    # Also test reversed segment insertion
                    if seg_len > 1:
                        insert_rev_delta = (dist_matrix[c_j, c_end] +
                                            dist_matrix[c_start, c_j1] -
                                            dist_matrix[c_j, c_j1])
                        total_rev_delta = removal_delta + insert_rev_delta
                        if total_rev_delta < 0:
                            rem = tour[:i] + tour[i + seg_len:]
                            j_new = rem.index(c_j)
                            tour = rem[:j_new + 1] + seg[::-1] + rem[j_new + 1:]
                            curr_distance += int(total_rev_delta)
                            improved = True
                            emit_counter += 1
                            if callback and (emit_counter % 5 == 0):
                                callback('or-opt', tour[:], curr_distance)
                            break
                if improved:
                    break
            if improved:
                break

    if callback:
        callback('or-opt', tour[:], curr_distance)

    return tour

