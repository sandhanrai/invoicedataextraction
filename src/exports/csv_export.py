"""
CSV export functionality for invoice data.
"""

import csv
import io
from typing import List, Dict, Any
from db.session import get_db
from db.crud import query_invoices_for_export

def export_invoices_to_csv(vendor: str = None, date_from: str = None, date_to: str = None) -> str:
    """
    Export invoices to CSV string format.

    Args:
        vendor: Filter by vendor name
        date_from: Filter from date (YYYY-MM-DD)
        date_to: Filter to date (YYYY-MM-DD)

    Returns:
        CSV content as string
    """
    db = next(get_db())

    try:
        # Get invoice data
        invoices = query_invoices_for_export(
            db=db,
            vendor=vendor,
            date_from=date_from,
            date_to=date_to
        )

        # Create CSV output
        output = io.StringIO()
        writer = csv.writer(output)

        # Write header
        writer.writerow([
            'ID',
            'Filename',
            'Vendor',
            'Invoice No',
            'Date',
            'Subtotal',
            'Tax',
            'Total',
            'Currency',
            'Status',
            'Created At'
        ])

        # Write data rows
        for invoice in invoices:
            writer.writerow([
                invoice.id,
                invoice.filename,
                invoice.vendor or '',
                invoice.invoice_no or '',
                invoice.date or '',
                invoice.subtotal or '',
                invoice.tax or '',
                invoice.total or '',
                invoice.currency,
                invoice.status,
                invoice.created_at.strftime('%Y-%m-%d %H:%M:%S') if invoice.created_at else ''
            ])

        return output.getvalue()

    finally:
        db.close()

def export_invoices_with_details_to_csv(vendor: str = None, date_from: str = None, date_to: str = None) -> str:
    """
    Export invoices with detailed information including line items and extractions.

    Args:
        vendor: Filter by vendor name
        date_from: Filter from date (YYYY-MM-DD)
        date_to: Filter to date (YYYY-MM-DD)

    Returns:
        CSV content as string with detailed information
    """
    from db.crud import list_invoices

    db = next(get_db())

    try:
        # Get detailed invoice data
        result = list_invoices(
            db=db,
            page=1,
            per_page=1000,  # Large number to get all
            vendor=vendor,
            date_from=date_from,
            date_to=date_to
        )

        invoices = result.get('invoices', [])

        # Create CSV output
        output = io.StringIO()
        writer = csv.writer(output)

        # Write header
        writer.writerow([
            'Invoice ID',
            'Filename',
            'Vendor',
            'Invoice No',
            'Date',
            'Subtotal',
            'Tax',
            'Total',
            'Currency',
            'Status',
            'Line Items Count',
            'Extractions Count',
            'Anomalies Count',
            'Created At'
        ])

        # Write data rows
        for invoice in invoices:
            writer.writerow([
                invoice['id'],
                invoice['filename'],
                invoice.get('vendor') or '',
                invoice.get('invoice_no') or '',
                invoice.get('date') or '',
                invoice.get('subtotal') or '',
                invoice.get('tax') or '',
                invoice.get('total') or '',
                invoice.get('currency', 'USD'),
                invoice.get('status', 'unknown'),
                len(invoice.get('line_items', [])),
                len(invoice.get('extractions', [])),
                len(invoice.get('anomalies', [])),
                invoice.get('created_at', '')
            ])

        return output.getvalue()

    finally:
        db.close()

def get_csv_filename(base_name: str = "invoices_export") -> str:
    """
    Generate a timestamped CSV filename.

    Args:
        base_name: Base name for the file

    Returns:
        Filename with timestamp
    """
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{base_name}_{timestamp}.csv"
