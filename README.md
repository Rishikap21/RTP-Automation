# RTP Automation

## Overview

RTP Automation is an intelligent document processing system that automates the extraction of structured data from PDF documents, scanned PDFs, images, and Excel files. The system generates clean Excel reports by combining traditional document processing techniques with AI-powered vision models.

The project follows a hybrid extraction approach, using local extraction methods for text-based documents and AI only when required, reducing processing time and API usage.

---

# Features

- Upload PDF documents
- Upload scanned PDF documents
- Upload images (.png, .jpg, .jpeg)
- Upload Excel files (.xlsx, .xls)
- Automatic document type detection
- Hybrid table extraction
- AI-assisted extraction for scanned documents
- Metadata generation
- Automatic Excel report generation
- Download generated Excel reports

---

# Workflow

```
                User Uploads File
                       │
        ┌──────────────┼───────────────┐
        │              │               │
        ▼              ▼               ▼
      Excel          PDF            Image
        │              │               │
        ▼              ▼               ▼
 Direct Read   pdfplumber +        Gemini Vision
               Camelot Extract
                     │
          Data Extracted Successfully?
               │                │
              Yes              No
               │                │
               ▼                ▼
        Local Extraction    Gemini Vision
               │                │
               └──────┬─────────┘
                      ▼
             Merge Extracted Data
                      ▼
            Clean & Normalize Data
                      ▼
              Generate Excel
```

---

# Technologies Used

## Backend

- FastAPI
- Python

## Document Processing

- pdfplumber
- Camelot
- pdf2image

## AI Processing

- Google Gemini Vision API (google-genai)

## Data Processing

- Pandas
- NumPy

## Excel Generation

- OpenPyXL

---

# Project Structure

```
RTP-Automation/
│
├── generated/
├── uploads/
│
├── processing/
│   ├── dataframe_builder.py
│   ├── document_understanding.py
│   ├── excel_generator.py
│   ├── excel_processor.py
│   ├── gemini_extractor.py
│   ├── metadata_extractor.py
│   ├── pdf_processor.py
│   └── table_extractor.py
│
├── static/
├── templates/
│
├── main.py
├── requirements.txt
├── README.md
└── .gitignore
```

---

# Installation

## Clone the repository

```bash
git clone <repository-url>
cd RTP-Automation
```

## Create Virtual Environment

Windows

```bash
python -m venv venv
```

Activate

```bash
venv\Scripts\activate
```

---

## Install Dependencies

```bash
pip install -r requirements.txt
```

---

# Configure Gemini API

Set your Gemini API key before running the project.

Windows PowerShell

```powershell
$env:GEMINI_API_KEY="YOUR_API_KEY"
```

or create a User Environment Variable named

```
GEMINI_API_KEY
```

---

# Run the Application

```bash
python main.py
```

or

```bash
uvicorn main:app --reload
```

---

# API Endpoints

## Upload Document

```
POST /api/upload
```

Supported Formats

- PDF
- Excel (.xlsx, .xls)
- PNG
- JPG
- JPEG

---

## Convert to Excel

```
POST /api/excel/convert
```

---

## Download Report

```
GET /api/reports/download/{report_id}
```

---

## Chatbot

```
POST /api/chatbot
```

---

# Processing Pipeline

### Excel Files

- Read workbook directly
- Convert sheets into DataFrames
- Generate Excel report

---

### Text-Based PDFs

- Extract tables using Camelot
- Use pdfplumber for pages where Camelot cannot detect tables
- Merge extracted tables

---

### Scanned PDFs

- Detect pages without extractable tables
- Convert those pages into images
- Send only those pages to Gemini Vision
- Merge AI results with local extraction

---

### Images

- Directly processed using Gemini Vision
- Convert extracted tables into DataFrames
- Generate Excel report

---

# Current Capabilities

- Hybrid PDF table extraction
- AI fallback for scanned documents
- Image table extraction
- Automatic metadata generation
- Excel report generation
- Downloadable reports
- REST API using FastAPI

---

# Future Enhancements

- Batch document processing
- User authentication
- Database integration
- AI-powered document chatbot
- Semantic document search
- Dashboard analytics
- Cloud storage support

---

# Author

**Rishika P**

B.Tech Computer Science Engineering

NMAM Institute of Technology
