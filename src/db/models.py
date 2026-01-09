from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey, Enum
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime
import enum

Base = declarative_base()

class ExtractionMethod(enum.Enum):
    OCR = "ocr"
    REGEX = "regex"
    GEMINI = "gemini"

class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    source_path = Column(String(500), nullable=False)
    vendor = Column(String(255))
    invoice_no = Column(String(100))
    date = Column(String(50))
    subtotal = Column(Float)
    tax = Column(Float)
    total = Column(Float)
    currency = Column(String(10), default="USD")
    status = Column(String(50), default="processed")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    line_items = relationship("LineItem", back_populates="invoice", cascade="all, delete-orphan")
    extractions = relationship("Extraction", back_populates="invoice", cascade="all, delete-orphan")
    anomalies = relationship("Anomaly", back_populates="invoice", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Invoice(id={self.id}, filename='{self.filename}', vendor='{self.vendor}')>"

class LineItem(Base):
    __tablename__ = "line_items"

    id = Column(Integer, primary_key=True, index=True)
    invoice_id = Column(Integer, ForeignKey("invoices.id"), nullable=False)
    description = Column(String(500))
    qty = Column(Float)
    unit_price = Column(Float)
    line_total = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    invoice = relationship("Invoice", back_populates="line_items")

    def __repr__(self):
        return f"<LineItem(id={self.id}, invoice_id={self.invoice_id}, description='{self.description}')>"

class Extraction(Base):
    __tablename__ = "extractions"

    id = Column(Integer, primary_key=True, index=True)
    invoice_id = Column(Integer, ForeignKey("invoices.id"), nullable=False)
    method = Column(Enum(ExtractionMethod), nullable=False)
    json_result = Column(Text, nullable=False)
    confidence = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    invoice = relationship("Invoice", back_populates="extractions")

    def __repr__(self):
        return f"<Extraction(id={self.id}, invoice_id={self.invoice_id}, method='{self.method.value}')>"

class Anomaly(Base):
    __tablename__ = "anomalies"

    id = Column(Integer, primary_key=True, index=True)
    invoice_id = Column(Integer, ForeignKey("invoices.id"), nullable=False)
    field = Column(String(100), nullable=False)
    reason = Column(String(500), nullable=False)
    score = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    invoice = relationship("Invoice", back_populates="anomalies")

    def __repr__(self):
        return f"<Anomaly(id={self.id}, invoice_id={self.invoice_id}, field='{self.field}')>"
