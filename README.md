# RTP Automation

## Overview

RTP Automation is an intelligent document processing system that automates the extraction of structured data from PDF documents, scanned PDFs, images, and Excel files. The system generates clean Excel reports by combining traditional document processing techniques with AI-powered vision models.

The project follows a hybrid extraction approach, using local extraction methods for text-based documents and AI only when required, reducing processing time and API usage.

---

## Admin Authentication Credentials

To access the restricted Mission Control Administrative Dashboard, use the following credentials:

- **Admin Email**: `admin@gmail.com`
- **Admin Password**: `RTP#Admin2026!Secured`

---

## Frontend & API Generation Structure

The application features a modern Single-Page Application (SPA) dashboard connected to a FastAPI backend gateway (`main.py` & `backend/api_main.py`).

### 1. Frontend Architecture (`templates/` & `static/`)
- **`templates/index.html`**: Premium HTML5 Dashboard with modern typography, glassmorphism UI, side navigation, upload pipeline dropzone, data extraction table preview, Excel report manager, AI chatbot interface, settings panel, and real-time audit log viewer.
- **`static/main.js`**: Application logic handling authentication state, async REST API calls via `APIClient`, file upload pipeline, table rendering, live progress tracking, chatbot streaming, and settings management.
- **`static/style.css`**: Styling rules, responsive container layouts, custom scrollbars, animations, and micro-interactions.

### 2. API Generation & Core Endpoints
- **Authentication Gateway**: `POST /api/login` - Authenticates admin operators and issues session credentials.
- **Document Pipeline Upload**: `POST /api/upload` - Receives PDF, Excel, or Image files into `uploads/`, triggers hybrid OCR/AI extraction, and queues records.
- **Pipeline Queue Management**: `GET /api/queue` & `POST /api/queue/process` - Fetches queue progress and initiates automated batch table extraction.
- **Extracted Data Viewer**: `GET /api/extraction/{file_id}` - Returns parsed structured rows, columns, and flagged confidence values.
- **Excel Spreadsheet Generator**: `POST /api/excel/convert` - Converts extracted JSON dataframes into styled `.xlsx` reports stored in `generated/`.
- **Report Manager & Download**: `GET /api/reports` & `GET /api/reports/download/{report_id}` - Lists and downloads generated Excel workbooks.
- **RAG AI Chatbot**: `POST /api/chatbot` - Contextual vector-store search and Gemini LLM question-answering over uploaded document text.
- **Admin Settings & Security**: `GET/POST /api/settings/operators`, `GET/PUT /api/settings/permissions`, `POST /api/settings/rotate-key` - Operator user management, module access toggles, and API security key rotation.
- **Audit Logging**: `GET /api/logs` - System action log trail for operational monitoring.

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
├── backend/
│   ├── __init__.py
│   └── api_main.py
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
│   ├── main.js
│   └── style.css
│
├── templates/
│   └── index.html
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

# AI Chatbot Module

The RTP Automation project includes an AI-powered chatbot that enables users to interact with uploaded documents using natural language. Instead of manually searching through extracted tables, users can ask questions related to the uploaded document and receive context-aware responses.

The chatbot combines semantic search with Google's Gemini Large Language Model to retrieve relevant information and generate accurate answers.

---

# Chatbot Features

- Natural language question answering
- Context-aware document search
- Semantic similarity retrieval
- Google Gemini LLM integration
- Vector embedding generation
- FAISS vector database
- Automatic document indexing after upload
- Retrieval-Augmented Generation (RAG) based responses

---

# Chatbot Workflow

             User Uploads Document
                     │
                     ▼
         Document Text Extraction
                     │
                     ▼
      Convert DataFrames to Plain Text
                     │
                     ▼
      Split Text into Smaller Chunks
                     │
                     ▼
 Generate Gemini Embeddings for Chunks
                     │
                     ▼
 Store Embeddings in FAISS Vector Store
                     │
                     ▼
          User Asks a Question
                     │
                     ▼
     Similarity Search (Top Relevant Chunks)
                     │
                     ▼
      Send Context + Question to Gemini
                     │
                     ▼
         AI Generates Final Answer
                     │
                     ▼
         Response Displayed to User

---

# Chatbot Architecture

### Document Processing

After a document is uploaded and processed, all extracted tables are converted into plain text. The extracted content is then prepared for semantic indexing.

### Text Chunking

The document text is divided into smaller overlapping chunks using LangChain's Recursive Character Text Splitter. Chunking improves retrieval accuracy by allowing the chatbot to search only the most relevant portions of the document instead of the entire content.

### Embedding Generation

Each text chunk is converted into high-dimensional vector embeddings using Google's Gemini Embedding Model (gemini-embedding-001). These embeddings capture the semantic meaning of the document rather than relying on keyword matching.

### Vector Database

The generated embeddings are stored in a FAISS Vector Store, enabling fast similarity searches across the uploaded document. This allows efficient retrieval even for large documents.

### Semantic Search

Whenever the user submits a question, the chatbot converts the query into an embedding and performs a similarity search in the FAISS vector database. The top relevant document chunks are selected as contextual information.

### AI Response Generation

The retrieved document context and the user's question are sent to Google Gemini 3.5 Flash, which generates a context-aware answer based only on the retrieved information from the uploaded document.

---

# Technologies Used

### Backend

- FastAPI
- Python

### AI Framework

- LangChain

### Embedding Model

- Gemini Embedding-001

### Vector Database

- FAISS

### Large Language Model

- Google Gemini 3.5 Flash

---

# Chatbot Project Structure

processing/
│
├── chatbot.py                # Handles question answering using Gemini
├── vector_store.py           # Creates embeddings and FAISS vector database
├── document_understanding.py # Supplies extracted document text
│
main.py                       # Chatbot API endpoint
requirements.txt              # Chatbot dependencies

---

# Chatbot API Endpoint

### Ask Question

- POST /api/chatbot

### Request Body

{
    "message": "What is the total quantity mentioned in the document?",
    "context_files": []
}

### Response

{
    "answer": "The total quantity mentioned in the uploaded document is 250 units."
}

---

# Chatbot Processing Flow

### Document Upload

- Upload document
- Extract structured data
- Convert extracted data into text

### Vector Indexing

- Split document into chunks
- Generate Gemini embeddings
- Store embeddings in FAISS

### Question Answering

- Receive user query
- Perform semantic similarity search
- Retrieve relevant document chunks
- Send context and question to Gemini
- Generate AI response

---

# Current Capabilities

- Semantic document search
- Context-aware question answering
- Gemini-powered AI responses
- FAISS vector indexing
- Automatic document embedding generation
- Fast retrieval of relevant information

---

# Future Enhancements

- Multi-document chatbot
- Conversation history
- Source citation for answers
- Streaming AI responses
- Persistent vector database
- Support for multilingual queries

---


# Authors

**Ashitha**

**Rishika P**

**Bhoomika V**

B.Tech Computer Science Engineering

NMAM Institute of Technology
