"""
Flask API Blueprint for invoice processing and analytics.
"""

import os
import json
from flask import Blueprint, request, jsonify, current_app, send_file
from werkzeug.utils import secure_filename
from typing import Dict, Any, List
import tempfile
import io

from db.session import get_db
from db.crud import (
    list_invoices, get_invoice, create_invoice_record,
    store_extraction, mark_anomaly, query_invoices_for_export
)
from db.models import ExtractionMethod
from analytics.aggregations import kpis, top_vendors, invoices_over_time, distribution_buckets
from pipeline.ai_extraction_pipeline import process_invoice_with_ai
from preprocessing.preprocess import preprocess_image
from ocr.ocr_test import extract_text_from_image

# Create blueprint
api_bp = Blueprint('api', __name__, url_prefix='/api')

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'tiff', 'bmp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def require_api_key():
    """Simple API key authentication"""
    api_key = request.headers.get('X-API-KEY')
    expected_key = os.getenv('API_KEY', 'dev-key-12345')
    if api_key != expected_key:
        return jsonify({"error": "Invalid API key"}), 401
    return None

@api_bp.route('/extract_invoice', methods=['POST'])
def extract_invoice():
    """Extract data from uploaded invoice image"""
    # Check API key
    auth_error = require_api_key()
    if auth_error:
        return auth_error

    # Check if file is present
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400

    if not allowed_file(file.filename):
        return jsonify({"error": "File type not allowed"}), 400

    try:
        # Save uploaded file temporarily
        filename = secure_filename(file.filename)
        temp_dir = tempfile.mkdtemp()
        filepath = os.path.join(temp_dir, filename)
        file.save(filepath)

        # Process the invoice
        result = process_invoice_with_ai(filepath)

        # Store in database if processing was successful
        if result and not result.get("errors"):
            db = next(get_db())

            try:
                # Extract invoice data
                ai_extraction = result.get("ai_extraction", {})
                schema = ai_extraction.get("schema", {})

                # Create invoice record
                invoice = create_invoice_record(
                    db=db,
                    filename=filename,
                    source_path=filepath,
                    vendor=schema.get("vendor_name", {}).get("value"),
                    invoice_no=schema.get("invoice_number", {}).get("value"),
                    date=schema.get("invoice_date", {}).get("value"),
                    subtotal=schema.get("subtotal", {}).get("value"),
                    tax=schema.get("tax_amount", {}).get("value"),
                    total=schema.get("total_amount", {}).get("value"),
                    currency=schema.get("currency", {}).get("value", "USD")
                )

                # Store extractions
                if result.get("ocr_text"):
                    store_extraction(
                        db=db,
                        invoice_id=invoice.id,
                        method=ExtractionMethod.OCR,
                        json_result={"ocr_text": result["ocr_text"]},
                        confidence=1.0
                    )

                if result.get("regex_extraction"):
                    store_extraction(
                        db=db,
                        invoice_id=invoice.id,
                        method=ExtractionMethod.REGEX,
                        json_result=result["regex_extraction"],
                        confidence=result.get("regex_extraction", {}).get("confidence", 0.8)
                    )

                if ai_extraction:
                    store_extraction(
                        db=db,
                        invoice_id=invoice.id,
                        method=ExtractionMethod.LAYOUTLM,
                        json_result=ai_extraction,
                        confidence=ai_extraction.get("overall_confidence", 0.7)
                    )

                # Store anomalies
                comparison = result.get("comparison", {})
                field_comparisons = comparison.get("field_comparisons", {})
                for field, comp in field_comparisons.items():
                    if comp.get("conflict"):
                        mark_anomaly(
                            db=db,
                            invoice_id=invoice.id,
                            field=field,
                            reason=f"Conflict between methods: {comp.get('recommended_value')}",
                            score=0.8
                        )

                db.commit()
                result["invoice_id"] = invoice.id

            except Exception as e:
                db.rollback()
                current_app.logger.error(f"Database error: {e}")
            finally:
                db.close()

        # Clean up temp file
        os.unlink(filepath)
        os.rmdir(temp_dir)

        return jsonify(result)

    except Exception as e:
        current_app.logger.error(f"Processing error: {e}")
        return jsonify({"error": str(e)}), 500

@api_bp.route('/invoices', methods=['GET'])
def get_invoices():
    """Get paginated list of invoices with optional filters"""
    auth_error = require_api_key()
    if auth_error:
        return auth_error

    try:
        # Parse query parameters
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        vendor = request.args.get('vendor')
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')
        flagged = request.args.get('flagged', '').lower() == 'true'

        db = next(get_db())
        try:
            result = list_invoices(
                db=db,
                page=page,
                per_page=per_page,
                vendor=vendor,
                date_from=date_from,
                date_to=date_to,
                flagged=flagged
            )
            return jsonify(result)
        finally:
            db.close()

    except Exception as e:
        current_app.logger.error(f"Error fetching invoices: {e}")
        return jsonify({"error": str(e)}), 500

@api_bp.route('/invoices/<int:invoice_id>', methods=['GET'])
def get_invoice_detail(invoice_id):
    """Get detailed invoice information"""
    auth_error = require_api_key()
    if auth_error:
        return auth_error

    try:
        db = next(get_db())
        try:
            result = get_invoice(db, invoice_id)
            if result:
                return jsonify(result)
            else:
                return jsonify({"error": "Invoice not found"}), 404
        finally:
            db.close()

    except Exception as e:
        current_app.logger.error(f"Error fetching invoice {invoice_id}: {e}")
        return jsonify({"error": str(e)}), 500

@api_bp.route('/metrics/kpis', methods=['GET'])
def get_kpis():
    """Get key performance indicators"""
    auth_error = require_api_key()
    if auth_error:
        return auth_error

    try:
        db = next(get_db())
        try:
            result = kpis(db)
            return jsonify(result)
        finally:
            db.close()

    except Exception as e:
        current_app.logger.error(f"Error fetching KPIs: {e}")
        return jsonify({"error": str(e)}), 500

@api_bp.route('/metrics/top_vendors', methods=['GET'])
def get_top_vendors():
    """Get top vendors by value"""
    auth_error = require_api_key()
    if auth_error:
        return auth_error

    try:
        limit = int(request.args.get('limit', 10))
        db = next(get_db())
        try:
            result = top_vendors(db, limit)
            return jsonify(result)
        finally:
            db.close()

    except Exception as e:
        current_app.logger.error(f"Error fetching top vendors: {e}")
        return jsonify({"error": str(e)}), 500

@api_bp.route('/metrics/time_series', methods=['GET'])
def get_time_series():
    """Get invoice metrics over time"""
    auth_error = require_api_key()
    if auth_error:
        return auth_error

    try:
        granularity = request.args.get('granularity', 'month')
        db = next(get_db())
        try:
            result = invoices_over_time(db, granularity)
            return jsonify(result)
        finally:
            db.close()

    except Exception as e:
        current_app.logger.error(f"Error fetching time series: {e}")
        return jsonify({"error": str(e)}), 500

@api_bp.route('/export/csv', methods=['GET'])
def export_csv():
    """Export invoices to CSV"""
    auth_error = require_api_key()
    if auth_error:
        return auth_error

    try:
        # Parse filters
        vendor = request.args.get('vendor')
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')

        db = next(get_db())
        try:
            invoices = query_invoices_for_export(
                db=db,
                vendor=vendor,
                date_from=date_from,
                date_to=date_to
            )

            # Create CSV content
            output = io.StringIO()
            output.write("ID,Filename,Vendor,Invoice No,Date,Total,Currency,Status,Created At\n")

            for invoice in invoices:
                output.write(f"{invoice.id},{invoice.filename},{invoice.vendor or ''},{invoice.invoice_no or ''},{invoice.date or ''},{invoice.total or ''},{invoice.currency},{invoice.status},{invoice.created_at}\n")

            output.seek(0)

            return send_file(
                io.BytesIO(output.getvalue().encode('utf-8')),
                mimetype='text/csv',
                as_attachment=True,
                download_name='invoices_export.csv'
            )

        finally:
            db.close()

    except Exception as e:
        current_app.logger.error(f"Error exporting CSV: {e}")
        return jsonify({"error": str(e)}), 500

@api_bp.route('/docs', methods=['GET'])
def api_docs():
    """Simple API documentation"""
    docs = {
        "title": "Invoice Processing API",
        "version": "1.0.0",
        "description": "REST API for AI-powered invoice data extraction and analytics",
        "authentication": {
            "type": "API Key",
            "header": "X-API-KEY",
            "example": "X-API-KEY: your-api-key-here"
        },
        "endpoints": {
            "POST /api/extract_invoice": {
                "description": "Upload and process an invoice image",
                "parameters": {"file": "Invoice image file (PNG, JPG, etc.)"},
                "returns": "Processing results with extracted data"
            },
            "GET /api/invoices": {
                "description": "Get paginated list of invoices",
                "parameters": {
                    "page": "Page number (default: 1)",
                    "per_page": "Items per page (default: 20)",
                    "vendor": "Filter by vendor name",
                    "date_from": "Filter from date (YYYY-MM-DD)",
                    "date_to": "Filter to date (YYYY-MM-DD)",
                    "flagged": "Show only flagged invoices (true/false)"
                }
            },
            "GET /api/invoices/{id}": {
                "description": "Get detailed invoice information",
                "returns": "Invoice metadata, line items, extractions, anomalies"
            },
            "GET /api/metrics/kpis": {
                "description": "Get key performance indicators",
                "returns": "Total counts, values, processing stats"
            },
            "GET /api/metrics/top_vendors": {
                "description": "Get top vendors by invoice value",
                "parameters": {"limit": "Number of vendors to return (default: 10)"}
            },
            "GET /api/metrics/time_series": {
                "description": "Get invoice metrics over time",
                "parameters": {"granularity": "month/week/day (default: month)"}
            },
            "GET /api/export/csv": {
                "description": "Export invoices to CSV",
                "parameters": "Same as /api/invoices filters",
                "returns": "CSV file download"
            }
        }
    }

    return jsonify(docs)
