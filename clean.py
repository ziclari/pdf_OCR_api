from fastapi import APIRouter
from fastapi.responses import JSONResponse
import requests
import re

router = APIRouter()

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
def limpiar(string_result: str):
    try:
        # limpiar texto OCR
        cleaned = discard_after_headers(string_result)

        if not cleaned:
            return JSONResponse(status_code=400, content={"message": "No se pudo limpiar el texto"})

        # enviar al webhook n8n
        url = "https://tplrmklmqgfenjvwdtsnygiv.hooks.n8n.cloud/webhook-test/e8546515-9b65-49cb-9d90-c1498c9cf503" #este es de ejemplo
        response = requests.post(url, json={"mensaje": cleaned})

        return JSONResponse(content={
            "message": "Datos limpiados y enviados",
            "status_code": response.status_code,
            "respuesta": response.text
        })

    except Exception as e:
        return JSONResponse(status_code=500, content={"message": "Error en limpiar", "error": str(e)})
