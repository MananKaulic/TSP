class TourRenderer {
    constructor(svgElement, coords) {
        this.svgEl = svgElement;
        this.coords = coords || [];
        this.svg = d3.select(svgElement);
        this.padding = 35;

        this.init();
    }

    init() {
        this.svg.selectAll('*').remove();

        const rect = this.svgEl.getBoundingClientRect();
        this.width = rect.width || 800;
        this.height = rect.height || 520;

        this.svg.attr('viewBox', `0 0 ${this.width} ${this.height}`)
                .attr('preserveAspectRatio', 'xMidYMid meet');

        // SVG filter for glow effect
        const defs = this.svg.append('defs');
        const filter = defs.append('filter')
            .attr('id', 'glow')
            .attr('x', '-20%')
            .attr('y', '-20%')
            .attr('width', '140%')
            .attr('height', '140%');

        filter.append('feGaussianBlur')
            .attr('stdDeviation', '2.5')
            .attr('result', 'coloredBlur');

        const feMerge = filter.append('feMerge');
        feMerge.append('feMergeNode').attr('in', 'coloredBlur');
        feMerge.append('feMergeNode').attr('in', 'SourceGraphic');

        // Layer groups
        this.edgeGlowGroup = this.svg.append('g').attr('class', 'edge-glow-layer');
        this.edgeGroup = this.svg.append('g').attr('class', 'edge-layer');
        this.cityGroup = this.svg.append('g').attr('class', 'city-layer');

        if (this.coords.length > 0) {
            this.computeScales();
            this.drawCities();
        }
    }

    updateCoords(newCoords) {
        this.coords = newCoords;
        this.computeScales();
        this.drawCities();
    }

    computeScales() {
        if (!this.coords || this.coords.length === 0) return;

        const xExtent = d3.extent(this.coords, d => d[0]);
        const yExtent = d3.extent(this.coords, d => d[1]);

        const dx = (xExtent[1] - xExtent[0]) || 1;
        const dy = (yExtent[1] - yExtent[0]) || 1;

        // Preserve aspect ratio
        const availW = this.width - 2 * this.padding;
        const availH = this.height - 2 * this.padding;

        const scale = Math.min(availW / dx, availH / dy);

        const cx = (xExtent[0] + xExtent[1]) / 2;
        const cy = (yExtent[0] + yExtent[1]) / 2;

        this.xScale = (x) => (this.width / 2) + (x - cx) * scale;
        // Invert Y axis for standard cartesian upward orientation
        this.yScale = (y) => (this.height / 2) - (y - cy) * scale;
    }

    drawCities() {
        if (!this.coords || this.coords.length === 0) return;

        const n = this.coords.length;
        const r = Math.max(2.2, Math.min(4.5, 30.0 / Math.sqrt(n)));

        this.cityGroup.selectAll('circle')
            .data(this.coords)
            .join('circle')
            .attr('cx', d => this.xScale(d[0]))
            .attr('cy', d => this.yScale(d[1]))
            .attr('r', r)
            .attr('fill', '#00d2ff')
            .attr('stroke', '#ffffff')
            .attr('stroke-width', 0.8)
            .attr('opacity', 0.95);
    }

    drawTour(tour, strokeColor = '#00f0a8', strokeWidth = 1.8) {
        if (!tour || tour.length < 2 || !this.coords || this.coords.length === 0) return;

        const pathPoints = tour.map(idx => [
            this.xScale(this.coords[idx][0]),
            this.yScale(this.coords[idx][1])
        ]);

        // Close circuit back to tour[0]
        pathPoints.push(pathPoints[0]);

        const lineGenerator = d3.line()
            .x(d => d[0])
            .y(d => d[1])
            .curve(d3.curveLinear);

        const dString = lineGenerator(pathPoints);

        // Glow line behind
        this.edgeGlowGroup.selectAll('path').remove();
        this.edgeGlowGroup.append('path')
            .attr('d', dString)
            .attr('fill', 'none')
            .attr('stroke', strokeColor)
            .attr('stroke-width', strokeWidth + 2.5)
            .attr('stroke-opacity', 0.28)
            .attr('filter', 'url(#glow)');

        // Crisp sharp line in front
        this.edgeGroup.selectAll('path').remove();
        this.edgeGroup.append('path')
            .attr('d', dString)
            .attr('fill', 'none')
            .attr('stroke', strokeColor)
            .attr('stroke-width', strokeWidth)
            .attr('stroke-linejoin', 'round')
            .attr('stroke-linecap', 'round')
            .attr('stroke-opacity', 0.92);
    }

    resize() {
        this.init();
    }
}

