import os
import uuid
import time
import random
from typing import List, Optional
from datetime import datetime
from fastapi import FastAPI, Request, Form, File, UploadFile, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from processing.document_understanding import understand_document
from processing.excel_generator import create_excel

app = FastAPI(title="RTP Automation AI API Gateway", version="4.2.0")

# Setup CORS for development flexibility
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Workspace Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")

# Mount Static assets
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Templates Config
templates = Jinja2Templates(directory=TEMPLATES_DIR)

# Real file storage
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
GENERATED_DIR = os.path.join(BASE_DIR, "generated")
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(GENERATED_DIR, exist_ok=True)

# Holds the REAL extraction results (metadata + dataframes + sheet_names)
# keyed by file_id, produced by processing/document_understanding.py
documents_store = {}

# ==================== IN-MEMORY MOCK STATEFUL DATABASES ====================

# Default Operators list
operators_db = [
    {"name": "John Doe", "email": "john.d@rtp-refinery.ai", "role": "Admin", "status": "Active", "last_login": "2 mins ago"},
    {"name": "Sarah Miller", "email": "s.miller@rtp-refinery.ai", "role": "Analyst", "status": "Active", "last_login": "4 hours ago"},
    {"name": "Robert Tiller", "email": "tiller.r@rtp-refinery.ai", "role": "Operator", "status": "Offline", "last_login": "2 days ago"}
]

# Active Modules Permissions
permissions_db = [
    {"id": "chatbot", "name": "Refinery Chatbot AI", "description": "Allow operators to query refinery manuals via LLM.", "enabled": True},
    {"id": "extraction", "name": "Data Auto-Extraction", "description": "High-precision parsing of legacy valve data logs.", "enabled": True},
    {"id": "excel", "name": "Excel Manager Core", "description": "Read/Write operations for plant performance spreadsheets.", "enabled": False}
]

# Security Gateway Configurations
gateway_db = {
    "api_key": "rtp_live_839a8c2f10b2401da05c87de9821a9A4",
    "last_rotation": "Sept 12, 2024"
}

# Audit Logs Trail
audit_logs_db = [
    {
        "id": "log_1",
        "type": "info",
        "title": "System Configuration Updated",
        "timestamp": "12:44 PM",
        "details": "Operator John Doe modified Chatbot API thresholds to 0.85.",
        "ip": "192.168.1.104"
    },
    {
        "id": "log_2",
        "type": "alert",
        "title": "Unusual Login Attempt",
        "timestamp": "11:02 AM",
        "details": "Failed login attempt from unauthorized location (Strasbourg, FR). Access denied.",
        "ip": "82.120.44.19"
    },
    {
        "id": "log_3",
        "type": "download",
        "title": "Bulk Data Export",
        "timestamp": "09:15 AM",
        "details": "Sarah Miller exported Valve_Performance_Q3.xlsx to Local Secure Vault.",
        "ip": "192.168.1.112"
    }
]

# Processing Queue Pipeline
# Populate with a default file to show on initial load
queue_db = [
    {
        "id": "doc_1",
        "name": "INV-2026-0082-Refinery.pdf",
        "size": 2516582,
        "progress": 100,
        "status": "Completed",
        "tables_found": 2,
        "operator": "John Doe",
        "extracted_rows": [
            {"ref_id": "VALVE-772-A", "description": "Pressure Relief Valve, 4-inch Titanium", "quantity": 12, "unit_price": 1420.00, "total": 17040.00, "status": "Verified"},
            {"ref_id": "PUMP-001-B", "description": "Centrifugal Fluid Pump - Grade C", "quantity": 2, "unit_price": 8900.00, "total": 17800.00, "status": "Verified"},
            {"ref_id": "SPEC-UNK-01", "description": "OCR Ambiguity: O-Ring Seal...", "quantity": 150, "unit_price": 4.20, "total": 630.00, "status": "Flagged"},
            {"ref_id": "SHIP-FEES", "description": "International Freight - Maritime", "quantity": 1, "unit_price": 2450.00, "total": 2450.00, "status": "Verified"}
        ]
    }
]

# Generated Excel spreadsheets in Excel Output Manager
reports_db = [
    {
        "id": "rep_1",
        "name": "Extraction_Report_2026_01.xlsx",
        "source_file": "INV-2026-0082-Refinery.pdf",
        "created_at": "Oct 24, 2026 14:20",
        "size": 2516582
    }
]

# ==================== DATA SCHEMAS ====================

class LoginRequest(BaseModel):
    email: str
    key: str

class OperatorRequest(BaseModel):
    name: str
    email: str
    role: str

class PermissionUpdateRequest(BaseModel):
    module_id: str
    enabled: bool

class ChatMessageRequest(BaseModel):
    message: str
    context_files: List[str]

class ConvertRequest(BaseModel):
    file_id: str

# ==================== HTML TEMPLATE ROUTE ====================

@app.get("/", response_class=HTMLResponse)
async def get_index(request: Request):
    return templates.TemplateResponse(request=request,name="index.html")

# ==================== API ENDPOINTS ====================

# 1. Login Authentication
@app.post("/api/login")
async def post_login(req: LoginRequest):
    # Simplified authentication check
    if not req.email or not req.key:
        raise HTTPException(status_code=400, detail="Missing credentials")
    
    # Mock JWT token generation
    session_token = f"jwt_{uuid.uuid4().hex}"
    
    # Check if matching operator or create temporary operator
    operator = next((op for op in operators_db if op["email"] == req.email), None)
    if not operator:
        operator = {
            "name": req.email.split('@')[0].capitalize(),
            "email": req.email,
            "role": "Operator",
            "status": "Active",
            "last_login": "Just now"
        }
        operators_db.append(operator)
    else:
        operator["status"] = "Active"
        operator["last_login"] = "Just now"
        
    # Append log entry
    audit_logs_db.insert(0, {
        "id": f"log_{uuid.uuid4().hex[:6]}",
        "type": "info",
        "title": "Operator Session Opened",
        "timestamp": datetime.now().strftime("%I:%M %p"),
        "details": f"Operator {operator['name']} successfully signed in through gateway portal.",
        "ip": "127.0.0.1"
    })
    
    return {"token": session_token, "operator": operator}

# 2. Upload Document File to Pipeline Queue
@app.post("/api/upload")
async def upload_document(file: UploadFile = File(...)):
    file_id = f"doc_{uuid.uuid4().hex[:6]}"

    extension = os.path.splitext(file.filename)[1]
    saved_path = os.path.join(UPLOAD_DIR, f"{file_id}{extension}")

    contents = await file.read()
    with open(saved_path, "wb") as f:
        f.write(contents)

    # Run the REAL extraction pipeline (pdf/excel/ocr -> dataframes -> metadata)
    try:
        result = understand_document(saved_path, extension)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Extraction failed: {e}")

    documents_store[file_id] = {
        "filename": file.filename,
        "file_path": saved_path,
        "metadata": result["metadata"],
        "dataframes": result["dataframes"],
        "sheet_names": result["sheet_names"],
    }

    new_doc = {
        "id": file_id,
        "name": file.filename,
        "size": len(contents),
        "progress": 100,
        "status": "Completed",
        "tables_found": len(result["dataframes"]),
        "operator": "operator",
    }

    queue_db.append(new_doc)
    
    audit_logs_db.insert(0, {
        "id": f"log_{uuid.uuid4().hex[:6]}",
        "type": "info",
        "title": "Pipeline Upload Initiated",
        "timestamp": datetime.now().strftime("%I:%M %p"),
        "details": f"Operator uploaded new source record: {file.filename}",
        "ip": "127.0.0.1"
    })
    
    return {"status": "success", "file_id": file_id, "tables_found": len(result["dataframes"])}

# 3. Get Pipeline Queue
@app.get("/api/queue")
async def get_queue():
    # Simulate extraction progress increase for processing items
    for item in queue_db:
        if item["status"] == "Scanning":
            item["progress"] += 20
            if item["progress"] >= 40:
                item["status"] = "Extracting"
        elif item["status"] == "Extracting":
            item["progress"] += 25
            if item["progress"] >= 100:
                item["progress"] = 100
                item["status"] = "Completed"
                item["tables_found"] = random.randint(1, 4)
                
    return queue_db

# 4. Trigger processing pipeline
@app.post("/api/queue/process")
async def post_process():
    for item in queue_db:
        if item["status"] == "Queued":
            item["status"] = "Scanning"
            item["progress"] = 10
            
    audit_logs_db.insert(0, {
        "id": f"log_{uuid.uuid4().hex[:6]}",
        "type": "info",
        "title": "Queue Pipeline Processing started",
        "timestamp": datetime.now().strftime("%I:%M %p"),
        "details": "AI pipeline batch execution command sent to background threads.",
        "ip": "127.0.0.1"
    })
    return {"status": "processing"}

# 5. Get Extracted Data Table details
@app.get("/api/extraction/{file_id}")
async def get_extraction(file_id: str):
    doc = next((d for d in queue_db if d["id"] == file_id), None)
    if not doc:
        raise HTTPException(status_code=404, detail="Document details not found")
    return doc

# 6. Convert Table to Excel Spreadsheet
@app.post("/api/excel/convert")
async def post_convert(req: ConvertRequest):
    doc = documents_store.get(req.file_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    report_id = f"rep_{uuid.uuid4().hex[:6]}"
    report_name = f"{doc['filename'].rsplit('.', 1)[0]}_Report.xlsx"
    output_path = os.path.join(GENERATED_DIR, f"{report_id}.xlsx")

    # Build the REAL workbook from the extracted dataframes + metadata
    create_excel([doc], output_path)

    new_report = {
        "id": report_id,
        "name": report_name,
        "source_file": doc["filename"],
        "created_at": datetime.now().strftime("%b %d, %Y %H:%M"),
        "size": os.path.getsize(output_path),
        "file_path": output_path,
    }
    
    reports_db.append(new_report)
    
    audit_logs_db.insert(0, {
        "id": f"log_{uuid.uuid4().hex[:6]}",
        "type": "download",
        "title": "Excel Spreadsheet Created",
        "timestamp": datetime.now().strftime("%I:%M %p"),
        "details": f"Successfully mapped OCR data to generated Excel report: {report_name}",
        "ip": "127.0.0.1"
    })
    
    return {"status": "success", "report": new_report}

# 7. Get Excel spreadsheet reports list
@app.get("/api/reports")
async def get_reports():
    return reports_db

# 8. Download spreadsheet report (streams the real generated file)
@app.get("/api/reports/download/{report_id}")
async def get_download_report(report_id: str):
    report = next((r for r in reports_db if r["id"] == report_id), None)
    if not report:
        raise HTTPException(status_code=404, detail="Spreadsheet report file not found")

    file_path = report.get("file_path")
    if not file_path or not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Generated report file is missing on disk")

    return FileResponse(file_path, filename=report["name"], media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

# 9. AI Chatbot queries Contextual response
@app.post("/api/chatbot")
async def post_chatbot(req: ChatMessageRequest):
    msg = req.message.lower()
    
    # Match keyword response intents
    if "summarize" in msg or "summary" in msg:
        answer = "Based on the refinery files context, here is the summary:\n- Valves Q2 vs Q3 shows steady pressure levels.\n- 3 critical O-ring warnings detected in SPEC-UNK-01.\n- Data formats match ASME-B16 pressure regulations."
    elif "pressure" in msg or "abnormal" in msg:
        answer = "Telemetry check reports:\n- Valve-772-A: Optimal pressure of 1420 PSI.\n- Pump-001-B: Centrifugal flow speed within margin.\n- Ambiguity Flag: GAUGE-AMB value scanned as '00-R' instead of numeric PSI limits."
    elif "valve" in msg:
        answer = "Detected Valve Specifications:\n1. VALVE-772-A: 4-inch Titanium Pressure Relief Valve (Qty: 12, Unit: $1,420)\n2. VALVE-124-T: Direct Action Control Valve Q-type (Qty: 4, Unit: $750)"
    else:
        answer = "I've reviewed the knowledge contexts. The pipeline processing contains 1 active document queue. Security credentials rotated recently. Feel free to ask details about O-Ring specs, valves listing, or Excel sheets export status."
        
    return {"answer": answer}

# 10. Settings Operators list
@app.get("/api/settings/operators")
async def get_operators():
    return operators_db

# 11. Add operator
@app.post("/api/settings/operators")
async def post_operators(req: OperatorRequest):
    new_op = {
        "name": req.name,
        "email": req.email,
        "role": req.role,
        "status": "Offline",
        "last_login": "Never"
    }
    operators_db.append(new_op)
    
    audit_logs_db.insert(0, {
        "id": f"log_{uuid.uuid4().hex[:6]}",
        "type": "info",
        "title": "Operator Credentials Added",
        "timestamp": datetime.now().strftime("%I:%M %p"),
        "details": f"Registered new dashboard operator credentials: {req.name} ({req.role})",
        "ip": "127.0.0.1"
    })
    
    return new_op

# 12. Settings Module access permissions
@app.get("/api/settings/permissions")
async def get_permissions():
    return permissions_db

@app.put("/api/settings/permissions")
async def put_permissions(req: PermissionUpdateRequest):
    perm = next((p for p in permissions_db if p["id"] == req.module_id), None)
    if not perm:
        raise HTTPException(status_code=404, detail="Permission category not found")
    
    perm["enabled"] = req.enabled
    
    audit_logs_db.insert(0, {
        "id": f"log_{uuid.uuid4().hex[:6]}",
        "type": "info",
        "title": "Access Controls Updated",
        "timestamp": datetime.now().strftime("%I:%M %p"),
        "details": f"Changed availability status for module '{perm['name']}' to {req.enabled}",
        "ip": "127.0.0.1"
    })
    return perm

# 13. Rotate Security API Gateway Key
@app.post("/api/settings/rotate-key")
async def post_rotate_key():
    new_key = f"rtp_live_{uuid.uuid4().hex[:8]}f10b2{uuid.uuid4().hex[:8]}da05c87de9821a9A4"
    gateway_db["api_key"] = new_key
    gateway_db["last_rotation"] = datetime.now().strftime("%b %d, %Y")
    
    audit_logs_db.insert(0, {
        "id": f"log_{uuid.uuid4().hex[:6]}",
        "type": "info",
        "title": "Gateway Security Key Rotated",
        "timestamp": datetime.now().strftime("%I:%M %p"),
        "details": "Gateway key rotated for RSA credentials session compliance.",
        "ip": "127.0.0.1"
    })
    
    return {"status": "success", "new_key": new_key}

# 14. Activity Audit Logs
@app.get("/api/logs")
async def get_logs():
    return audit_logs_db

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)