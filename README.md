# RTP Automation - Backend

## Project Overview

RTP Automation is a backend system developed to automate the extraction of tabular data from uploaded documents and generate structured Excel reports.

The backend supports PDF, Excel, and image uploads. It processes the uploaded document, extracts tabular information, generates metadata, and creates a downloadable Excel report.

---

## Features

- Upload PDF documents
- Upload Excel files
- Upload image screenshots
- Extract tables from PDF documents
- Read multiple sheets from Excel files
- OCR-based text extraction from images
- Generate Excel reports
- Download generated Excel files
- Automatic metadata generation

---

## Technologies Used

### Backend
- FastAPI
- Python

### Document Processing
- pdfplumber
- Camelot
- EasyOCR
- OpenCV

### Data Processing
- Pandas
- NumPy

### Excel Generation
- OpenPyXL

---

## Project Structure

backend/
│
├── generated/
├── uploads/
├── processing/
│   ├── dataframe_builder.py
│   ├── document_understanding.py
│   ├── excel_generator.py
│   ├── excel_processor.py
│   ├── metadata_extractor.py
│   ├── ocr_processor.py
│   ├── pdf_processor.py
│   └── table_extractor.py
│
├── main.py
├── requirements.txt
└── README.md

---

## Installation

Clone the repository.

Install all dependencies:

pip install -r requirements.txt

---

## Running the Project

Start the FastAPI server:

uvicorn main:app --reload

Open Swagger UI:

http://127.0.0.1:8000/docs

---

## API Endpoints

### Upload Document

POST /upload

Supported formats:

- PDF
- Excel (.xlsx, .xls)
- Images (.png, .jpg, .jpeg)

Returns:

- Processing status
- Generated report name
- Download URL

---

### Download Report

GET /download-report/{report_name}

Downloads the generated Excel report.

---

## Workflow

Upload Document

↓

Document Processing

↓

Table Extraction

↓

Metadata Generation

↓

Excel Generation

↓

Download Report

---

## Current Capabilities

✅ PDF table extraction

✅ Excel sheet extraction

✅ OCR-based image text extraction

✅ Metadata generation

✅ Excel report generation

✅ Download generated reports

---

## Future Enhancements

- Image table reconstruction
- AI-powered chatbot integration
- Batch document processing
- Cloud storage integration
- User authentication
- Dashboard and analytics

---

## Author

Rishika P