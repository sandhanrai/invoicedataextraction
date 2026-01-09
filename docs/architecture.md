# Invoice AI Extraction System - Architecture Documentation

## Overview

The Invoice AI Extraction System is a comprehensive solution for processing invoice images using Google Gemini Vision API for AI-powered extraction. The system provides web interfaces, REST APIs, analytics dashboards, and data persistence capabilities.

## System Architecture

### Core Processing Pipeline

- **AI Extraction**: Google Gemini Vision API for document understanding and structured data extraction
- **Image Conversion**: pdf2image + Pillow for PDF-to-image processing
- **Validation**: Schema validation and anomaly detection
- **Persistence**: SQLAlchemy ORM for data storage and retrieval

### Production System

- **Database Layer**: SQLAlchemy ORM with SQLite (dev) / PostgreSQL (prod)
- **REST API**: Full CRUD operations with authentication
- **Web UI**: Bootstrap-based responsive interface
- **Analytics Engine**: KPI calculations and data visualization with Chart.js
- **Export Features**: CSV data export capabilities
- **Docker Support**: Containerized deployment

## Component Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Web Layer (Flask)                        │
│  ┌─────────────────────────────────────────────────────┐    │
│  │                 API Blueprint                        │    │
│  │  • /api/extract_invoice (POST)                       │    │
│  │  • /api/invoices (GET)                               │    │
│  │  • /api/invoices/<id> (GET)                          │    │
│  │  • /api/metrics/* (GET)                              │    │
│  │  • /api/export/csv (GET)                             │    │
│  └─────────────────────────────────────────────────────┘    │
│  ┌─────────────────────────────────────────────────────┐    │
│  │                 UI Routes                            │    │
│  │  • /invoices - Invoice list with pagination         │    │
│  │  • /invoice/<id> - Detail view                       │    │
│  │  • /analytics - Dashboard with charts               │    │
│  │  • /api-docs - API documentation                     │    │
│  └─────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────┐
│                 Business Logic Layer                       │
│  ┌─────────────────────────────────────────────────────┐    │
│  │            Gemini Extraction Pipeline               │    │
│  │  • Gemini Vision API inference                      │    │
│  │  • Schema mapping and validation                    │    │
│  │  • Confidence scoring                               │    │
│  └─────────────────────────────────────────────────────┘    │
│  ┌─────────────────────────────────────────────────────┐    │
│  │            Analytics Engine                         │    │
│  │  • KPI calculations                                 │    │
│  │  • Time series aggregation                          │    │
│  │  • Vendor analysis                                  │    │
│  └─────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────┐
│                 Data Access Layer                          │
│  ┌─────────────────────────────────────────────────────┐    │
│  │            SQLAlchemy ORM                            │    │
│  │  • Invoice, LineItem, Extraction, Anomaly models     │    │
│  │  • Session management                                │    │
│  │  • CRUD operations                                   │    │
│  └─────────────────────────────────────────────────────┘    │
│  ┌─────────────────────────────────────────────────────┐    │
│  │            Database (SQLite/PostgreSQL)             │    │
│  │  • Persistent storage                                │    │
│  │  • Transaction support                               │    │
│  │  • Query optimization                                │    │
│  └─────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

## Data Models

### Invoice Model

```python
class Invoice(Base):
    id: Primary Key
    filename: String (uploaded file name)
    source_path: String (file system path)
    vendor: String (extracted vendor name)
    invoice_no: String (invoice number)
    date: String (invoice date)
    subtotal: Float
    tax: Float
    total: Float
    currency: String (default: USD)
    status: String (processing status)
    created_at: DateTime
    updated_at: DateTime

    # Relationships
    line_items: List[LineItem]
    extractions: List[Extraction]
    anomalies: List[Anomaly]
```

### Extraction Model

```python
class Extraction(Base):
    id: Primary Key
    invoice_id: Foreign Key (Invoice)
    method: Enum (OCR, REGEX, LAYOUTLM)
    json_result: Text (extraction results)
    confidence: Float (0.0-1.0)
    created_at: DateTime
```

### Analytics Data Flow

1. **Data Ingestion**: Processed JSON files loaded into database
2. **KPI Calculation**: Real-time metrics computation
3. **Time Series**: Historical data aggregation
4. **Vendor Analysis**: Top performers by value/volume
5. **Export Generation**: CSV/JSON formatted downloads

## API Architecture

### Authentication

- API Key based authentication via `X-API-KEY` header
- Configurable keys for different environments
- Simple but extensible security model

### Response Formats

- JSON for all API responses
- Consistent error handling structure
- Pagination metadata for list endpoints

### Key Endpoints

#### Data Operations

- `POST /api/extract_invoice`: Process uploaded invoice
- `GET /api/invoices`: Paginated invoice list
- `GET /api/invoices/{id}`: Detailed invoice view

#### Analytics

- `GET /api/metrics/kpis`: System-wide KPIs
- `GET /api/metrics/top_vendors`: Vendor performance
- `GET /api/metrics/time_series`: Historical trends

#### Exports

- `GET /api/export/csv`: Filtered CSV download

## Deployment Architecture

### Docker Configuration

```yaml
services:
  invoice-ai-system:
    build: .
    ports:
      - "5000:5000"
    volumes:
      - ./data:/app/data
      - ./models/cache:/app/models/cache
    environment:
      - DATABASE_URL=sqlite:///./data/invoice_system.db
      - API_KEY=prod-key-secure-123
```

### Environment Variables

- `DATABASE_URL`: Database connection string
- `API_KEY`: API authentication key
- `FLASK_ENV`: Environment mode (development/production)
- `SECRET_KEY`: Flask session secret

## Security Considerations

### API Security

- API key authentication for all endpoints
- Input validation and sanitization
- File upload restrictions (size, type, content)

### Data Protection

- No sensitive data storage in logs
- Secure file handling with temporary paths
- Database connection security

### Container Security

- Non-root user execution
- Minimal base image dependencies
- Volume mounting for persistent data

## Performance Characteristics

### Processing Times

- OCR Extraction: 2-5 seconds per image
- AI Inference: 3-8 seconds per image
- Database Operations: <100ms per query
- API Response: <500ms for most endpoints

### Scalability Considerations

- Stateless API design for horizontal scaling
- Database connection pooling
- File-based caching for model artifacts
- Async processing for batch operations

## Monitoring and Observability

### Health Checks

- `/health` endpoint for service status
- Database connectivity verification
- Model loading status

### Logging

- Structured logging with timestamps
- Error tracking and alerting
- Performance metrics collection

### Metrics

- Processing success rates
- API response times
- Database query performance
- Model inference accuracy

## Future Enhancements

### Phase 4 Considerations

- **Microservices Architecture**: Separate services for OCR, AI, and API
- **Message Queue**: Async processing for large batches
- **Advanced Analytics**: ML-based anomaly detection
- **Multi-tenancy**: User/organization isolation
- **Cloud Integration**: AWS/Azure deployment options

### Technology Upgrades

- **GraphQL API**: More flexible data fetching
- **WebSocket Support**: Real-time processing updates
- **Advanced Caching**: Redis for session/model caching
- **CI/CD Pipeline**: Automated testing and deployment
