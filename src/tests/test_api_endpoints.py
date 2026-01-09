"""
Tests for API endpoints.
"""

import pytest
import json
from io import BytesIO
from unittest.mock import patch, MagicMock

from ui.flask_app.app import app
from db.session import reset_db

@pytest.fixture(scope="function")
def test_client():
    """Create a test client for the Flask app."""
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'test-secret-key'

    # Use test database
    with app.test_client() as client:
        with app.app_context():
            reset_db()  # Reset database for each test
        yield client

@pytest.fixture(scope="function")
def api_headers():
    """API headers with authentication."""
    return {
        'X-API-KEY': 'dev-key-12345'
    }

def create_test_image():
    """Create a mock image file for testing."""
    # Create a simple PNG-like bytes object
    image_data = b'\x89PNG\r\n\x1a\n' + b'0' * 100  # Minimal PNG header + data
    return BytesIO(image_data)

@patch('ui.flask_app.api_blueprint.process_invoice_with_ai')
def test_extract_invoice_success(mock_process, test_client, api_headers):
    """Test successful invoice extraction."""
    # Mock the processing result
    mock_process.return_value = {
        'invoice_path': '/path/to/test.png',
        'processing_timestamp': '2024-01-15T10:00:00',
        'ocr_text': 'Sample OCR text',
        'ai_extraction': {
            'schema': {
                'vendor_name': {'value': 'Test Vendor'},
                'invoice_number': {'value': 'INV-001'},
                'total_amount': {'value': 110.00}
            }
        },
        'regex_extraction': {
            'vendor': 'Test Vendor',
            'invoice_number': 'INV-001',
            'total': 110.00
        },
        'comparison': {
            'overall_metrics': {
                'data_completeness': 0.85,
                'agreement_rate': 0.90
            }
        },
        'processing_time_seconds': 2.5
    }

    # Create test image
    image_file = create_test_image()

    # Make request
    response = test_client.post(
        '/api/extract_invoice',
        data={
            'file': (image_file, 'test.png')
        },
        headers=api_headers,
        content_type='multipart/form-data'
    )

    assert response.status_code == 200
    data = json.loads(response.data)

    assert data['status'] == 'success'
    assert 'result' in data
    assert data['result']['ocr_text_length'] > 0
    assert 'ai_extraction' in data['result']

@patch('ui.flask_app.api_blueprint.process_invoice_with_ai')
def test_extract_invoice_no_file(mock_process, test_client, api_headers):
    """Test extract invoice without file."""
    response = test_client.post('/api/extract_invoice', headers=api_headers)

    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data

def test_extract_invoice_invalid_api_key(test_client):
    """Test extract invoice with invalid API key."""
    response = test_client.post(
        '/api/extract_invoice',
        headers={'X-API-KEY': 'invalid-key'}
    )

    assert response.status_code == 401

def test_get_invoices_empty(test_client, api_headers):
    """Test getting invoices when database is empty."""
    response = test_client.get('/api/invoices', headers=api_headers)

    assert response.status_code == 200
    data = json.loads(response.data)

    assert 'invoices' in data
    assert 'pagination' in data
    assert len(data['invoices']) == 0

def test_get_kpis(test_client, api_headers):
    """Test getting KPIs."""
    response = test_client.get('/api/metrics/kpis', headers=api_headers)

    assert response.status_code == 200
    data = json.loads(response.data)

    # Should return KPI structure even if empty
    assert isinstance(data, dict)
    assert 'total_invoices' in data
    assert 'total_anomalies' in data

def test_get_top_vendors(test_client, api_headers):
    """Test getting top vendors."""
    response = test_client.get('/api/metrics/top_vendors', headers=api_headers)

    assert response.status_code == 200
    data = json.loads(response.data)

    assert isinstance(data, list)

def test_get_time_series(test_client, api_headers):
    """Test getting time series data."""
    response = test_client.get('/api/metrics/time_series', headers=api_headers)

    assert response.status_code == 200
    data = json.loads(response.data)

    assert isinstance(data, list)

def test_api_docs(test_client):
    """Test API documentation endpoint."""
    response = test_client.get('/api/docs')

    assert response.status_code == 200
    data = json.loads(response.data)

    assert 'title' in data
    assert 'version' in data
    assert 'endpoints' in data

def test_health_endpoint(test_client):
    """Test health check endpoint."""
    response = test_client.get('/health')

    assert response.status_code == 200
    data = json.loads(response.data)

    assert data['status'] == 'healthy'
    assert 'timestamp' in data

# Test invalid requests
def test_invalid_endpoint(test_client, api_headers):
    """Test accessing invalid endpoint."""
    response = test_client.get('/api/invalid', headers=api_headers)

    assert response.status_code == 404

def test_missing_api_key(test_client):
    """Test accessing API without key."""
    response = test_client.get('/api/invoices')

    assert response.status_code == 401

def test_csv_export(test_client, api_headers):
    """Test CSV export functionality."""
    response = test_client.get('/api/export/csv', headers=api_headers)

    assert response.status_code == 200
    assert response.content_type == 'text/csv'
    assert 'attachment' in response.headers.get('Content-Disposition', '')

    # Check CSV content
    csv_content = response.data.decode('utf-8')
    assert 'ID,Filename,Vendor' in csv_content  # Header check
