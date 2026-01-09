// Chart.js configurations for analytics dashboard

document.addEventListener('DOMContentLoaded', function() {
    // Initialize charts when page loads
    if (document.getElementById('kpiChart')) {
        loadKPIs();
    }
    if (document.getElementById('timeSeriesChart')) {
        loadTimeSeries();
    }
    if (document.getElementById('vendorChart')) {
        loadVendorAnalysis();
    }
});

async function loadKPIs() {
    try {
        const response = await fetch('/api/metrics/kpis');
        const data = await response.json();

        // Create KPI cards
        const kpiContainer = document.getElementById('kpiCards');
        kpiContainer.innerHTML = `
            <div class="col-md-3">
                <div class="card text-center">
                    <div class="card-body">
                        <h5 class="card-title">${data.total_invoices}</h5>
                        <p class="card-text">Total Invoices</p>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card text-center">
                    <div class="card-body">
                        <h5 class="card-title">$${data.total_value.toLocaleString()}</h5>
                        <p class="card-text">Total Value</p>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card text-center">
                    <div class="card-body">
                        <h5 class="card-title">${data.avg_processing_time}s</h5>
                        <p class="card-text">Avg Processing Time</p>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card text-center">
                    <div class="card-body">
                        <h5 class="card-title">${data.success_rate}%</h5>
                        <p class="card-text">Success Rate</p>
                    </div>
                </div>
            </div>
        `;
    } catch (error) {
        console.error('Error loading KPIs:', error);
    }
}

async function loadTimeSeries() {
    try {
        const response = await fetch('/api/metrics/time_series');
        const data = await response.json();

        const ctx = document.getElementById('timeSeriesChart').getContext('2d');
        new Chart(ctx, {
            type: 'line',
            data: {
                labels: data.labels,
                datasets: [{
                    label: 'Invoice Count',
                    data: data.counts,
                    borderColor: 'rgb(75, 192, 192)',
                    tension: 0.1
                }, {
                    label: 'Total Value',
                    data: data.values,
                    borderColor: 'rgb(255, 99, 132)',
                    yAxisID: 'y1',
                    tension: 0.1
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        type: 'linear',
                        display: true,
                        position: 'left',
                    },
                    y1: {
                        type: 'linear',
                        display: true,
                        position: 'right',
                        grid: {
                            drawOnChartArea: false,
                        },
                    }
                }
            }
        });
    } catch (error) {
        console.error('Error loading time series:', error);
    }
}

async function loadVendorAnalysis() {
    try {
        const response = await fetch('/api/metrics/top_vendors');
        const data = await response.json();

        const ctx = document.getElementById('vendorChart').getContext('2d');
        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: data.vendors,
                datasets: [{
                    label: 'Total Value',
                    data: data.values,
                    backgroundColor: 'rgba(54, 162, 235, 0.5)',
                    borderColor: 'rgba(54, 162, 235, 1)',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    } catch (error) {
        console.error('Error loading vendor analysis:', error);
    }
}

// File upload handling
function handleFileUpload() {
    const fileInput = document.getElementById('fileInput');
    const uploadArea = document.getElementById('uploadArea');
    const uploadButton = document.getElementById('uploadButton');
    const progressBar = document.getElementById('progressBar');
    const resultDiv = document.getElementById('result');

    if (!fileInput.files[0]) {
        alert('Please select a file first.');
        return;
    }

    const formData = new FormData();
    formData.append('file', fileInput.files[0]);

    uploadButton.disabled = true;
    progressBar.style.display = 'block';
    resultDiv.innerHTML = '';

    fetch('/api/extract_invoice', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            resultDiv.innerHTML = `
                <div class="alert alert-success">
                    <h5>Extraction Successful!</h5>
                    <p>Invoice ID: ${data.invoice_id}</p>
                    <a href="/invoice/${data.invoice_id}" class="btn btn-primary">View Details</a>
                </div>
            `;
        } else {
            resultDiv.innerHTML = `
                <div class="alert alert-danger">
                    <h5>Extraction Failed</h5>
                    <p>${data.message}</p>
                </div>
            `;
        }
    })
    .catch(error => {
        resultDiv.innerHTML = `
            <div class="alert alert-danger">
                <h5>Error</h5>
                <p>${error.message}</p>
            </div>
        `;
    })
    .finally(() => {
        uploadButton.disabled = false;
        progressBar.style.display = 'none';
    });
}

// Drag and drop functionality
document.addEventListener('DOMContentLoaded', function() {
    const uploadArea = document.getElementById('uploadArea');
    const fileInput = document.getElementById('fileInput');

    if (uploadArea && fileInput) {
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            uploadArea.addEventListener(eventName, preventDefaults, false);
        });

        ['dragenter', 'dragover'].forEach(eventName => {
            uploadArea.addEventListener(eventName, highlight, false);
        });

        ['dragleave', 'drop'].forEach(eventName => {
            uploadArea.addEventListener(eventName, unhighlight, false);
        });

        uploadArea.addEventListener('drop', handleDrop, false);
    }
});

function preventDefaults(e) {
    e.preventDefault();
    e.stopPropagation();
}

function highlight() {
    document.getElementById('uploadArea').classList.add('dragover');
}

function unhighlight() {
    document.getElementById('uploadArea').classList.remove('dragover');
}

function handleDrop(e) {
    const dt = e.dataTransfer;
    const files = dt.files;

    document.getElementById('fileInput').files = files;
}
