## Project Overview

This project automates the extraction and validation of structured data from unstructured invoices (PDFs, images) in multiple languages using AI techniques including OCR, NLP, and machine learning. The system aims to process invoices in English and Hindi, extracting key fields like vendor name, invoice number, date, line items, totals, and taxes, while performing validation and anomaly detection.

## Phase 1 Objectives (Days 1-5)

- Set up project structure and environment
- Implement basic OCR pipeline with Tesseract and EasyOCR
- Create preprocessing utilities for image enhancement
- Build minimal Streamlit UI prototype
- Develop unit tests for OCR functionality
- Produce working OCR proof-of-concept

## System Dependencies

### Ubuntu/Debian

```bash
sudo apt update
sudo apt install tesseract-ocr tesseract-ocr-eng tesseract-ocr-hin
```

### macOS

```bash
brew install tesseract
```

### Windows

Download and install Tesseract from: https://github.com/UB-Mannheim/tesseract/wiki
Add to PATH and install language packs for English and Hindi.

## Python Environment Setup

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## How to Run OCR Test

1. Place sample invoice images in `data/raw_invoices/` (e.g., invoice1.jpg, invoice2.png)
2. Run: `python src/ocr/ocr_test.py data/raw_invoices/invoice1.jpg`
3. Expected output: OCR text from both Tesseract and EasyOCR, saved to `outputs/ocr_texts.json`

## Project Structure

```
/project-root
  /data/raw_invoices      # Input invoice images/PDFs
  /data/processed         # Processed images
  /notebooks              # Jupyter notebooks for experimentation
  /src
    /ocr                  # OCR-related code
    /preprocessing        # Image preprocessing utilities
    /models               # ML models and training code
    /ui                   # Streamlit UI components
  /outputs                # Extracted data and results
  /docs                   # Documentation
```

## Usage

1. Install system dependencies
2. Set up Python virtual environment
3. Install Python packages
4. Run OCR test on sample invoice
5. # Extend with additional features in subsequent phases

# AI-Based Multi-Language Invoice Data Extraction and Validation System

## Project Overview

This project automates the extraction and validation of structured data from unstructured invoices (PDFs, images) using Google Gemini Vision API and Flask. The system processes invoices in multiple languages, extracting key fields like vendor name, invoice number, date, line items, totals, and taxes, while performing validation and anomaly detection.

## Architecture

The system uses a modern stack:

- **AI Extraction**: Google Gemini Vision API for document understanding
- **Web Framework**: Flask with REST API and Bootstrap UI
- **Database**: SQLAlchemy ORM with SQLite (dev) / PostgreSQL (prod)
- **Image Processing**: pdf2image + Pillow for PDF-to-image conversion

## Quick Start

### 1. Environment Setup

```bash
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your settings
# Required: GEMINI_API_KEY from Google AI Studio
```

### 3. Run the Application

```bash
# Initialize database
export FLASK_APP=src/ui/flask_app/app.py
flask shell -c "from src.db.session import init_db; init_db()"

# Run development server
flask run --host=0.0.0.0 --port=5000
```

### 4. Test the API

```bash
# Health check
curl http://localhost:5000/health

# Upload invoice (replace with actual file)
curl -X POST -F "file=@sample_invoice.pdf" http://localhost:5000/api/extract_invoice
```

## Project Structure

```
/project-root
  /data
    /raw_invoices/        # Input invoice files
    /processed/           # Processed data
    /testing_data/        # Test datasets
  /src
    /pipeline/            # Gemini extraction pipeline
    /ui/flask_app/        # Flask application
      /templates/         # Jinja2 templates
      /static/            # CSS/JS assets
    /db/                  # Database models and CRUD
    /analytics/           # KPI calculations
    /config/              # Settings and logging
    /exports/             # CSV export utilities
    /tests/               # Unit tests
  /docs/                  # Documentation
  /logs/                  # Application logs
```

## API Endpoints

- `POST /api/extract_invoice` - Upload and process invoice
- `GET /api/invoices` - List processed invoices
- `GET /api/invoices/{id}` - Get invoice details
- `GET /api/metrics/kpis` - System KPIs
- `GET /api/export/csv` - Export data as CSV

## Web Interface

- `/` - Home page
- `/invoices` - Invoice list with pagination
- `/invoice/{id}` - Detailed invoice view
- `/analytics` - Dashboard with charts
- `/api-docs` - Interactive API documentation

## Key Features

- **AI-Powered Extraction**: Google Gemini Vision API for accurate data extraction
- **Multi-format Support**: Handles PDFs, PNG, JPG, JPEG files
- **Validation & Anomalies**: Automatic data validation and anomaly detection
- **Analytics Dashboard**: Real-time KPIs and visualizations
- **REST API**: Full CRUD operations with JSON responses
- **Export Capabilities**: CSV download with filtering
- **Responsive UI**: Bootstrap-based web interface

## Development

```bash
# Run tests
pytest src/tests/

# Format code
black src/
isort src/

# Type checking
mypy src/
```

## Deployment

See `docs/deploy.md` for Docker and production deployment instructions.
