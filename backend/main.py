import os
import sys
import shutil
from datetime import datetime

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse

# --------------------------------------------------
# Add project root to Python path
# --------------------------------------------------
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# --------------------------------------------------
# Imports
# --------------------------------------------------
from processing.document_understanding import understand_document
from processing.excel_generator import create_excel

from processing.chatbot import ask_chatbot
from processing.pdf_processor import extract_text,extract_tables

app = FastAPI(
    title="RTP Automation API",
    version="3.0"
)

UPLOAD_FOLDER = os.path.join(PROJECT_ROOT, "uploads")
GENERATED_FOLDER = os.path.join(PROJECT_ROOT, "generated")

document_text = ""

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(GENERATED_FOLDER, exist_ok=True)


@app.get("/")
def home():
    return {
        "message": "RTP Automation Backend Running",
        "supported_files": [
            "PDF",
            "Excel",
            "PNG",
            "JPG",
            "JPEG"
        ]
    }


@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    global document_text
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)

    file_path = os.path.join(
        UPLOAD_FOLDER,
        file.filename
    )

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    extension = os.path.splitext(file.filename)[1].lower()

    supported = [
        ".pdf",
        ".xlsx",
        ".xls",
        ".png",
        ".jpg",
        ".jpeg"
    ]

    # PDF Processing
    if extension == ".pdf":

        extracted_text = extract_text(file_path)
        document_text = extracted_text  

        if extracted_text is None:
            return {
                "error": "Invalid or corrupted PDF."
            }

        tables = extract_tables(file_path)

        excel_path = os.path.join(
            GENERATED_FOLDER,
            file.filename.replace(".pdf", ".xlsx"))
    if extension not in supported:
        raise HTTPException(
            status_code=400,
            detail="Unsupported file type."
        )

    try:

        document = understand_document(
            file_path,
            extension
        )

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        report_name = f"Generated_Report_{timestamp}.xlsx"

        report_path = os.path.join(
            GENERATED_FOLDER,
            report_name
        )

        create_excel(
            [
                {
                    "filename": file.filename,
                    "metadata": document["metadata"],
                    "sheet_names": document["sheet_names"],
                    "dataframes": document["dataframes"]
                }
            ],
            report_path
        )

        return {
            "status": "success",
            "filename": file.filename,
            "file_type": extension.replace(".", "").upper(),
            "tables_found": len(document["dataframes"]),
            "generated_report": report_name,
            "download_url": f"/download-report/{report_name}",
            "metadata": document["metadata"]
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
    )

@app.post("/chat")
async def chat(request: dict):
    question = request.get("question")

    if not question:
        return {"error": "Question is required"}

    answer = ask_chatbot(question,document_text)

    return {
        "question": question,
        "answer": answer
    }
    


@app.get("/download-report/{report_name}")
def download_report(report_name: str):

    report_path = os.path.join(
        GENERATED_FOLDER,
        report_name
    )

    if not os.path.exists(report_path):

        raise HTTPException(
            status_code=404,
            detail="Report not found."
        )

    return FileResponse(
        report_path,
        filename=report_name,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
