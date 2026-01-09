/**
 * Custom JavaScript for Invoice AI Extraction Flask App
 */

// Global variables
let uploadProgress = 0;
let processingStartTime = null;

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeFileUpload();
    initializeTooltips();
    initializeAlerts();
});

// File upload handling
function initializeFileUpload() {
    const fileInput = document.getElementById('invoice');
    const submitBtn = document.getElementById('submitBtn');

    if (fileInput && submitBtn) {
        fileInput.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                validateFile(file);
                updateSubmitButton(file, submitBtn);
            }
        });

        // Form submission handling
        const form = fileInput.closest('form');
        if (form) {
            form.addEventListener('submit', function(e) {
                processingStartTime = Date.now();
                showProcessingIndicator();
            });
        }
    }
}

// File validation
function validateFile(file) {
    const maxSize = 16 * 1024 * 1024; // 16MB
    const allowedTypes = ['image/png', 'image/jpeg', 'image/jpg', 'image/tiff', 'image/bmp', 'application/pdf'];

    let isValid = true;
    let errorMessage = '';

    if (file.size > maxSize) {
        isValid = false;
        errorMessage = `File size (${formatFileSize(file.size)}) exceeds maximum allowed size (16MB)`;
    } else if (!allowedTypes.includes(file.type)) {
        isValid = false;
        errorMessage = 'File type not supported. Please upload PNG, JPG, JPEG, TIFF, BMP, or PDF files.';
    }

    if (!isValid) {
        showAlert(errorMessage, 'danger');
        document.getElementById('invoice').value = '';
        return false;
    }

    return true;
}

// Update submit button based on file selection
function updateSubmitButton(file, button) {
    if (file) {
        const fileSize = formatFileSize(file.size);
        button.innerHTML = `<i class="fas fa-upload"></i> Process "${file.name}" (${fileSize})`;
        button.disabled = false;
    } else {
        button.innerHTML = `<i class="fas fa-upload"></i> Select File First`;
        button.disabled = true;
    }
}

// Show processing indicator
function showProcessingIndicator() {
    const indicator = document.getElementById('processingIndicator');
    if (indicator) {
        indicator.classList.remove('d-none');
    }
}

// Format file size
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// Show alert messages
function showAlert(message, type = 'info') {
    const alertContainer = document.createElement('div');
    alertContainer.className = `alert alert-${type} alert-dismissible fade show`;
    alertContainer.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;

    const container = document.querySelector('.container');
    if (container) {
        container.insertBefore(alertContainer, container.firstChild);
    }

    // Auto-dismiss after 5 seconds
    setTimeout(() => {
        if (alertContainer.parentNode) {
            alertContainer.remove();
        }
    }, 5000);
}

// Initialize Bootstrap tooltips
function initializeTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

// Initialize alert auto-dismiss
function initializeAlerts() {
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        if (!alert.querySelector('.btn-close')) {
            // Add close button if missing
            const closeBtn = document.createElement('button');
            closeBtn.type = 'button';
            closeBtn.className = 'btn-close';
            closeBtn.setAttribute('data-bs-dismiss', 'alert');
            alert.appendChild(closeBtn);
        }
    });
}

// Copy to clipboard functionality
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(function() {
        showAlert('Copied to clipboard!', 'success');
    }).catch(function(err) {
        console.error('Failed to copy: ', err);
        showAlert('Failed to copy to clipboard', 'warning');
    });
}

// Format confidence scores
function formatConfidence(confidence) {
    const percentage = Math.round(confidence * 100);
    let badgeClass = 'secondary';

    if (percentage >= 80) badgeClass = 'success';
    else if (percentage >= 60) badgeClass = 'warning';
    else badgeClass = 'danger';

    return `<span class="badge bg-${badgeClass}">${percentage}%</span>`;
}

// Format processing time
function formatProcessingTime(seconds) {
    if (seconds < 1) {
        return `${Math.round(seconds * 1000)}ms`;
    } else if (seconds < 60) {
        return `${seconds.toFixed(1)}s`;
    } else {
        const minutes = Math.floor(seconds / 60);
        const remainingSeconds = seconds % 60;
        return `${minutes}m ${remainingSeconds.toFixed(0)}s`;
    }
}

// Update results display with animations
function updateResultsDisplay(result) {
    const resultsSection = document.getElementById('resultsSection');
    if (resultsSection) {
        resultsSection.classList.add('fade-in');
    }

    // Update processing time display
    if (result.processing_time_seconds) {
        const timeElement = document.querySelector('.card-text.h4.text-primary');
        if (timeElement) {
            timeElement.textContent = formatProcessingTime(result.processing_time_seconds);
        }
    }

    // Add tooltips to confidence badges
    const badges = document.querySelectorAll('.badge');
    badges.forEach(badge => {
        const confidence = badge.textContent.replace('%', '');
        if (!isNaN(confidence)) {
            badge.setAttribute('data-bs-toggle', 'tooltip');
            badge.setAttribute('title', `Confidence: ${confidence}%`);
        }
    });

    // Re-initialize tooltips for dynamically added content
    initializeTooltips();
}

// API call helper
async function apiCall(endpoint, method = 'GET', data = null) {
    const config = {
        method: method,
        headers: {
            'Content-Type': 'application/json',
        }
    };

    if (data) {
        config.body = JSON.stringify(data);
    }

    try {
        const response = await fetch(endpoint, config);
        const result = await response.json();

        if (!response.ok) {
            throw new Error(result.message || 'API call failed');
        }

        return result;
    } catch (error) {
        console.error('API call error:', error);
        showAlert(`API Error: ${error.message}`, 'danger');
        throw error;
    }
}

// Health check
async function checkHealth() {
    try {
        const result = await apiCall('/health');
        const statusElement = document.querySelector('.health-status');

        if (statusElement) {
            statusElement.className = `health-status health-${result.status}`;
            statusElement.textContent = result.status.toUpperCase();
        }

        return result;
    } catch (error) {
        console.error('Health check failed:', error);
        return null;
    }
}

// Periodic health check (every 30 seconds)
setInterval(checkHealth, 30000);

// Export functions for global use
window.InvoiceApp = {
    copyToClipboard: copyToClipboard,
    formatConfidence: formatConfidence,
    formatProcessingTime: formatProcessingTime,
    apiCall: apiCall,
    checkHealth: checkHealth,
    showAlert: showAlert
};
