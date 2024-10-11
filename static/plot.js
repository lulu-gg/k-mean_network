function renderPlots(data) {
    var pcaData = data.map(d => ({
        x: d.PCA1, 
        y: d.PCA2, 
        cluster: d.Cluster, 
        category: d.Category, 
        username: d.Username
    }));
    
    var histogramData = Array.from({ length: 5 }, (_, i) => data.filter(d => d.Cluster === i).length);
    
    var pca3DData = data.map(d => ({
        x: d.PCA1, 
        y: d.PCA2, 
        z: d.PCA3, 
        cluster: d.Cluster, 
        category: d.Category, 
        username: d.Username
    }));
    
    var pieData = histogramData.map((count, i) => ({ label: `Cluster ${i}`, value: count }));

    // PCA Plot
    var pcaChart = new Chart(document.getElementById('pcaPlot'), {
        type: 'scatter',
        data: {
            datasets: [{
                label: 'PCA Plot',
                data: pcaData.map(d => ({
                    x: d.x, 
                    y: d.y, 
                    username: d.username,
                    cluster: d.cluster,
                    category: d.category
                })),
                backgroundColor: pcaData.map(d => `rgba(${d.cluster * 50}, ${d.cluster * 25}, ${d.cluster * 75}, 0.7)`),
                pointRadius: 5,
                pointHoverRadius: 10,
            }]
        },
        options: {
            plugins: {
                tooltip: {
                    callbacks: {
                        label: function(tooltipItem) {
                            return `User: ${tooltipItem.raw.username}, Cluster: ${tooltipItem.raw.cluster}, Category: ${tooltipItem.raw.category}`;
                        }
                    }
                }
            },
            scales: {
                x: { title: { display: true, text: 'PCA1' } },
                y: { title: { display: true, text: 'PCA2' } }
            }
        }
    });

    // Histogram
    var histogramChart = new Chart(document.getElementById('histogram'), {
        type: 'bar',
        data: {
            labels: histogramData.map((_, i) => `Cluster ${i}`),
            datasets: [{
                label: 'Number of Points',
                data: histogramData,
                backgroundColor: 'rgba(75, 192, 192, 0.7)'
            }]
        },
        options: {
            scales: {
                x: { title: { display: true, text: 'Cluster' } },
                y: { title: { display: true, text: 'Number of Points' } }
            }
        }
    });

    // 3D PCA Plot (2D representation as Chart.js does not support 3D)
    var pca3DChart = new Chart(document.getElementById('3dPlot'), {
        type: 'bubble',
        data: {
            datasets: [{
                label: '3D PCA Plot (2D Representation)',
                data: pca3DData.map(d => ({
                    x: d.x, 
                    y: d.y, 
                    r: d.z / 1000, // Adjust radius for visualization
                    username: d.username,
                    cluster: d.cluster,
                    category: d.category
                })),
                backgroundColor: pca3DData.map(d => `rgba(${d.cluster * 50}, ${d.cluster * 25}, ${d.cluster * 75}, 0.7)`),
            }]
        },
        options: {
            plugins: {
                tooltip: {
                    callbacks: {
                        label: function(tooltipItem) {
                            return `User: ${tooltipItem.raw.username}, Cluster: ${tooltipItem.raw.cluster}, Category: ${tooltipItem.raw.category}`;
                        }
                    }
                }
            },
            scales: {
                x: { title: { display: true, text: 'PCA1' } },
                y: { title: { display: true, text: 'PCA2' } }
            }
        }
    });

    // Pie Chart
    var pieChart = new Chart(document.getElementById('pieChart'), {
        type: 'pie',
        data: {
            labels: pieData.map(d => d.label),
            datasets: [{
                label: 'Cluster Distribution',
                data: pieData.map(d => d.value),
                backgroundColor: pieData.map((d, i) => `rgba(${i * 50}, ${i * 25}, ${i * 75}, 0.7)`)
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'top',
                },
                title: {
                    display: true,
                    text: 'Cluster Distribution'
                }
            }
        }
    });
}
