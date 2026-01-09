#!/usr/bin/env python3
"""
Phase 2 Model Inference Demo

This script demonstrates the LayoutLMv3 inference pipeline and compares
AI extraction results with regex-based extraction from Phase 1.
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

def cell_1_setup():
    """Cell 1: Setup and imports"""
    print("=== Phase 2 Model Inference Demo ===")
    print("Setting up AI extraction pipeline...")

    # Check if we're in the right directory
    if not os.path.exists('src'):
        print("ERROR: Run this from the project root directory")
        return False

    # Import our modules
    try:
        from src.pipeline.ai_extraction_pipeline import process_invoice_with_ai, batch_process_invoices
        from src.models.layoutlm.model_loader import load_layoutlm_model
        print("✓ Pipeline modules imported successfully")
        return True
    except ImportError as e:
        print(f"✗ Import error: {e}")
        print("Make sure all Phase 2 modules are created and requirements are installed")
        return False

def cell_2_sample_data():
    """Cell 2: Check for sample data"""
    print("\n=== Checking Sample Data ===")

    sample_dir = "data/raw_invoices"
    if os.path.exists(sample_dir):
        images = [f for f in os.listdir(sample_dir)
                 if f.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp'))]
        if images:
            print(f"✓ Found {len(images)} sample image(s): {images}")
            return images
        else:
            print("! No images found in data/raw_invoices/")
            print("  Add some invoice images to test the AI pipeline")
            return []
    else:
        print("! Sample directory not found: data/raw_invoices/")
        print("  Create it and add invoice images")
        return []

def cell_3_model_loading():
    """Cell 3: Test model loading"""
    print("\n=== Testing Model Loading ===")

    try:
        from src.models.layoutlm.model_loader import load_layoutlm_model, get_model_info

        # Load model
        processor, model, device = load_layoutlm_model()
        print("✓ LayoutLMv3 model loaded successfully"        print(f"  Device: {device}")

        # Get model info
        info = get_model_info()
        if "error" not in info:
            print(f"  Parameters: {info['total_parameters']:,}")
            print(f"  Model: {info['model_name']}")
        else:
            print(f"  Info error: {info['error']}")

        return True

    except Exception as e:
        print(f"✗ Model loading failed: {e}")
        print("Make sure transformers and torch are installed")
        return False

def cell_4_single_inference(image_path):
    """Cell 4: Run inference on single image"""
    print(f"\n=== Single Image Inference: {image_path} ===")

    if not os.path.exists(image_path):
        print(f"Image not found: {image_path}")
        return None

    try:
        # Run complete pipeline
        result = process_invoice_with_ai(image_path)

        if result.get("errors"):
            print(f"Errors encountered: {result['errors']}")

        # Print key results
        print("OCR Text preview:")
        ocr_text = result.get("ocr_text", "")
        print(f"  Length: {len(ocr_text)} characters")
        print(f"  Preview: {ocr_text[:100]}..." if len(ocr_text) > 100 else f"  Full: {ocr_text}")

        # AI extraction results
        ai_extraction = result.get("ai_extraction", {})
        if "schema" in ai_extraction:
            schema = ai_extraction["schema"]
            print("
AI Extracted Fields:")
            for field, data in schema.items():
                if field != "_validation" and isinstance(data, dict):
                    value = data.get("value", "")
                    conf = data.get("confidence", 0.0)
                    print(f"  {field}: '{value}' (conf: {conf:.2f})")

        # Comparison results
        comparison = result.get("comparison", {})
        metrics = comparison.get("overall_metrics", {})
        print("\nComparison Metrics:")
        print(f"  Data completeness: {metrics.get('data_completeness', 0):.1%}")
        print(f"  Method agreement: {metrics.get('agreement_rate', 0):.1%}")

        recommendations = comparison.get("recommendations", [])
        if recommendations:
            print(f"  Recommendations: {recommendations[0]}")

        return result

    except Exception as e:
        print(f"✗ Inference failed: {e}")
        return None

def cell_5_batch_processing(sample_images):
    """Cell 5: Batch processing demo"""
    print("\n=== Batch Processing Demo ===")

    if not sample_images:
        print("No sample images available for batch processing")
        return []

    try:
        # Process all images
        results = batch_process_invoices()

        print(f"✓ Processed {len(results)} invoices")

        # Summary statistics
        total_entities = sum(r.get("ai_extraction", {}).get("num_entities", 0) for r in results)
        avg_completeness = sum(
            r.get("comparison", {}).get("overall_metrics", {}).get("data_completeness", 0)
            for r in results
        ) / len(results) if results else 0

        print("\nBatch Summary:")
        print(f"  Total AI entities extracted: {total_entities}")
        print(f"  Average data completeness: {avg_completeness:.1%}")

        return results

    except Exception as e:
        print(f"✗ Batch processing failed: {e}")
        return []

def cell_6_evaluation_metrics(results):
    """Cell 6: Evaluation and metrics"""
    print("\n=== Evaluation Metrics ===")

    if not results:
        print("No results to evaluate")
        return

    # Calculate aggregate metrics
    total_invoices = len(results)
    successful_extractions = sum(1 for r in results if not r.get("errors"))

    ai_entities_total = sum(r.get("ai_extraction", {}).get("num_entities", 0) for r in results)
    avg_ai_entities = ai_entities_total / total_invoices if total_invoices > 0 else 0

    completeness_scores = [
        r.get("comparison", {}).get("overall_metrics", {}).get("data_completeness", 0)
        for r in results
    ]
    avg_completeness = sum(completeness_scores) / len(completeness_scores) if completeness_scores else 0

    agreement_scores = [
        r.get("comparison", {}).get("overall_metrics", {}).get("agreement_rate", 0)
        for r in results
    ]
    avg_agreement = sum(agreement_scores) / len(agreement_scores) if agreement_scores else 0

    print("Aggregate Performance Metrics:")
    print(f"  Total invoices processed: {total_invoices}")
    print(f"  Successful extractions: {successful_extractions}")
    print(f"  Success rate: {successful_extractions/total_invoices:.1%}" if total_invoices > 0 else "  Success rate: N/A")
    print(f"  Average AI entities per invoice: {avg_ai_entities:.1f}")
    print(f"  Average data completeness: {avg_completeness:.1%}")
    print(f"  Average method agreement: {avg_agreement:.1%}")

    # Field-level analysis
    field_success = {}
    for result in results:
        comparison = result.get("comparison", {})
        field_comparisons = comparison.get("field_comparisons", {})

        for field, comp in field_comparisons.items():
            if field not in field_success:
                field_success[field] = {"total": 0, "with_data": 0}

            field_success[field]["total"] += 1
            if comp.get("recommended_value"):
                field_success[field]["with_data"] += 1

    print("\nField Extraction Success Rates:")
    for field, stats in field_success.items():
        rate = stats["with_data"] / stats["total"] if stats["total"] > 0 else 0
        print(f"  {field}: {rate:.1%} ({stats['with_data']}/{stats['total']})")

def cell_7_save_evaluation(results):
    """Cell 7: Save evaluation results"""
    print("\n=== Saving Evaluation Results ===")

    if not results:
        print("No results to save")
        return

    try:
        # Create evaluation summary
        evaluation = {
            "evaluation_timestamp": datetime.now().isoformat(),
            "phase": "phase2_model_inference_demo",
            "total_invoices": len(results),
            "results_summary": []
        }

        for i, result in enumerate(results):
            summary = {
                "invoice_path": result.get("invoice_path", ""),
                "processing_time": result.get("processing_time_seconds", 0),
                "ai_entities": result.get("ai_extraction", {}).get("num_entities", 0),
                "data_completeness": result.get("comparison", {}).get("overall_metrics", {}).get("data_completeness", 0),
                "method_agreement": result.get("comparison", {}).get("overall_metrics", {}).get("agreement_rate", 0),
                "errors": result.get("errors", [])
            }
            evaluation["results_summary"].append(summary)

        # Save to file
        os.makedirs("data/processed", exist_ok=True)
        output_file = f"data/processed/phase2_evaluation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(evaluation, f, indent=2, ensure_ascii=False)

        print(f"✓ Evaluation results saved to: {output_file}")

    except Exception as e:
        print(f"✗ Failed to save evaluation: {e}")

def main():
    """Run the Phase 2 model inference demo"""
    print("Phase 2 Model Inference Demo - LayoutLMv3 Invoice Processing")
    print("=" * 60)

    # Cell 1: Setup
    if not cell_1_setup():
        return

    # Cell 2: Sample data
    sample_images = cell_2_sample_data()

    # Cell 3: Model loading
    if not cell_3_model_loading():
        print("Model loading failed - cannot proceed with inference")
        return

    # Cell 4: Single inference (if images available)
    single_result = None
    if sample_images:
        first_image = os.path.join("data/raw_invoices", sample_images[0])
        single_result = cell_4_single_inference(first_image)

    # Cell 5: Batch processing
    batch_results = cell_5_batch_processing(sample_images)

    # Combine results for evaluation
    all_results = []
    if single_result:
        all_results.append(single_result)
    all_results.extend(batch_results)

    # Remove duplicates (if single result is also in batch)
    seen_paths = set()
    unique_results = []
    for result in all_results:
        path = result.get("invoice_path", "")
        if path not in seen_paths:
            seen_paths.add(path)
            unique_results.append(result)

    # Cell 6: Evaluation
    cell_6_evaluation_metrics(unique_results)

    # Cell 7: Save results
    cell_7_save_evaluation(unique_results)

    print("\n" + "=" * 60)
    print("Phase 2 Model Inference Demo completed!")
    print("\nNext steps:")
    print("- Review the extracted entities and confidence scores")
    print("- Compare AI vs regex extraction results")
    print("- Fine-tune model or add more training data if needed")
    print("- Proceed to Flask UI integration (Phase 2 final step)")

if __name__ == "__main__":
    main()
