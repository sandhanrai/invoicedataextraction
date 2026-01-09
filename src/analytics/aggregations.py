"""
Analytics and KPI calculations for the Invoice AI Extraction System.

This module provides functions to compute various metrics and aggregations
from the processed invoice data.
"""

from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from datetime import datetime, timedelta
from typing import Dict, List, Any
from src.db.models import Invoice, Extraction, Anomaly

def kpis(db: Session) -> Dict[str, Any]:
    """Calculate key performance indicators."""
    total_invoices = db.query(Invoice).count()
    total_value = db.query(func.sum(Invoice.total)).filter(Invoice.total.isnot(None)).scalar() or 0.0

    # Average processing time (mock for now - would need timestamps)
    avg_processing_time = 3.2  # seconds

    # Success rate based on processed invoices
    processed_count = db.query(Invoice).filter(Invoice.status == "processed").count()
    success_rate = (processed_count / total_invoices * 100) if total_invoices > 0 else 0.0

    # Anomalies count
    total_anomalies = db.query(Anomaly).count()

    return {
        "total_invoices": total_invoices,
        "total_value": round(total_value, 2),
        "avg_processing_time": avg_processing_time,
        "success_rate": round(success_rate, 1),
        "total_anomalies": total_anomalies
    }

def top_vendors(db: Session, limit: int = 10) -> Dict[str, List]:
    """Get top vendors by total invoice value."""
    result = db.query(
        Invoice.vendor,
        func.sum(Invoice.total).label('total_value'),
        func.count(Invoice.id).label('invoice_count')
    ).filter(
        Invoice.vendor.isnot(None),
        Invoice.total.isnot(None)
    ).group_by(Invoice.vendor).order_by(
        func.sum(Invoice.total).desc()
    ).limit(limit).all()

    vendors = [row.vendor for row in result]
    values = [round(row.total_value, 2) for row in result]
    counts = [row.invoice_count for row in result]

    return {
        "vendors": vendors,
        "values": values,
        "counts": counts
    }

def invoices_over_time(db: Session, days: int = 30) -> Dict[str, List]:
    """Get invoice count and value over time."""
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)

    # Group by date
    result = db.query(
        func.date(Invoice.created_at).label('date'),
        func.count(Invoice.id).label('count'),
        func.sum(Invoice.total).label('total_value')
    ).filter(
        Invoice.created_at >= start_date,
        Invoice.created_at <= end_date
    ).group_by(func.date(Invoice.created_at)).order_by(func.date(Invoice.created_at)).all()

    labels = []
    counts = []
    values = []

    current_date = start_date.date()
    end_date_only = end_date.date()

    # Fill in missing dates with zeros
    data_dict = {row.date: (row.count, row.total_value or 0) for row in result}

    while current_date <= end_date_only:
        labels.append(current_date.strftime('%Y-%m-%d'))
        if current_date in data_dict:
            counts.append(data_dict[current_date][0])
            values.append(round(data_dict[current_date][1], 2))
        else:
            counts.append(0)
            values.append(0.0)
        current_date += timedelta(days=1)

    return {
        "labels": labels,
        "counts": counts,
        "values": values
    }

def vendor_performance(db: Session) -> List[Dict[str, Any]]:
    """Get detailed vendor performance metrics."""
    result = db.query(
        Invoice.vendor,
        func.count(Invoice.id).label('invoice_count'),
        func.sum(Invoice.total).label('total_value'),
        func.avg(Invoice.total).label('avg_invoice_value'),
        func.min(Invoice.created_at).label('first_invoice'),
        func.max(Invoice.created_at).label('last_invoice')
    ).filter(Invoice.vendor.isnot(None)).group_by(Invoice.vendor).all()

    vendors = []
    for row in result:
        vendors.append({
            "vendor": row.vendor,
            "invoice_count": row.invoice_count,
            "total_value": round(row.total_value or 0, 2),
            "avg_invoice_value": round(row.avg_invoice_value or 0, 2),
            "first_invoice": row.first_invoice.isoformat() if row.first_invoice else None,
            "last_invoice": row.last_invoice.isoformat() if row.last_invoice else None
        })

    return sorted(vendors, key=lambda x: x['total_value'], reverse=True)

def extraction_accuracy(db: Session) -> Dict[str, Any]:
    """Calculate extraction accuracy metrics."""
    total_extractions = db.query(Extraction).count()
    high_confidence = db.query(Extraction).filter(Extraction.confidence >= 0.8).count()

    accuracy_rate = (high_confidence / total_extractions * 100) if total_extractions > 0 else 0.0

    # Method breakdown
    method_counts = db.query(
        Extraction.method,
        func.count(Extraction.id).label('count'),
        func.avg(Extraction.confidence).label('avg_confidence')
    ).group_by(Extraction.method).all()

    methods = {}
    for row in method_counts:
        methods[row.method.value] = {
            "count": row.count,
            "avg_confidence": round(row.avg_confidence or 0, 2)
        }

    return {
        "total_extractions": total_extractions,
        "high_confidence_rate": round(accuracy_rate, 1),
        "methods": methods
    }

def anomaly_summary(db: Session) -> Dict[str, Any]:
    """Summarize anomalies by field and severity."""
    field_counts = db.query(
        Anomaly.field,
        func.count(Anomaly.id).label('count'),
        func.avg(Anomaly.score).label('avg_score')
    ).group_by(Anomaly.field).order_by(func.count(Anomaly.id).desc()).all()

    fields = []
    for row in field_counts:
        fields.append({
            "field": row.field,
            "count": row.count,
            "avg_score": round(row.avg_score or 0, 2)
        })

    total_anomalies = db.query(Anomaly).count()
    high_severity = db.query(Anomaly).filter(Anomaly.score >= 0.7).count()

    return {
        "total_anomalies": total_anomalies,
        "high_severity_rate": round((high_severity / total_anomalies * 100) if total_anomalies > 0 else 0, 1),
        "field_breakdown": fields
    }

def monthly_trends(db: Session, months: int = 12) -> Dict[str, List]:
    """Get monthly invoice trends."""
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=months*30)

    result = db.query(
        extract('year', Invoice.created_at).label('year'),
        extract('month', Invoice.created_at).label('month'),
        func.count(Invoice.id).label('count'),
        func.sum(Invoice.total).label('total_value')
    ).filter(
        Invoice.created_at >= start_date
    ).group_by(
        extract('year', Invoice.created_at),
        extract('month', Invoice.created_at)
    ).order_by(
        extract('year', Invoice.created_at),
        extract('month', Invoice.created_at)
    ).all()

    labels = []
    counts = []
    values = []

    for row in result:
        label = f"{int(row.year)}-{int(row.month):02d}"
        labels.append(label)
        counts.append(row.count)
        values.append(round(row.total_value or 0, 2))

    return {
        "labels": labels,
        "counts": counts,
        "values": values
    }
