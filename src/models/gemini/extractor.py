"""
Gemini API Extractor for Invoice Data Extraction.

This module provides the GeminiExtractor class that uses Google's Gemini API
to extract structured data from invoice documents.
"""

import os
import json
import time
import logging
from typing import Dict, Any, Optional, List
from pathlib import Path
import google.generativeai as genai
from PIL import Image

from .prompts import get_prompt_for_task

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GeminiExtractor:
    """
    Extractor class for processing invoices using Google's Gemini API.
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Gemini extractor.

        Args:
            api_key: Google AI API key. If None, uses environment variable.
        """
        self.api_key = api_key or os.getenv("GOOGLE_AI_API_KEY")
        if not self.api_key:
            raise ValueError("Google AI API key not provided. Set GOOGLE_AI_API_KEY environment variable.")

        # Configure Gemini API
        genai.configure(api_key=self.api_key)

        # Initialize model
        self.model = genai.GenerativeModel('gemini-1.5-flash')

        # Generation config for consistent results
        self.generation_config = genai.types.GenerationConfig(
            temperature=0.1,
            top_p=0.8,
            top_k=40,
            max_output_tokens=4096,
        )

        logger.info("GeminiExtractor initialized successfully")

    def extract_invoice_data(self, image_path: str, prompt: str) -> Dict[str, Any]:
        """
        Extract invoice data from an image using Gemini API.

        Args:
            image_path: Path to the invoice image
            prompt: Extraction prompt to use

        Returns:
            Dict containing extraction results with metadata
        """
        start_time = time.time()

        try:
            # Validate image exists
            if not os.path.exists(image_path):
                raise FileNotFoundError(f"Image file not found: {image_path}")

            # Load and validate image
            image = Image.open(image_path)
            image.verify()  # Check if image is valid
            image = Image.open(image_path)  # Re-open after verify

            # Convert to RGB if necessary
            if image.mode not in ('RGB', 'RGBA'):
                image = image.convert('RGB')

            logger.info(f"Processing image: {image_path}")

            # Create content for Gemini
            content = [prompt, image]

            # Generate response
            response = self.model.generate_content(
                content,
                generation_config=self.generation_config
            )

            processing_time = time.time() - start_time

            # Parse response
            if response.text:
                try:
                    # Clean the response text
                    response_text = self._clean_response_text(response.text)

                    # Parse JSON
                    extracted_data = json.loads(response_text)

                    # Validate and structure the data
                    structured_data = self._structure_extracted_data(extracted_data)

                    return {
                        "success": True,
                        "data": structured_data,
                        "raw_response": response.text,
                        "processing_time": processing_time,
                        "model": "gemini-1.5-flash",
                        "usage": getattr(response, 'usage_metadata', None)
                    }

                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse Gemini response as JSON: {e}")
                    return {
                        "success": False,
                        "error": f"Invalid JSON response: {str(e)}",
                        "raw_response": response.text,
                        "processing_time": processing_time
                    }
            else:
                return {
                    "success": False,
                    "error": "Empty response from Gemini API",
                    "processing_time": processing_time
                }

        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(f"Error in extract_invoice_data: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "processing_time": processing_time
            }

    def _clean_response_text(self, text: str) -> str:
        """
        Clean the response text from Gemini API.

        Args:
            text: Raw response text

        Returns:
            Cleaned JSON string
        """
        # Remove markdown code blocks if present
        text = text.strip()
        if text.startswith("```json"):
            text = text[7:]
        elif text.startswith("```"):
            text = text[3:]

        if text.endswith("```"):
            text = text[:-3]

        text = text.strip()

        # Try to find JSON object boundaries
        start_idx = text.find("{")
        end_idx = text.rfind("}")

        if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
            text = text[start_idx:end_idx + 1]

        return text

    def _structure_extracted_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Structure and validate extracted data.

        Args:
            data: Raw extracted data from Gemini

        Returns:
            Structured data with consistent format
        """
        structured = {}

        # Define expected fields and their types
        field_mappings = {
            "vendor_name": str,
            "invoice_number": str,
            "invoice_date": str,
            "total_amount": (int, float),
            "currency": str,
            "vendor_address": str,
            "customer_name": str,
            "customer_address": str,
            "due_date": str,
            "subtotal": (int, float),
            "tax_amount": (int, float),
            "discount_amount": (int, float),
            "line_items": list,
            "language_detected": str
        }

        for field, expected_type in field_mappings.items():
            if field in data:
                value = data[field]

                # Handle confidence-based fields
                if isinstance(value, dict) and "value" in value:
                    structured[field] = value
                else:
                    # Create confidence structure
                    confidence = data.get(f"{field}_confidence", 0.8)
                    structured[field] = {
                        "value": value,
                        "confidence": float(confidence)
                    }

                # Type validation
                if field != "line_items":  # Special handling for line items
                    actual_value = structured[field]["value"]
                    if actual_value is not None:
                        if not isinstance(actual_value, expected_type):
                            try:
                                # Try type conversion
                                if expected_type == str:
                                    structured[field]["value"] = str(actual_value)
                                elif expected_type in (int, float):
                                    structured[field]["value"] = float(actual_value)
                            except (ValueError, TypeError):
                                logger.warning(f"Could not convert {field} to expected type {expected_type}")

        return structured

    def extract_batch(self, image_paths: List[str], prompt: str) -> List[Dict[str, Any]]:
        """
        Extract data from multiple images.

        Args:
            image_paths: List of image paths
            prompt: Extraction prompt

        Returns:
            List of extraction results
        """
        results = []

        for image_path in image_paths:
            result = self.extract_invoice_data(image_path, prompt)
            results.append(result)

            # Rate limiting - avoid hitting API limits
            time.sleep(1)

        return results

    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the current model configuration.

        Returns:
            Dict with model information
        """
        return {
            "model_name": "gemini-1.5-flash",
            "provider": "Google AI",
            "capabilities": ["text", "vision", "multimodal"],
            "supported_languages": ["English", "Hindi", "Multi-language"],
            "max_tokens": 4096,
            "temperature": 0.1
        }


def test_gemini_connection() -> bool:
    """
    Test the connection to Gemini API.

    Returns:
        True if connection successful, False otherwise
    """
    try:
        extractor = GeminiExtractor()
        info = extractor.get_model_info()
        logger.info(f"Gemini API connection successful: {info}")
        return True
    except Exception as e:
        logger.error(f"Gemini API connection failed: {e}")
        return False


if __name__ == "__main__":
    # Test the extractor
    print("Testing Gemini Extractor...")

    if test_gemini_connection():
        print("✓ Gemini API connection successful")

        # Test with sample image if available
        test_image = "data/testing_data/images/82251504.png"
        if os.path.exists(test_image):
            print(f"Testing extraction with: {test_image}")
            extractor = GeminiExtractor()
            prompt = get_prompt_for_task("standard")

            result = extractor.extract_invoice_data(test_image, prompt)

            if result["success"]:
                print("✓ Extraction successful!")
                print(f"Processing time: {result['processing_time']:.2f}s")
                print("Extracted data:")
                for field, data in result["data"].items():
                    if isinstance(data, dict) and "value" in data:
                        print(f"  {field}: {data['value']} (conf: {data.get('confidence', 0):.2f})")
            else:
                print(f"✗ Extraction failed: {result.get('error', 'Unknown error')}")
        else:
            print(f"Test image not found: {test_image}")
    else:
        print("✗ Gemini API connection failed")
