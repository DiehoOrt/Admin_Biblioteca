document.addEventListener('DOMContentLoaded', function () {

    function init(id) {
        const el = document.getElementById(id);
        return {
            chart: echarts.init(el),
            data: JSON.parse(el.dataset.chart),
        };
    }

    // Responsive: redimensionar todos los charts al cambiar tamaño de ventana
    const chartIds = ['chartArea', 'chartEstados', 'chartLibros', 'chartLineas', 'chartMultas', 'chartIngresos'];
    window.addEventListener('resize', () => {
        chartIds.forEach(id => {
            const el = document.getElementById(id);
            if (el) echarts.getInstanceByDom(el)?.resize();
        });
    });

    // ── 1. Gradient Stacked Area — Préstamos vs Devoluciones ─────────────────
    const { chart: c1, data: area } = init('chartArea');
    c1.setOption({
        color: ['#0d6efd', '#198754'],
        tooltip: { trigger: 'axis' },
        legend: { data: ['Préstamos', 'Devoluciones'], bottom: 0 },
        grid: { left: '3%', right: '4%', bottom: '15%', containLabel: true },
        xAxis: { type: 'category', boundaryGap: false, data: area.labels },
        yAxis: { type: 'value', minInterval: 1 },
        series: [
            {
                name: 'Préstamos',
                type: 'line',
                stack: 'total',
                smooth: true,
                symbol: 'circle',
                symbolSize: 6,
                areaStyle: {
                    color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                        { offset: 0, color: 'rgba(13, 110, 253, 0.75)' },
                        { offset: 1, color: 'rgba(13, 110, 253, 0.05)' },
                    ]),
                },
                data: area.prestamos,
            },
            {
                name: 'Devoluciones',
                type: 'line',
                stack: 'total',
                smooth: true,
                symbol: 'circle',
                symbolSize: 6,
                areaStyle: {
                    color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                        { offset: 0, color: 'rgba(25, 135, 84, 0.75)' },
                        { offset: 1, color: 'rgba(25, 135, 84, 0.05)' },
                    ]),
                },
                data: area.devoluciones,
            },
        ],
    });

    // ── 2. Pie / Donut — Estado de préstamos ─────────────────────────────────
    const { chart: c2, data: estados } = init('chartEstados');
    c2.setOption({
        color: ['#198754', '#6c757d', '#dc3545'],
        tooltip: { trigger: 'item', formatter: '{b}: {c} ({d}%)' },
        legend: { bottom: 0, data: estados.labels },
        series: [{
            type: 'pie',
            radius: ['45%', '70%'],
            center: ['50%', '44%'],
            avoidLabelOverlap: false,
            label: { show: false, position: 'center' },
            emphasis: { label: { show: true, fontSize: 18, fontWeight: 'bold' } },
            labelLine: { show: false },
            data: estados.labels.map((l, i) => ({ name: l, value: estados.data[i] })),
        }],
    });

    // ── 3. Horizontal Bar — Top 5 libros más prestados ────────────────────────
    const { chart: c3, data: libros } = init('chartLibros');
    c3.setOption({
        tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
        grid: { left: '3%', right: '8%', bottom: '3%', containLabel: true },
        xAxis: { type: 'value', minInterval: 1 },
        yAxis: {
            type: 'category',
            data: libros.labels,
            axisLabel: { width: 130, overflow: 'truncate' },
        },
        series: [{
            type: 'bar',
            data: libros.data,
            barMaxWidth: 28,
            label: { show: true, position: 'right' },
            itemStyle: {
                borderRadius: [0, 5, 5, 0],
                color: new echarts.graphic.LinearGradient(1, 0, 0, 0, [
                    { offset: 0, color: '#ffc107' },
                    { offset: 1, color: '#fd7e14' },
                ]),
            },
        }],
    });

    // ── 4. Stacked Line — Préstamos por estado por mes ────────────────────────
    const { chart: c4, data: lineas } = init('chartLineas');
    c4.setOption({
        color: ['#198754', '#0d6efd', '#dc3545'],
        tooltip: { trigger: 'axis' },
        legend: { data: ['Devuelto', 'Activo', 'Vencido'], bottom: 0 },
        grid: { left: '3%', right: '4%', bottom: '15%', containLabel: true },
        xAxis: { type: 'category', data: lineas.labels },
        yAxis: { type: 'value', minInterval: 1 },
        series: [
            {
                name: 'Devuelto',
                type: 'line',
                stack: 'total',
                smooth: true,
                symbol: 'circle',
                symbolSize: 6,
                areaStyle: { opacity: 0.45 },
                data: lineas.devuelto,
            },
            {
                name: 'Activo',
                type: 'line',
                stack: 'total',
                smooth: true,
                symbol: 'circle',
                symbolSize: 6,
                areaStyle: { opacity: 0.45 },
                data: lineas.activo,
            },
            {
                name: 'Vencido',
                type: 'line',
                stack: 'total',
                smooth: true,
                symbol: 'circle',
                symbolSize: 6,
                areaStyle: { opacity: 0.45 },
                data: lineas.vencido,
            },
        ],
    });

    // ── 5. Bar — Ingresos por multas pagadas por mes ──────────────────────────
    const { chart: c5b, data: ingresos } = init('chartIngresos');
    c5b.setOption({
        tooltip: {
            trigger: 'axis',
            axisPointer: { type: 'shadow' },
            formatter: params => `${params[0].name}<br/>$ ${params[0].value.toFixed(2)}`,
        },
        grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
        xAxis: { type: 'category', data: ingresos.labels },
        yAxis: {
            type: 'value',
            axisLabel: { formatter: val => `$${val}` },
        },
        series: [{
            type: 'bar',
            data: ingresos.data,
            barMaxWidth: 48,
            itemStyle: {
                borderRadius: [5, 5, 0, 0],
                color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                    { offset: 0, color: '#6610f2' },
                    { offset: 1, color: '#a855f7' },
                ]),
            },
            label: {
                show: true,
                position: 'top',
                formatter: params => params.value > 0 ? `$${params.value.toFixed(2)}` : '',
            },
        }],
    });

    // ── 6. Pie / Donut — Estado de multas ─────────────────────────────────────
    const { chart: c5, data: multas } = init('chartMultas');
    c5.setOption({
        color: ['#ffc107', '#198754', '#6c757d'],
        tooltip: { trigger: 'item', formatter: '{b}: {c} ({d}%)' },
        legend: { bottom: 0, data: multas.labels },
        series: [{
            type: 'pie',
            radius: ['45%', '70%'],
            center: ['50%', '44%'],
            avoidLabelOverlap: false,
            label: { show: false, position: 'center' },
            emphasis: { label: { show: true, fontSize: 18, fontWeight: 'bold' } },
            labelLine: { show: false },
            data: multas.labels.map((l, i) => ({ name: l, value: multas.data[i] })),
        }],
    });
});
