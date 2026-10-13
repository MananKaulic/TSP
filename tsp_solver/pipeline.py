import time
from .parser import parse_tsp
from .distance import euclidean_distance_matrix, tour_length
from .construction import nearest_neighbor, nearest_neighbor_best
from .two_opt import two_opt
from .or_opt import or_opt
from .three_opt import three_opt
from .lin_kernighan import lk_opt
from .simulated_annealing import simulated_annealing
from .iterated_ls import iterated_local_search

# TSPLIB known optimal values for the benchmark challenge instances
KNOWN_OPTIMALS = {
    'pr152': 73682,
    'd198': 15780,
    'ts225': 126643,
    'pr226': 80369,
    'a280': 2579,
    'lin318': 42029,
    'fl417': 11861,
    'pr439': 107217,
    'pcb442': 50778,
    'd493': 35002
}

DEFAULT_HEURISTICS = ['2-opt', 'or-opt', '3-opt', 'lk-opt', 'simulated_annealing', 'ils']

def solve(filepath: str, enabled_heuristics: list = None, callback=None,
          n_restarts: int = 10, stop_flag=None) -> dict:
    """
    Executes the comprehensive TSP optimization pipeline.
    """
    if enabled_heuristics is None:
        enabled_heuristics = DEFAULT_HEURISTICS

    start_time = time.time()
    data = parse_tsp(filepath)
    coords = data['coords']
    n = data['dimension']
    name = data['name'].lower()
    dist_matrix = euclidean_distance_matrix(coords)

    history = []

    def emit(stage, tour, dist):
        history.append({
            'stage': stage,
            'distance': int(dist),
            'time': round(time.time() - start_time, 2)
        })
        if callback:
            callback(stage, tour, int(dist))

    # Initial tour via Nearest Neighbor
    if n <= 300:
        tour = nearest_neighbor_best(dist_matrix, callback=emit, max_starts=10)
    else:
        tour = nearest_neighbor(dist_matrix, start=0, callback=emit)

    curr_dist = tour_length(tour, dist_matrix)
    emit('nn_complete', tour, curr_dist)

    if stop_flag and stop_flag.is_set():
        return format_result(data, coords, tour, curr_dist, history)

    # 1. 2-opt
    if '2-opt' in enabled_heuristics:
        tour = two_opt(tour, dist_matrix, callback=emit)
        curr_dist = tour_length(tour, dist_matrix)
        emit('2-opt_complete', tour, curr_dist)

    if stop_flag and stop_flag.is_set():
        return format_result(data, coords, tour, curr_dist, history)

    # 2. Or-opt
    if 'or-opt' in enabled_heuristics:
        tour = or_opt(tour, dist_matrix, callback=emit)
        curr_dist = tour_length(tour, dist_matrix)
        emit('or-opt_complete', tour, curr_dist)

    if stop_flag and stop_flag.is_set():
        return format_result(data, coords, tour, curr_dist, history)

    # 3. 3-opt
    if '3-opt' in enabled_heuristics:
        tour = three_opt(tour, dist_matrix, callback=emit)
        curr_dist = tour_length(tour, dist_matrix)
        emit('3-opt_complete', tour, curr_dist)

    if stop_flag and stop_flag.is_set():
        return format_result(data, coords, tour, curr_dist, history)

    # 4. Lin-Kernighan
    if 'lk-opt' in enabled_heuristics:
        tour = lk_opt(tour, dist_matrix, callback=emit)
        curr_dist = tour_length(tour, dist_matrix)
        emit('lk-opt_complete', tour, curr_dist)

    if stop_flag and stop_flag.is_set():
        return format_result(data, coords, tour, curr_dist, history)

    # 5. Simulated Annealing
    if 'simulated_annealing' in enabled_heuristics:
        tour = simulated_annealing(tour, dist_matrix, callback=emit)
        curr_dist = tour_length(tour, dist_matrix)
        emit('sa_complete', tour, curr_dist)

    if stop_flag and stop_flag.is_set():
        return format_result(data, coords, tour, curr_dist, history)

    # 6. Iterated Local Search
    if 'ils' in enabled_heuristics and n_restarts > 0:
        tour = iterated_local_search(tour, dist_matrix, callback=emit, n_restarts=n_restarts)
        curr_dist = tour_length(tour, dist_matrix)
        emit('ils_complete', tour, curr_dist)

    emit('complete', tour, curr_dist)
    return format_result(data, coords, tour, curr_dist, history)

def format_result(data, coords, tour, distance, history):
    name = data['name'].lower()
    optimal = KNOWN_OPTIMALS.get(name)
    gap = None
    if optimal is not None and optimal > 0:
        gap = round(((distance / optimal) - 1.0) * 100.0, 2)

    return {
        'instance_name': data['name'],
        'dimension': data['dimension'],
        'coords': coords.tolist(),
        'best_tour': tour,
        'best_distance': int(distance),
        'known_optimal': optimal,
        'gap_percent': gap,
        'history': history
    }

