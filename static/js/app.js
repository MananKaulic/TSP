// Global Application State
let socket;
let renderer;
let convergenceChart;
let isSolving = false;
let startTime = null;
let timerInterval = null;
let currentCoords = null;
let benchmarkResults = [];

const KNOWN_OPTIMALS = {
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
};

const STAGE_LABELS = {
    'nearest_neighbor': 'Nearest Neighbor',
    'nearest_neighbor_best': 'Multi-Start NN',
    'nn_complete': 'NN Complete',
    '2-opt': '2-Opt Local Search',
    '2-opt_complete': '2-Opt Done',
    'or-opt': 'Or-Opt Relocation',
    'or-opt_complete': 'Or-Opt Done',
    '3-opt': '3-Opt Reconnection',
    '3-opt_complete': '3-Opt Done',
    'lk-opt': 'Lin-Kernighan Search',
    'lk-opt_complete': 'LK Done',
    'simulated_annealing': 'Simulated Annealing',
    'sa_complete': 'SA Done',
    'ils': 'ILS Double Bridge Kick',
    'ils_progress': 'ILS Iteration',
    'ils_complete': 'ILS Done',
    'complete': 'Optimization Complete'
};

document.addEventListener('DOMContentLoaded', () => {
    initVisualizer();
    initSocket();
    initEventListeners();
    updateOptimalMetric();
});

function initVisualizer() {
    const svgEl = document.getElementById('tour-svg');
    renderer = new TourRenderer(svgEl, []);

    const chartCanvas = document.getElementById('convergence-canvas');
    convergenceChart = new ConvergenceChart(chartCanvas);

    window.addEventListener('resize', () => {
        if (renderer) renderer.resize();
    });
}

function initSocket() {
    socket = io();

    socket.on('connect', () => {
        document.getElementById('status-indicator').classList.add('connected');
        document.getElementById('connection-text').textContent = 'Connected (Live)';
    });

    socket.on('disconnect', () => {
        document.getElementById('status-indicator').classList.remove('connected');
        document.getElementById('connection-text').textContent = 'Disconnected';
    });

    socket.on('instance_loaded', (data) => {
        currentCoords = data.coords;
        renderer.updateCoords(currentCoords);
        document.getElementById('empty-state').classList.add('hidden');
        document.getElementById('active-instance-title').textContent =
            `Instance: ${data.name} (${data.dimension} cities)`;
    });

    socket.on('tour_update', (data) => {
        if (data.coords && (!currentCoords || currentCoords.length === 0)) {
            currentCoords = data.coords;
            renderer.updateCoords(currentCoords);
            document.getElementById('empty-state').classList.add('hidden');
        }

        if (data.tour && data.tour.length > 1) {
            renderer.drawTour(data.tour);
        }

        updateLiveMetrics(data.stage, data.distance);
        convergenceChart.addPoint(data.stage, data.distance);
    });

    socket.on('solve_complete', (data) => {
        setSolvingState(false);
        updateLiveMetrics('complete', data.best_distance);
        document.getElementById('badge-stage').textContent = 'Completed ✓';

        // Add to benchmark table
        addBenchmarkResult({
            name: data.instance_name,
            dimension: data.dimension,
            distance: data.best_distance,
            optimal: data.known_optimal,
            gap: data.gap_percent
        });
    });

    socket.on('benchmark_step', (data) => {
        addBenchmarkResult({
            name: data.instance_name,
            dimension: data.dimension,
            distance: data.best_distance,
            optimal: data.known_optimal,
            gap: data.gap_percent
        });
    });

    socket.on('benchmark_complete', () => {
        setSolvingState(false);
        document.getElementById('badge-stage').textContent = 'Benchmarks Complete';
    });
}

function initEventListeners() {
    const instanceSelect = document.getElementById('instance-select');
    instanceSelect.addEventListener('change', () => {
        updateOptimalMetric();
        loadInstanceData(instanceSelect.value);
    });

    const restartsSlider = document.getElementById('restarts-slider');
    restartsSlider.addEventListener('input', (e) => {
        document.getElementById('restarts-val').textContent = e.target.value;
    });

    document.getElementById('btn-solve').addEventListener('click', startSolve);
    document.getElementById('btn-stop').addEventListener('click', stopSolve);
    document.getElementById('btn-benchmark').addEventListener('click', startAllBenchmarks);
    document.getElementById('btn-export-csv').addEventListener('click', exportCSV);

    // Initial preload of default instance
    loadInstanceData(instanceSelect.value);
}

function loadInstanceData(instanceName) {
    if (isSolving) return;
    socket.emit('load_instance', { instance: instanceName });
}

function startSolve() {
    const instance = document.getElementById('instance-select').value;
    const heuristics = Array.from(document.querySelectorAll('.h-checkbox:checked')).map(cb => cb.value);
    const restarts = parseInt(document.getElementById('restarts-slider').value, 10);

    setSolvingState(true);
    convergenceChart.reset();

    socket.emit('start_solve', {
        instance: instance,
        heuristics: heuristics,
        n_restarts: restarts
    });
}

function stopSolve() {
    socket.emit('stop_solve');
    setSolvingState(false);
}

function startAllBenchmarks() {
    const heuristics = Array.from(document.querySelectorAll('.h-checkbox:checked')).map(cb => cb.value);
    const restarts = parseInt(document.getElementById('restarts-slider').value, 10);

    setSolvingState(true);
    document.getElementById('benchmark-tbody').innerHTML = '';
    benchmarkResults = [];

    socket.emit('run_all_benchmarks', {
        heuristics: heuristics,
        n_restarts: restarts
    });
}

function setSolvingState(active) {
    isSolving = active;
    document.getElementById('btn-solve').disabled = active;
    document.getElementById('btn-benchmark').disabled = active;
    document.getElementById('btn-stop').disabled = !active;

    const pulse = document.getElementById('solver-pulse');
    if (active) {
        pulse.classList.add('active');
        startTime = Date.now();
        timerInterval = setInterval(() => {
            const elapsed = ((Date.now() - startTime) / 1000).toFixed(1);
            document.getElementById('val-time').textContent = `${elapsed}s`;
        }, 100);
    } else {
        pulse.classList.remove('active');
        if (timerInterval) clearInterval(timerInterval);
    }
}

function updateOptimalMetric() {
    const instance = document.getElementById('instance-select').value;
    const optimal = KNOWN_OPTIMALS[instance];
    document.getElementById('val-optimal').textContent = optimal ? optimal.toLocaleString() : '—';
}

function updateLiveMetrics(stage, distance) {
    const stageLabel = STAGE_LABELS[stage] || stage;
    document.getElementById('badge-stage').textContent = stageLabel;
    document.getElementById('val-distance').textContent = distance ? distance.toLocaleString() : '—';

    const instance = document.getElementById('instance-select').value;
    const optimal = KNOWN_OPTIMALS[instance];
    if (optimal && distance) {
        const gap = ((distance / optimal - 1.0) * 100).toFixed(2);
        const gapEl = document.getElementById('val-gap');
        gapEl.textContent = `${gap}%`;
        gapEl.style.color = gap < 3.0 ? '#00f0a8' : (gap < 6.0 ? '#00d2ff' : '#ffb800');
    }
}

function addBenchmarkResult(item) {
    // Check if item exists in results
    const existingIndex = benchmarkResults.findIndex(b => b.name === item.name);
    if (existingIndex >= 0) {
        benchmarkResults[existingIndex] = item;
    } else {
        benchmarkResults.push(item);
    }

    renderBenchmarkTable();
}

function renderBenchmarkTable() {
    const tbody = document.getElementById('benchmark-tbody');
    tbody.innerHTML = '';

    benchmarkResults.forEach(item => {
        const tr = document.createElement('tr');
        const gapClass = (item.gap !== null && item.gap < 2.5) ? 'gap-super' :
                         (item.gap !== null && item.gap < 5.0 ? 'gap-good' : 'gap-ok');

        tr.innerHTML = `
            <td><strong>${item.name}</strong></td>
            <td>${item.dimension}</td>
            <td>${item.distance ? item.distance.toLocaleString() : '—'}</td>
            <td>${item.optimal ? item.optimal.toLocaleString() : '—'}</td>
            <td class="${gapClass}">${item.gap !== null ? item.gap + '%' : '—'}</td>
        `;
        tbody.appendChild(tr);
    });
}

function exportCSV() {
    if (benchmarkResults.length === 0) {
        alert('No benchmark results to export yet! Run the solver first.');
        return;
    }

    let csvContent = 'data:text/csv;charset=utf-8,';
    csvContent += 'Instance,Dimension,Best Distance,Known Optimal,Gap (%)\n';

    benchmarkResults.forEach(r => {
        csvContent += `${r.name},${r.dimension},${r.distance},${r.optimal || ''},${r.gap || ''}\n`;
    });

    const encodedUri = encodeURI(csvContent);
    const link = document.createElement('a');
    link.setAttribute('href', encodedUri);
    link.setAttribute('download', 'tsp_hall_of_fame_results.csv');
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

