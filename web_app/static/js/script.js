document.addEventListener('DOMContentLoaded', function () {
    fetchData();
});

async function fetchData() {
    try {
        const response = await fetch('/api/data');
        const data = await response.json();

        if (data.status === 'success') {
            renderChart(data);
            updateKPIs(data);
        } else {
            console.error('Error fetching data:', data.message);
        }
    } catch (error) {
        console.error('Network error:', error);
    }
}

function updateKPIs(data) {
    // Calcular algunos KPIs en vivo
    const psoeIdx = data.labels.indexOf('PSOE');
    const ppIdx = data.labels.indexOf('PP');

    if (psoeIdx !== -1 && ppIdx !== -1) {
        const psoeOfficial = data.datasets.official[psoeIdx];
        const psoeBenedicto = data.datasets.benedicto[psoeIdx];

        // Sesgo Tezanos (Diferencia Oficial - Benedicto)
        const bias = (psoeOfficial - psoeBenedicto).toFixed(1);
        const biasEl = document.getElementById('bias-psoe');
        biasEl.innerHTML = `${bias > 0 ? '+' : ''}${bias}%`;
        biasEl.className = `value ${bias > 0 ? 'positive' : 'warning'}`; // Positive bias typically means overestimation
    }
}

function renderChart(data) {
    const ctx = document.getElementById('mainChart').getContext('2d');

    // Colores por partido (aunque aquí comparamos métodos, mejor usar colores por método para claridad)
    // O mejor: Agrupado por partido.

    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: data.labels,
            datasets: [
                {
                    label: 'Voto Directo (SIN COCINA)',
                    data: data.datasets.raw,
                    backgroundColor: '#e5e7eb',
                    borderColor: '#d1d5db',
                    borderWidth: 1,
                    barPercentage: 0.6,
                    categoryPercentage: 0.8
                },
                {
                    label: 'CIS Oficial (Tezanos)',
                    data: data.datasets.official,
                    backgroundColor: 'rgba(59, 130, 246, 0.2)', // Blueish transparent
                    borderColor: '#3b82f6',
                    borderWidth: 2,
                    barPercentage: 0.6,
                    categoryPercentage: 0.8
                },
                {
                    label: 'Estimación Benedicto-Gemini',
                    data: data.datasets.benedicto,
                    backgroundColor: 'rgba(16, 185, 129, 0.8)', // Green solid
                    borderColor: '#059669',
                    borderWidth: 2,
                    barPercentage: 0.7, // Slightly wider to stand out
                    categoryPercentage: 0.8
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'top',
                },
                tooltip: {
                    mode: 'index',
                    intersect: false,
                    callbacks: {
                        label: function (context) {
                            return `${context.dataset.label}: ${context.raw}%`;
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Estimación de Voto (%)'
                    }
                }
            }
        }
    });
}
