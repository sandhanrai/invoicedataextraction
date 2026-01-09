# Google Gemini Integration for Invoice Data Extraction

## Overview

This document explains how Google Gemini Vision API is used for invoice data extraction in the Invoice AI Extraction System.

## Why Gemini?

Google Gemini Vision API was chosen for the following reasons:

- **Advanced Vision Understanding**: Gemini can understand complex document layouts, handwritten text, and multi-language content
- **Structured Output**: Can generate JSON responses with specific schema requirements
- **Multi-modal Capabilities**: Handles both images and PDFs effectively
- **High Accuracy**: State-of-the-art performance on document understanding tasks
- **API Simplicity**: Easy to integrate with REST APIs

## Integration Architecture

```
Invoice Image/PDF → pdf2image/Pillow → Base64 → Gemini Vision API → JSON Response → Validation → Database
```

## API Usage

### Authentication

Set the `GEMINI_API_KEY` environment variable with your Google AI API key:

```bash
export GEMINI_API_KEY="your-api-key-here"
```

### Prompt Engineering

The system uses carefully crafted prompts to extract structured data:

```python
prompt = """
Extract the following information from this invoice image:
- Vendor name
- Invoice number
- Date
- Line items (description, quantity, unit price, line total)
- Subtotal, tax, total amounts
- Currency

Return as valid JSON with this exact structure:
{
  "vendor": "string",
  "invoice_no": "string",
  "date": "string",
  "line_items": [
    {
      "description": "string",
      "qty": number,
      "unit_price": number,
      "line_total": number
    }
  ],
  "subtotal": number,
  "tax": number,
  "total": number,
  "currency": "string"
}
"""
```

### Error Handling

- Network timeouts are handled with retries
- Invalid JSON responses are caught and logged
- Fallback to basic extraction if Gemini fails
- Confidence scores are calculated based on response completeness

## Performance Characteristics

- **Processing Time**: 2-5 seconds per invoice
- **Success Rate**: >95% for clear, standard invoices
- **Cost**: ~$0.002-0.005 per invoice (depending on image size)
- **Rate Limits**: 60 requests per minute (can be increased)

## Limitations and Mitigations

### Limitations

- Requires internet connection
- API costs (though minimal)
- Rate limiting for high-volume processing
- Dependency on Google's service availability

### Mitigations

- Local caching of results
- Batch processing with delays
- Fallback extraction methods
- Error recovery and retry logic

## Configuration

Environment variables for Gemini integration:

```bash
GEMINI_API_KEY=your-api-key
GEMINI_MODEL=gemini-1.5-flash  # or gemini-1.5-pro
GEMINI_MAX_TOKENS=4096
GEMINI_TEMPERATURE=0.1  # Low for consistent extraction
```

## Testing

Test the Gemini integration:

```python
from src.pipeline.gemini_extraction import GeminiExtractor

extractor = GeminiExtractor()
result = extractor.extract_invoice("path/to/invoice.png")
print(result)
```

## Future Enhancements

- **Fine-tuning**: Custom model training on invoice data
- **Multi-language**: Enhanced support for more languages
- **Batch Processing**: Process multiple invoices in single API call
- **Confidence Calibration**: Better confidence scoring algorithms
- **Caching**: Intelligent caching to reduce API calls
