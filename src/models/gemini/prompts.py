"""
Prompt templates for Gemini API invoice extraction.

This module contains structured prompts for different types of
invoice data extraction tasks using Gemini API.
"""

INVOICE_EXTRACTION_PROMPT = """
You are an expert at extracting structured data from invoice documents. Analyze the provided invoice image and extract the following information in valid JSON format:

Required Fields:
- vendor_name: Company/vendor name (string)
- invoice_number: Invoice/bill number (string)
- invoice_date: Invoice date in YYYY-MM-DD format (string)
- total_amount: Total amount as number (float)
- currency: Currency code like USD, EUR, INR (string)

Optional Fields (if present):
- vendor_address: Vendor address (string)
- customer_name: Customer/client name (string)
- customer_address: Customer address (string)
- due_date: Payment due date in YYYY-MM-DD format (string)
- subtotal: Subtotal amount (float)
- tax_amount: Tax amount (float)
- discount_amount: Discount amount (float)
- line_items: Array of line items with description, quantity, unit_price, total (array)

For each extracted field, provide:
- value: The extracted value
- confidence: Confidence score from 0.0 to 1.0

Return ONLY valid JSON in this exact format:
{
  "vendor_name": {"value": "string", "confidence": 0.95},
  "invoice_number": {"value": "string", "confidence": 0.98},
  "invoice_date": {"value": "YYYY-MM-DD", "confidence": 0.90},
  "total_amount": {"value": 123.45, "confidence": 0.95},
  "currency": {"value": "USD", "confidence": 0.95},
  "vendor_address": {"value": "string", "confidence": 0.85},
  "customer_name": {"value": "string", "confidence": 0.90},
  "due_date": {"value": "YYYY-MM-DD", "confidence": 0.80},
  "subtotal": {"value": 100.00, "confidence": 0.90},
  "tax_amount": {"value": 23.45, "confidence": 0.85},
  "line_items": [
    {
      "description": "Item description",
      "quantity": 1,
      "unit_price": 100.00,
      "total": 100.00
    }
  ]
}

Important:
- Return ONLY the JSON object, no additional text
- Use null for missing values
- Ensure dates are in YYYY-MM-DD format
- Ensure amounts are numbers, not strings
- Be precise with the field names and structure
"""

MULTI_LANGUAGE_INVOICE_PROMPT = """
You are an expert at extracting structured data from invoice documents in multiple languages including English and Hindi. Analyze the provided invoice image and extract the following information in valid JSON format:

Required Fields:
- vendor_name: Company/vendor name (string)
- invoice_number: Invoice/bill number (string)
- invoice_date: Invoice date in YYYY-MM-DD format (string)
- total_amount: Total amount as number (float)
- currency: Currency code like USD, EUR, INR (string)

Optional Fields (if present):
- vendor_address: Vendor address (string)
- customer_name: Customer/client name (string)
- customer_address: Customer address (string)
- due_date: Payment due date in YYYY-MM-DD format (string)
- subtotal: Subtotal amount (float)
- tax_amount: Tax amount (float)
- discount_amount: Discount amount (float)
- line_items: Array of line items with description, quantity, unit_price, total (array)
- language_detected: Detected language of the document (string)

For each extracted field, provide:
- value: The extracted value
- confidence: Confidence score from 0.0 to 1.0

Return ONLY valid JSON in the same format as specified above.
Handle both English and Hindi text appropriately.
"""

TABLE_EXTRACTION_PROMPT = """
Focus on extracting tabular data from the invoice. Look for line items, itemized charges, and any tabular information. Return the line items in the following format:

{
  "line_items": [
    {
      "description": "Item description",
      "quantity": 1,
      "unit_price": 100.00,
      "total": 100.00,
      "confidence": 0.95
    }
  ]
}
"""

VALIDATION_PROMPT = """
Review the extracted invoice data and provide validation feedback. Check for:
1. Date format consistency
2. Amount calculations (subtotal + tax = total)
3. Logical consistency
4. Missing required fields

Return validation results in JSON format:
{
  "is_valid": true/false,
  "issues": ["list of issues found"],
  "recommendations": ["suggested fixes"],
  "confidence_score": 0.95
}
"""


def get_prompt_for_task(task: str = "standard") -> str:
    """
    Get the appropriate prompt for the extraction task.

    Args:
        task: Type of extraction task ("standard", "multi_lang", "table", "validation")

    Returns:
        str: The prompt template
    """
    prompts = {
        "standard": INVOICE_EXTRACTION_PROMPT,
        "multi_lang": MULTI_LANGUAGE_INVOICE_PROMPT,
        "table": TABLE_EXTRACTION_PROMPT,
        "validation": VALIDATION_PROMPT
    }

    return prompts.get(task, INVOICE_EXTRACTION_PROMPT)


def create_custom_prompt(required_fields: list, optional_fields: list = None) -> str:
    """
    Create a custom prompt for specific field extraction.

    Args:
        required_fields: List of required fields to extract
        optional_fields: List of optional fields to extract

    Returns:
        str: Custom prompt
    """
    if optional_fields is None:
        optional_fields = []

    prompt = """
You are an expert at extracting structured data from invoice documents. Analyze the provided invoice image and extract the following information in valid JSON format:

Required Fields:
"""

    for field in required_fields:
        prompt += f"- {field}: Description (type)\n"

    if optional_fields:
        prompt += "\nOptional Fields (if present):\n"
        for field in optional_fields:
            prompt += f"- {field}: Description (type)\n"

    prompt += """
For each extracted field, provide:
- value: The extracted value
- confidence: Confidence score from 0.0 to 1.0

Return ONLY valid JSON with the field structure.
"""

    return prompt
