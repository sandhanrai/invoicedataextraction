# AI Invoice Data Extraction System using Gemini Vision

A Flask-based web application that extracts structured data from invoice images and PDFs using **Google Gemini 2.5 Flash (multimodal vision model)**. The system converts unstructured invoice documents into structured, queryable data and provides analytics and export functionality.

---

## Features

* 📄 **Invoice Upload**

  * Supports PDF, PNG, JPG, and JPEG files
* 🤖 **AI-Powered Extraction**

  * Uses Google Gemini 2.5 Flash Vision for document understanding
* 🧾 **Structured Data Output**

  * Extracts invoice number, vendor, date, totals, tax, and line items
* 💾 **Database Storage**

  * Stores invoices and line items using SQLAlchemy (SQLite)
* 📊 **Analytics Dashboard**

  * Vendor spend analysis and invoice KPIs
* 📤 **CSV Export**

  * Export extracted invoice data to CSV format
* 🔌 **REST API**

  * API endpoints for programmatic invoice extraction and retrieval

---

## Tech Stack

| Layer               | Technology                                    |
| ------------------- | --------------------------------------------- |
| Backend             | Flask, SQLAlchemy                             |
| AI / ML             | Google Gemini 2.5 Flash (google-generativeai) |
| Document Processing | Pillow, pdf2image                             |
| Frontend            | HTML, Bootstrap 5, Chart.js                   |
| Database            | SQLite (default)                              |
| Deployment          | Local Flask development server                |

---

## How It Works (High-Level Flow)

1. User uploads an invoice (PDF or image)
2. PDF pages are converted to images (if applicable)
3. Image is sent to **Gemini 2.5 Flash Vision**
4. Gemini performs multimodal document understanding
5. Structured JSON is returned
6. Data is validated and stored in the database
7. Invoice is displayed, analyzed, and exportable

---

## Project Structure

```
.
├── config/
│   └── settings.py            # Environment and app configuration
├── data/                      # Uploaded invoice files
├── exports/                   # CSV exports
├── invoices.db                # SQLite database
├── src/
│   ├── pipeline/
│   │   └── gemini_extraction.py   # Gemini Vision extraction logic
│   ├── db/
│   │   ├── models.py              # SQLAlchemy models
│   │   ├── crud.py                # Database operations
│   │   └── session.py             # DB session management
│   ├── analytics/
│   │   └── aggregations.py        # KPI calculations
│   └── ui/
│       └── flask_app/
│           ├── app.py             # Flask application
│           ├── api.py             # REST API endpoints
│           ├── templates/         # Jinja2 templates
│           └── static/            # CSS & JS assets
├── requirements.txt
├── .env.example
├── README.md
└── test_invoice.png
```

---

## Setup Instructions

### 1. Clone Repository

```bash
git clone https://github.com/your-username/ai-invoice-extractor.git
cd ai-invoice-extractor
```

### 2. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

```bash
cp .env.example .env
```

Edit `.env`:

```
SECRET_KEY=your-secret-key
GEMINI_API_KEY=your-gemini-api-key
DATABASE_URL=sqlite:///invoices.db
```

> Get your API key from **Google AI Studio**

---

### 5. Run the Application

```bash
flask run
```

Open:
📍 `http://127.0.0.1:5000`

---

## Web Interface

* **Upload** – Upload invoices for extraction
* **Invoices** – View extracted invoices and line items
* **Analytics** – Vendor-wise and invoice-level insights
* **Export** – Download invoice data as CSV

---

## REST API Endpoints

### Extract Invoice

```http
POST /api/extract_invoice
Content-Type: multipart/form-data
```

**Response (Example)**

```json
{
  "invoice_no": "2577",
  "vendor": "INV24.COM",
  "date": "2024-02-27",
  "total": 1070.0,
  "tax": 83.82,
  "line_items": [
    {
      "description": "My products",
      "quantity": 3,
      "unit_price": 92.17,
      "line_total": 276.5
    }
  ]
}
```

---

### Get All Invoices

```http
GET /api/invoices
```

---

### Get Invoice by ID

```http
GET /api/invoices/{id}
```

---

### Get Analytics KPIs

```http
GET /api/metrics/kpis
```

---

## CSV Export Format

```
Field,Value
Invoice No,2577
Vendor,INV24.COM
Date,2024-02-27
Total,1070.00
Tax,83.82

Line Items
Description,Quantity,Unit Price,Line Total
My products,3,92.17,276.50
```

---

## AI Model Details

* **Model**: Gemini 2.5 Flash
* **Type**: Multimodal (Vision + Language)
* **Role**:

  * OCR + layout understanding
  * Semantic field extraction
  * Table and line item parsing
* **Why Flash**:

  * Faster inference
  * Lower cost
  * Ideal for document processing

---

## Data Science Relevance

This project demonstrates:

* Document AI & multimodal ML
* Unstructured → structured data pipelines
* Real-world data ingestion
* Feature extraction & aggregation
* Practical analytics and reporting
* End-to-end ML application deployment

---

## Limitations & Future Work

* No authentication yet
* No confidence scoring
* No multi-page invoice aggregation
* No model fine-tuning
* SQLite only (can be extended)

---

