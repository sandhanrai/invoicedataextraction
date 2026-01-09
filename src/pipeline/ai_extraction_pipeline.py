"""
AI Extraction Pipeline

This module integrates Phase 1 OCR pipeline with LayoutLMv3 AI extraction,
providing a complete end-to-end invoice processing pipeline with comparison
between rule-based and AI-based extraction methods.
"""

import os
import sys
import json
import time
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Import Phase 1 modules (assuming they exist)
try:
    from src.ocr.ocr_test import run_tesseract, run_easyocr, preprocess_image
    from src.preprocessing.preprocess import preprocess_pipeline
    PHASE1_AVAILABLE = True
except ImportError as e:
    PHASE1_AVAILABLE = False
    print(f"Phase 1 import failed: {e}")

# Import AI modules
try:
    from src.models.layoutlm.inference import run_layoutlm_inference, extract_entities_from_predictions
    from src.models.layoutlm.schema_mapper import map_entities_to_schema, validate_schema_completeness
    AI_AVAILABLE = True
except ImportError as e:
    AI_AVAILABLE = False
    print(f"AI import failed: {e}")


def process_invoice_with_ai(invoice_path: str) -> Dict[str, Any]:
    """
    Complete pipeline: OCR -> AI Extraction -> Schema Mapping -> Comparison

    Args:
        invoice_path: Path to invoice image

    Returns:
        dict: Complete processing results including OCR text, AI extraction, and comparison
    """
    start_time = time.time()
    result = {
        "invoice_path": invoice_path,
        "processing_timestamp": datetime.now().isoformat(),
        "ocr_text": "",
        "regex_extraction": {},
        "ai_extraction": {},
        "comparison": {},
        "processing_time_seconds": 0,
        "errors": []
    }

    try:
        # Phase 1: OCR Processing
        print(f"Running Phase 1 OCR on: {invoice_path}")
        ocr_result = _run_phase1_ocr(invoice_path)
        result["ocr_text"] = ocr_result.get("ocr_text", "")
        result["regex_extraction"] = ocr_result.get("regex_extraction", {})

        # Phase 2: AI Extraction
        print("Running Phase 2 AI extraction...")
        ai_result = _run_ai_extraction(invoice_path, ocr_result)
        result["ai_extraction"] = ai_result

        # Comparison
        print("Comparing extraction methods...")
        result["comparison"] = _compare_extractions(
            result["regex_extraction"],
            result["ai_extraction"]
        )

        result["processing_time_seconds"] = time.time() - start_time
        print(f"Processing completed in {result["processing_time_seconds"]:.2f} seconds")
    except Exception as e:
        result["errors"].append(f"Pipeline error: {str(e)}")
        print(f"Pipeline error: {e}")

    return result


def _run_phase1_ocr(invoice_path: str) -> Dict[str, Any]:
    """
    Run Phase 1 OCR pipeline.

    Args:
        invoice_path: Path to invoice image

    Returns:
        dict: OCR results with text and basic regex extraction
    """
    if not PHASE1_AVAILABLE:
        return {
            "ocr_text": "Phase 1 modules not available",
            "regex_extraction": {},
            "error": "Phase 1 OCR pipeline not found"
        }

    try:
        # Load and preprocess image
        processed_image = preprocess_image(invoice_path)

        # Run OCR engines
        tesseract_text = run_tesseract(processed_image)
        easyocr_text = run_easyocr(processed_image)

        # Combine OCR texts (prefer Tesseract as primary)
        ocr_text = tesseract_text if tesseract_text else easyocr_text

        # Basic regex extraction (simplified - would use actual Phase 1 regex rules)
        regex_extraction = _basic_regex_extraction(ocr_text)

        return {
            "ocr_text": ocr_text,
            "tesseract_text": tesseract_text,
            "easyocr_text": easyocr_text,
            "regex_extraction": regex_extraction
        }

    except Exception as e:
        return {
            "ocr_text": f"OCR failed: {str(e)}",
            "regex_extraction": {},
            "error": str(e)
        }


def _run_ai_extraction(invoice_path: str, ocr_result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Run AI extraction using LayoutLMv3.

    Args:
        invoice_path: Path to invoice image
        ocr_result: Results from Phase 1 OCR

    Returns:
        dict: AI extraction results
    """
    if not AI_AVAILABLE:
        return {
            "error": "AI modules not available",
            "schema": {},
            "raw_predictions": {},
            "entities": []
        }

    try:
        # Run LayoutLMv3 inference
        predictions = run_layoutlm_inference(invoice_path)

        if "error" in predictions:
            return {
                "error": predictions["error"],
                "schema": {},
                "raw_predictions": predictions,
                "entities": []
            }

        # Extract entities
        entities = extract_entities_from_predictions(predictions)

        # Map to schema
        schema = map_entities_to_schema(entities)

        # Validate completeness
        validated_schema = validate_schema_completeness(schema)

        return {
            "schema": validated_schema,
            "raw_predictions": predictions,
            "entities": entities,
            "num_entities": len(entities),
            "entity_types": list(set(e["label"] for e in entities))
        }

    except Exception as e:
        return {
            "error": f"AI extraction failed: {str(e)}",
            "schema": {},
            "raw_predictions": {},
            "entities": []
        }


def _basic_regex_extraction(ocr_text: str) -> Dict[str, Any]:
    """
    Basic regex-based field extraction (simplified version of Phase 1).

    Args:
        ocr_text: OCR text from invoice

    Returns:
        dict: Extracted fields with basic confidence scores
    """
    import re

    extraction = {
        "invoice_no": {"value": "", "confidence": 0.0},
        "vendor": {"value": "", "confidence": 0.0},
        "date": {"value": "", "confidence": 0.0},
        "total": {"value": "", "confidence": 0.0}
    }

    if not ocr_text:
        return extraction

    text_lower = ocr_text.lower()

    # Invoice number patterns
    inv_patterns = [
        r'invoice\s*#?\s*([A-Z0-9\-]+)',
        r'inv\s*#?\s*([A-Z0-9\-]+)',
        r'bill\s*#?\s*([A-Z0-9\-]+)'
    ]

    for pattern in inv_patterns:
        match = re.search(pattern, text_lower, re.IGNORECASE)
        if match:
            extraction["invoice_no"] = {"value": match.group(1).upper(), "confidence": 0.8}
            break

    # Date patterns
    date_patterns = [
        r'date[:\s]*(\d{1,2}[/-]\d{1,2}[/-]\d{4})',
        r'(\d{4}[/-]\d{1,2}[/-]\d{1,2})',
        r'date[:\s]*(\w{3}\s+\d{1,2},?\s+\d{4})'
    ]

    for pattern in date_patterns:
        match = re.search(pattern, text_lower, re.IGNORECASE)
        if match:
            extraction["date"] = {"value": match.group(1), "confidence": 0.7}
            break

    # Total amount patterns
    total_patterns = [
        r'total[:\s]*[\$₹€£¥]?\s*([\d,]+\.?\d*)',
        r'amount[:\s]*[\$₹€£¥]?\s*([\d,]+\.?\d*)',
        r'grand\s+total[:\s]*[\$₹€£¥]?\s*([\d,]+\.?\d*)'
    ]

    for pattern in total_patterns:
        match = re.search(pattern, text_lower, re.IGNORECASE)
        if match:
            amount = match.group(1).replace(',', '')
            extraction["total"] = {"value": amount, "confidence": 0.75}
            break

    # Vendor extraction (simplified - look for company-like patterns)
    lines = ocr_text.split('\n')
    for line in lines[:5]:  # Check first few lines
        line = line.strip()
        if len(line) > 3 and not any(keyword in line.lower() for keyword in
                                    ['invoice', 'date', 'total', 'amount', 'bill']):
            # Look for company indicators
            if any(indicator in line.upper() for indicator in ['LTD', 'INC', 'CORP', 'CO.', 'LLC']):
                extraction["vendor"] = {"value": line, "confidence": 0.6}
                break

    return extraction


def _compare_extractions(regex_extraction: Dict, ai_extraction: Dict) -> Dict[str, Any]:
    """
    Compare regex-based and AI-based extractions.

    Args:
        regex_extraction: Results from regex extraction
        ai_extraction: Results from AI extraction

    Returns:
        dict: Comparison metrics and recommendations
    """
    comparison = {
        "field_comparisons": {},
        "overall_metrics": {},
        "recommendations": []
    }

    # Compare each field
    fields_to_compare = ["invoice_no", "vendor", "date", "total"]

    for field in fields_to_compare:
        regex_value = regex_extraction.get(field, {}).get("value", "")
        regex_conf = regex_extraction.get(field, {}).get("confidence", 0.0)

        ai_value = ai_extraction.get("schema", {}).get(field, {}).get("value", "")
        ai_conf = ai_extraction.get("schema", {}).get(field, {}).get("confidence", 0.0)

        # Simple comparison metrics
        both_present = bool(regex_value and ai_value)
        values_match = regex_value.lower().strip() == ai_value.lower().strip() if both_present else False

        field_comparison = {
            "regex_value": regex_value,
            "ai_value": ai_value,
            "regex_confidence": regex_conf,
            "ai_confidence": ai_conf,
            "both_present": both_present,
            "values_match": values_match,
            "recommended_value": "",
            "recommended_method": ""
        }

        # Determine recommendation
        if both_present and values_match:
            field_comparison["recommended_value"] = regex_value
            field_comparison["recommended_method"] = "either"
        elif ai_conf > regex_conf:
            field_comparison["recommended_value"] = ai_value
            field_comparison["recommended_method"] = "ai"
        elif regex_conf > ai_conf:
            field_comparison["recommended_value"] = regex_value
            field_comparison["recommended_method"] = "regex"
        elif ai_value:
            field_comparison["recommended_value"] = ai_value
            field_comparison["recommended_method"] = "ai"
        elif regex_value:
            field_comparison["recommended_value"] = regex_value
            field_comparison["recommended_method"] = "regex"

        comparison["field_comparisons"][field] = field_comparison

    # Overall metrics
    total_fields = len(fields_to_compare)
    fields_with_data = sum(1 for f in fields_to_compare
                          if comparison["field_comparisons"][f]["recommended_value"])
    matching_fields = sum(1 for f in fields_to_compare
                         if comparison["field_comparisons"][f]["values_match"])

    comparison["overall_metrics"] = {
        "total_fields": total_fields,
        "fields_with_data": fields_with_data,
        "matching_fields": matching_fields,
        "data_completeness": fields_with_data / total_fields if total_fields > 0 else 0,
        "agreement_rate": matching_fields / fields_with_data if fields_with_data > 0 else 0
    }

    # Generate recommendations
    if comparison["overall_metrics"]["agreement_rate"] > 0.8:
        comparison["recommendations"].append("High agreement between methods - use AI for better accuracy")
    elif comparison["overall_metrics"]["data_completeness"] < 0.5:
        comparison["recommendations"].append("Low data completeness - consider improving OCR quality")
    else:
        comparison["recommendations"].append("Moderate agreement - use confidence-weighted combination")

    return comparison


def save_pipeline_results(results: Dict[str, Any], output_dir: str = "data/processed/ai_extractions"):
    """
    Save pipeline results to JSON file.

    Args:
        results: Pipeline results
        output_dir: Output directory
    """
    os.makedirs(output_dir, exist_ok=True)

    # Generate filename from invoice path
    invoice_name = Path(results["invoice_path"]).stem
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{invoice_name}_ai_extraction_{timestamp}.json"

    output_path = os.path.join(output_dir, filename)

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"Results saved to: {output_path}")
    return output_path


def batch_process_invoices(invoice_dir: str = "data/raw_invoices") -> List[Dict[str, Any]]:
    """
    Process all invoices in a directory.

    Args:
        invoice_dir: Directory containing invoice images

    Returns:
        list: List of processing results
    """
    if not os.path.exists(invoice_dir):
        print(f"Invoice directory not found: {invoice_dir}")
        return []

    results = []
    image_extensions = {'.jpg', '.jpeg', '.png', '.tiff', '.bmp'}

    for file_path in Path(invoice_dir).iterdir():
        if file_path.suffix.lower() in image_extensions:
            print(f"Processing: {file_path.name}")
            result = process_invoice_with_ai(str(file_path))
            results.append(result)

            # Save individual results
            save_pipeline_results(result)

    return results


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="AI Invoice Extraction Pipeline")
    parser.add_argument("--image", help="Path to single invoice image")
    parser.add_argument("--batch", action="store_true", help="Process all images in data/raw_invoices")
    parser.add_argument("--output", default="data/processed/ai_extractions", help="Output directory")

    args = parser.parse_args()

    if args.batch:
        print("Running batch processing...")
        results = batch_process_invoices()
        print(f"Processed {len(results)} invoices")
    elif args.image:
        if not os.path.exists(args.image):
            print(f"Image not found: {args.image}")
            exit(1)

        print(f"Processing single image: {args.image}")
        result = process_invoice_with_ai(args.image)
        output_path = save_pipeline_results(result, args.output)
        print(f"Result saved to: {output_path}")

        # Print summary
        print("\n=== EXTRACTION SUMMARY ===")
        print(f"OCR Text length: {len(result.get('ocr_text', ''))}")
        print(f"AI Entities found: {result.get('ai_extraction', {}).get('num_entities', 0)}")

        comparison = result.get('comparison', {})
        metrics = comparison.get('overall_metrics', {})
        print(f"Data completeness: {metrics.get('data_completeness', 0):.1%}")
        print(f"Method agreement: {metrics.get('agreement_rate', 0):.1%}")
    else:
        print("Usage:")
        print("  python src/pipeline/ai_extraction_pipeline.py --image path/to/invoice.jpg")
        print("  python src/pipeline/ai_extraction_pipeline.py --batch")
