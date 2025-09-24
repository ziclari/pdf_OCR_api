from fastapi import APIRouter
from fastapi.responses import JSONResponse
import requests
import re
import os
import requests
from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv()

router = APIRouter()

LLAMA_API_KEY = os.getenv("LLAMA_API_KEY")
LLAMA_API_URL = os.getenv("LLAMA_API_URL")

class LimpiarRequest(BaseModel):
    string_result: str

# === Función para limpiar cabeceras ===
def discard_after_headers(text: str) -> str:
    lines = text.splitlines()
    found_headers = False

    for i, line in enumerate(lines):
        cleaned_line = line.strip()

        # Línea que parece cabecera (no empieza en número ni es solo número con puntos)
        if cleaned_line and not re.match(r'^\d', cleaned_line) and not cleaned_line.replace('.', '').isdigit():
            found_headers = True
            continue

        # Una vez detectadas cabeceras, cortar al primer número
        if found_headers and re.match(r'^\s*\d+', line):
            return "\n".join(lines[i:])

    return ""


# === Endpoint: limpiar y enviar a webhook ===
@router.post("/limpiar/")
def limpiar(data: LimpiarRequest):
    try:
        string_result = data.string_result
        # limpiar texto OCR
        cleaned = discard_after_headers(string_result)

        if not cleaned:
            return JSONResponse(status_code=400, content={"message": "No se pudo limpiar el texto"})

        # leer el prompt base desde archivo
        with open("prompt.txt", "r", encoding="utf-8") as f:
            base_prompt = f.read()

        # armar el mensaje para la AI
        payload = {
            "model": "llama3.1:latest",  # o el que tengas cargado
            "messages": [
                {"role": "system", "content": base_prompt},
                {"role": "user", "content": cleaned},
            ],
            "stream": False,
            "format": {
                "type": "array",
                "items": {
                    "type": "array",
                    "items": [
                        {"type": "string"},
                        {"type": "string"},
                        {"type": "string"},
                        {"type": "string"}
                    ]
                }
            },
            "options": {
                "temperature": 0,
                "top_p": 0.005,
            }
        }


        headers = {"Authorization": f"Bearer {LLAMA_API_KEY}"}

        response = requests.post(LLAMA_API_URL, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()
        print(data)
        ai_output = data["message"]["content"]

        return JSONResponse(content={
            "message": "Datos limpiados y enviados a Llama",
            "ai_result": ai_output
        })

    except Exception as e:
        return JSONResponse(status_code=500, content={"message": "Error en limpiar", "error": str(e)})
