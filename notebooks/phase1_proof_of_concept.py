#!/usr/bin/env python3
"""
Phase 1 Proof of Concept Notebook (Python Script Version)

This script demonstrates the OCR pipeline for invoice processing.
Since we can't create .ipynb files directly, this serves as the notebook content.

To run as a notebook:
1. Copy this content to a Jupyter notebook
2. Run cells sequentially
3. Add visualizations and experiments as needed

Usage:
    python notebooks/phase1_proof_of_concept.py
"""

import os
import sys
import json
from datetime import datetime

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

def cell_1_setup():
    """Cell 1: Setup and imports"""
    print("=== Phase 1 Proof of Concept ===")
    print("Setting up environment...")

    # Check if we're in the right directory
    if not os.path.exists('src'):
        print("ERROR: Run this from the project root directory")
        return False

    # Import our modules
    try:
        from src.preprocessing.preprocess import preprocess_pipeline
        from src.ocr.ocr_test import run_tesseract, run_easyocr, preprocess_image
        print("✓ Modules imported successfully")
        return True
    except ImportError as e:
        print(f"✗ Import error: {e}")
        print("Make sure requirements are installed: pip install -r requirements.txt")
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
            return images[0]  # Return first image
        else:
            print("! No images found in data/raw_invoices/")
            print("  Add some invoice images to test the pipeline")
            return None
    else:
        print("! Sample directory not found: data/raw_invoices/")
        print("  Create it and add invoice images")
        return None

def cell_3_preprocessing_demo(image_path):
    """Cell 3: Demonstrate preprocessing"""
    print("\n=== Preprocessing Demo ===")

    if not image_path:
        print("Skipping preprocessing demo - no image available")
        return None

    try:
        from src.preprocessing.preprocess import binarize, denoise
        import cv2

        # Load and preprocess
        full_path = os.path.join("data/raw_invoices", image_path)
        image = cv2.imread(full_path)

        print(f"Original image shape: {image.shape}")

        # Apply preprocessing steps
        denoised = denoise(image)
        binary = binarize(denoised)

        print("✓ Preprocessing completed")
        print(f"  - Denoised shape: {denoised.shape}")
        print(f"  - Binary shape: {binary.shape}")

        return binary

    except Exception as e:
        print(f"✗ Preprocessing error: {e}")
        return None

def cell_4_ocr_demo(processed_image):
    """Cell 4: Demonstrate OCR"""
    print("\n=== OCR Demo ===")

    if processed_image is None:
        print("Skipping OCR demo - no processed image")
        return

    try:
        # Run Tesseract
        print("Running Tesseract...")
        tesseract_result = run_tesseract(processed_image)
        print(f"Tesseract extracted {len(tesseract_result)} characters")

        # Run EasyOCR
        print("Running EasyOCR...")
        easyocr_result = run_easyocr(processed_image)
        print(f"EasyOCR extracted {len(easyocr_result)} characters")

        # Compare results
        print("\n=== Results Comparison ===")
        print("Tesseract (first 200 chars):")
        print(tesseract_result[:200] + "..." if len(tesseract_result) > 200 else tesseract_result)

        print("\nEasyOCR (first 200 chars):")
        print(easyocr_result[:200] + "..." if len(easyocr_result) > 200 else easyocr_result)

        return tesseract_result, easyocr_result

    except Exception as e:
        print(f"✗ OCR error: {e}")
        return None, None

def cell_5_save_results(image_name, tesseract_text, easyocr_text):
    """Cell 5: Save results"""
    print("\n=== Saving Results ===")

    if not tesseract_text or not easyocr_text:
        print("Skipping save - no OCR results")
        return

    try:
        # Create output directory
        os.makedirs("outputs", exist_ok=True)

        # Prepare result data
        result = {
            "filename": image_name,
            "tesseract_text": tesseract_text,
            "easyocr_text": easyocr_text,
            "timestamp": datetime.now().isoformat(),
            "phase": "proof_of_concept"
        }

        # Save to JSON
        output_file = "outputs/ocr_texts.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)

        print(f"✓ Results saved to {output_file}")

        # Show file size
        file_size = os.path.getsize(output_file)
        print(f"  File size: {file_size} bytes")

    except Exception as e:
        print(f"✗ Save error: {e}")

def main():
    """Run the proof of concept"""
    print("Phase 1 Proof of Concept - Invoice OCR Pipeline")
    print("=" * 50)

    # Cell 1: Setup
    if not cell_1_setup():
        return

    # Cell 2: Sample data
    sample_image = cell_2_sample_data()

    # Cell 3: Preprocessing
    processed = cell_3_preprocessing_demo(sample_image)

    # Cell 4: OCR
    tesseract_result, easyocr_result = cell_4_ocr_demo(processed)

    # Cell 5: Save results
    cell_5_save_results(sample_image, tesseract_result, easyocr_result)

    print("\n" + "=" * 50)
    print("Proof of concept completed!")
    print("\nNext steps:")
    print("- Add more sample invoices to data/raw_invoices/")
    print("- Experiment with different preprocessing parameters")
    print("- Compare OCR accuracy on different image types")
    print("- Proceed to Phase 2: Dataset collection and LayoutLM research")

if __name__ == "__main__":
    main()
