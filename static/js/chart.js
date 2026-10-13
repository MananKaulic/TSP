class ConvergenceChart {
    constructor(canvasElement) {
        this.canvas = canvasElement;
        this.labels = [];
        this.distances = [];

        const ctx = this.canvas.getContext('2d');
        this.chart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: this.labels,
                datasets: [{
                    label: 'Tour Length (km/units)',
                    data: this.distances,
                    borderColor: '#00f0a8',
                    backgroundColor: 'rgba(0, 240, 168, 0.08)',
                    borderWidth: 2,
                    pointRadius: 0,
                    tension: 0.15,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                animation: false,
                interaction: {
                    intersect: false,
                    mode: 'index'
                },
                scales: {
                    x: {
                        display: true,
                        grid: {
                            color: 'rgba(255, 255, 255, 0.04)'
                        },
                        ticks: {
                            color: '#606782',
                            font: { family: 'JetBrains Mono', size: 10 },
                            maxTicksLimit: 8
                        }
                    },
                    y: {
                        display: true,
                        grid: {
                            color: 'rgba(255, 255, 255, 0.04)'
                        },
                        ticks: {
                            color: '#606782',
                            font: { family: 'JetBrains Mono', size: 10 },
                            callback: function(value) {
                                return value.toLocaleString();
                            }
                        }
                    }
                },
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        backgroundColor: '#14161f',
                        borderColor: '#363d59',
                        borderWidth: 1,
                        titleFont: { family: 'JetBrains Mono' },
                        bodyFont: { family: 'JetBrains Mono' },
                        callbacks: {
                            label: (ctx) => `Distance: ${Number(ctx.raw).toLocaleString()}`
                        }
                    }
                }
            }
        });
    }

    addPoint(stage, distance) {
        if (!distance || distance <= 0) return;
        this.labels.push(this.labels.length + 1);
        this.distances.push(distance);

        // Cap array to last 400 points to keep UI blazing fast
        if (this.labels.length > 400) {
            this.labels.shift();
            this.distances.shift();
        }

        this.chart.update('none');
    }

    reset() {
        this.labels.length = 0;
        this.distances.length = 0;
        this.chart.update();
    }
}

