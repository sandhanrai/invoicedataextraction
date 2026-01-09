#!/usr/bin/env python3
"""
Ingestion script to load processed invoice JSON files into the database.
"""

import os
import sys
import json
import argparse
from pathlib import Path
from typing import Dict, Any, List

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from db.session import SessionLocal, init_db
from db.crud import create_invoice_record, store_extraction, mark_anomaly
from db.models import ExtractionMethod

def load_json_file(filepath: str) -> Dict[str, Any]:
    """Load and parse a JSON file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def extract_invoice_data(json_data: Dict[str, Any]) -> Dict[str, Any]:
    """Extract invoice metadata from JSON data"""
    # Try to get data from different possible sources
    invoice_data = {}

    # Check if there's a schema section (from AI extraction)
    if "ai_extraction" in json_data and "schema" in json_data["ai_extraction"]:
        schema = json_data["ai_extraction"]["schema"]
        invoice_data.update({
            "vendor": schema.get("vendor_name", {}).get("value"),
            "invoice_no": schema.get("invoice_number", {}).get("value"),
            "date": schema.get("invoice_date", {}).get("value"),
            "subtotal": schema.get("subtotal", {}).get("value"),
            "tax": schema.get("tax_amount", {}).get("value"),
            "total": schema.get("total_amount", {}).get("value"),
            "currency": schema.get("currency", {}).get("value", "USD")
        })

    # Check regex extraction as fallback
    if not invoice_data.get("vendor") and "regex_extraction" in json_data:
        regex_data = json_data["regex_extraction"]
        invoice_data.update({
            "vendor": regex_data.get("vendor"),
            "invoice_no": regex_data.get("invoice_number"),
            "date": regex_data.get("date"),
            "total": regex_data.get("total")
        })

    return invoice_data

def ingest_single_file(db, json_filepath: str, commit: bool = True) -> bool:
    """Ingest a single JSON file into the database"""
    try:
        # Load JSON data
        json_data = load_json_file(json_filepath)

        # Extract basic invoice info
        invoice_info = extract_invoice_data(json_data)

        # Get filename and source path
        filename = Path(json_filepath).stem + ".png"  # Assume PNG for now
        source_path = f"data/raw_invoices/{filename}"

        # Create invoice record
        invoice = create_invoice_record(
            db=db,
            filename=filename,
            source_path=source_path,
            vendor=invoice_info.get("vendor"),
            invoice_no=invoice_info.get("invoice_no"),
            date=invoice_info.get("date"),
            subtotal=invoice_info.get("subtotal"),
            tax=invoice_info.get("tax"),
            total=invoice_info.get("total"),
            currency=invoice_info.get("currency", "USD")
        )

        print(f"Created invoice record: {invoice.id} - {invoice.filename}")

        # Store OCR extraction
        if "ocr_text" in json_data:
            store_extraction(
                db=db,
                invoice_id=invoice.id,
                method=ExtractionMethod.OCR,
                json_result={"ocr_text": json_data["ocr_text"]},
                confidence=1.0
            )

        # Store regex extraction
        if "regex_extraction" in json_data:
            store_extraction(
                db=db,
                invoice_id=invoice.id,
                method=ExtractionMethod.REGEX,
                json_result=json_data["regex_extraction"],
                confidence=json_data.get("regex_extraction", {}).get("confidence", 0.8)
            )

        # Store AI extraction
        if "ai_extraction" in json_data:
            ai_data = json_data["ai_extraction"]
            confidence = ai_data.get("overall_confidence", 0.7)
            store_extraction(
                db=db,
                invoice_id=invoice.id,
                method=ExtractionMethod.LAYOUTLM,
                json_result=ai_data,
                confidence=confidence
            )

        # Store anomalies if any
        if "anomalies" in json_data:
            for anomaly in json_data["anomalies"]:
                mark_anomaly(
                    db=db,
                    invoice_id=invoice.id,
                    field=anomaly.get("field", "unknown"),
                    reason=anomaly.get("reason", "Detected anomaly"),
                    score=anomaly.get("score", 0.5)
                )

        if commit:
            db.commit()
            print(f"Successfully ingested: {json_filepath}")
        else:
            db.rollback()
            print(f"Dry run - would ingest: {json_filepath}")

        return True

    except Exception as e:
        print(f"Error ingesting {json_filepath}: {e}")
        if commit:
            db.rollback()
        return False

def main():
    parser = argparse.ArgumentParser(description="Ingest processed invoice JSON files into database")
    parser.add_argument("--data-dir", default="data/processed", help="Directory containing JSON files")
    parser.add_argument("--pattern", default="*.json", help="File pattern to match")
    parser.add_argument("--commit", action="store_true", help="Actually commit changes to database")
    parser.add_argument("--reset-db", action="store_true", help="Reset database before ingesting")

    args = parser.parse_args()

    # Initialize database
    if args.reset_db:
        from db.session import reset_db
        reset_db()
    else:
        init_db()

    # Find JSON files
    data_dir = Path(args.data_dir)
    if not data_dir.exists():
        print(f"Data directory not found: {data_dir}")
        return

    json_files = list(data_dir.glob(args.pattern))
    if not json_files:
        print(f"No JSON files found in {data_dir}")
        return

    print(f"Found {len(json_files)} JSON files to process")

    # Process files
    db = SessionLocal()
    success_count = 0

    try:
        for json_file in json_files:
            if ingest_single_file(db, str(json_file), args.commit):
                success_count += 1

        print(f"\nIngestion complete: {success_count}/{len(json_files)} files processed successfully")

        if not args.commit:
            print("NOTE: This was a dry run. Use --commit to actually save to database.")

    finally:
        db.close()

if __name__ == "__main__":
    main()
