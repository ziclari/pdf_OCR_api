from fastapi import APIRouter, UploadFile, File, HTTPException
import os
import uuid

router = APIRouter()

# === Configuración de directorios ===
UPLOAD_DIR = "uploads"

os.makedirs(UPLOAD_DIR, exist_ok=True)
# === Endpoint: subir PDF ===
@router.post("/upload_pdf/")
async def upload_pdf(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="El archivo debe ser PDF")

    unique_name = f"{uuid.uuid4()}.pdf"
    file_path = os.path.join(UPLOAD_DIR, unique_name)

    with open(file_path, "wb") as f:
        f.write(await file.read())

    return {"message": "PDF guardado correctamente", "pdf_url": file_path}