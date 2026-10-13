import os
import threading
import time
from flask import Flask, render_template, jsonify
from flask_socketio import SocketIO, emit
from tsp_solver.parser import parse_tsp
from tsp_solver.pipeline import solve, KNOWN_OPTIMALS

app = Flask(__name__)
app.config['SECRET_KEY'] = 'tsp-secret-key-2026'

# Support CORS for all environments
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')

# Active solve session tracking
current_stop_flag = None

ALL_INSTANCES = [
    'pr152', 'd198', 'ts225', 'pr226', 'a280',
    'lin318', 'fl417', 'pr439', 'pcb442', 'd493'
]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/instances')
def list_instances():
    instances = []
    for inst in ALL_INSTANCES:
        path = os.path.join(DATA_DIR, f"{inst}.tsp")
        if os.path.exists(path):
            data = parse_tsp(path)
            instances.append({
                'name': inst,
                'dimension': data['dimension'],
                'optimal': KNOWN_OPTIMALS.get(inst)
            })
    return jsonify(instances)

@socketio.on('load_instance')
def handle_load_instance(data):
    inst_name = data.get('instance', 'pr152')
    filepath = os.path.join(DATA_DIR, f"{inst_name}.tsp")
    if os.path.exists(filepath):
        parsed = parse_tsp(filepath)
        emit('instance_loaded', {
            'name': parsed['name'],
            'dimension': parsed['dimension'],
            'coords': parsed['coords'].tolist()
        })

@socketio.on('start_solve')
def handle_start_solve(data):
    global current_stop_flag
    current_stop_flag = threading.Event()
    stop_flag = current_stop_flag

    inst_name = data.get('instance', 'pr152')
    heuristics = data.get('heuristics', None)
    restarts = int(data.get('n_restarts', 8))
    filepath = os.path.join(DATA_DIR, f"{inst_name}.tsp")

    if not os.path.exists(filepath):
        emit('error', {'message': f'Instance {inst_name} not found'})
        return

    def solver_thread():
        last_emit_time = [0.0]

        def callback(stage, tour, distance):
            now = time.time()
            # Throttle WebSocket emissions to max ~25 fps so the browser stays responsive
            if stage in ('complete', 'nn_complete', '2-opt_complete', 'or-opt_complete',
                         '3-opt_complete', 'lk-opt_complete', 'sa_complete', 'ils_complete') or (now - last_emit_time[0] > 0.04):
                last_emit_time[0] = now
                socketio.emit('tour_update', {
                    'stage': stage,
                    'tour': tour,
                    'distance': distance
                })
                # Yield execution briefly
                time.sleep(0.005)

        try:
            result = solve(
                filepath=filepath,
                enabled_heuristics=heuristics,
                callback=callback,
                n_restarts=restarts,
                stop_flag=stop_flag
            )
            socketio.emit('solve_complete', result)
        except Exception as e:
            socketio.emit('error', {'message': str(e)})

    threading.Thread(target=solver_thread, daemon=True).start()

@socketio.on('stop_solve')
def handle_stop_solve():
    global current_stop_flag
    if current_stop_flag:
        current_stop_flag.set()

@socketio.on('run_all_benchmarks')
def handle_run_all(data):
    global current_stop_flag
    current_stop_flag = threading.Event()
    stop_flag = current_stop_flag

    heuristics = data.get('heuristics', None)
    restarts = int(data.get('n_restarts', 5))

    def batch_thread():
        for inst in ALL_INSTANCES:
            if stop_flag.is_set():
                break

            filepath = os.path.join(DATA_DIR, f"{inst}.tsp")
            if not os.path.exists(filepath):
                continue

            last_emit = [0.0]
            def cb(stage, tour, dist):
                now = time.time()
                if now - last_emit[0] > 0.06:
                    last_emit[0] = now
                    socketio.emit('tour_update', {
                        'stage': f"{inst}: {stage}",
                        'tour': tour,
                        'distance': dist
                    })
                    time.sleep(0.005)

            try:
                # Preload coords
                parsed = parse_tsp(filepath)
                socketio.emit('instance_loaded', {
                    'name': parsed['name'],
                    'dimension': parsed['dimension'],
                    'coords': parsed['coords'].tolist()
                })

                res = solve(filepath, enabled_heuristics=heuristics, callback=cb,
                            n_restarts=restarts, stop_flag=stop_flag)
                socketio.emit('benchmark_step', res)
            except Exception as e:
                print(f"Error on {inst}: {e}")

        socketio.emit('benchmark_complete')

    threading.Thread(target=batch_thread, daemon=True).start()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    socketio.run(app, host='0.0.0.0', port=port, debug=False, allow_unsafe_werkzeug=True)

