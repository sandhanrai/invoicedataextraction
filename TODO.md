# TODO List for AI-Based Multi-Language Invoice Data Extraction and Validation System

## Day 1: Project Initialization and Environment Setup

- [x] Create project directory structure (src/, data/, models/, notebooks/, tests/, config/, ui/)
- [x] Initialize Git repo
- [x] Create virtual environment
- [x] Install system dependencies (Tesseract OCR for English and Hindi)
- [x] Install Python dependencies from requirements.txt
- [x] Create .gitignore, README.md, src/**init**.py
- [x] Verify installations (check tesseract --version, pip list)

## Day 2: Dataset Collection and Research

- [ ] Collect sample invoices (3-5 files: PDF, JPG, PNG in English/Hindi)
- [ ] Define JSON schema for extracted data
- [ ] Research LayoutLMv3 usage (notebook with basic model load)

## Day 3: OCR Pipeline Development

- [ ] Implement OCR script using Tesseract and EasyOCR
- [ ] Create testing notebook for OCR accuracy comparison
- [ ] Run OCR on sample invoices and save text outputs

## Day 4: Basic Extraction and Validation Setup

- [ ] Implement regex rules for key fields
- [ ] Create extraction and validation functions
- [ ] Test extraction on OCR text

## Day 5: UI Prototype and Integration

- [ ] Build minimal Streamlit app for upload and display
- [ ] Integrate OCR/extraction into UI
- [ ] Create unit tests for OCR functionality
- [ ] Run tests and verify UI functionality
