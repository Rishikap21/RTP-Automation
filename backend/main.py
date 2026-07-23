from fastapi import FastAPI, UploadFile, File
import os
import shutil

from processing.pdf_processor import extract_text, extract_tables
from processing.excel_generator import create_excel
from processing.ocr_processor import extract_text_from_image

from processing.chatbot import ask_chatbot

app = FastAPI(
    title="RTP Automation API",
    version="1.0"
)

UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "output"

document_text = ""

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)


@app.get("/")
def home():
    return {
        "message": "RTP Automation Backend is Running"
    }


@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    global document_text
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    extension = os.path.splitext(file.filename)[1].lower()

    extracted_text = ""
    tables = []

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
            OUTPUT_FOLDER,
            file.filename.replace(".pdf", ".xlsx")
        )

        create_excel(tables, excel_path)

    # Image OCR
    elif extension in [".png", ".jpg", ".jpeg"]:

        extracted_text = extract_text_from_image(file_path)

        excel_path = None

    else:

        return {
            "error": "Unsupported file type."
        }

    return {
        "message": "File processed successfully",
        "filename": file.filename,
        "excel_file": excel_path,
        "text": extracted_text,
        "tables": tables
    }

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