from fastapi import APIRouter
from fastapi.responses import JSONResponse
import requests
import re
import os
import requests
from dotenv import load_dotenv
from pydantic import BaseModel
from google import genai

load_dotenv()

router = APIRouter()

api_key_value =os.getenv("GOOGLE_API_KEY")

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

        if not api_key_value:
            return JSONResponse(status_code=400, content={"message": "La variable de entorno GOOGLE_API_KEY no está configurada o está vacía."})

        # leer el prompt base desde archivo
        with open("prompt.txt", "r", encoding="utf-8") as f:
            base_prompt = f.read()

        try:
            client = genai.Client(api_key=api_key_value)
        except Exception as e:
            return JSONResponse(status_code=500, content={"message": "Error al inicializar el cliente", "error": str(e)})

        model_name = 'gemini-2.5-flash' 
        full_prompt = base_prompt.format(input_tokens=cleaned)
        response = client.models.generate_content(
            model=model_name,
            contents=full_prompt
        )

        ai_output = response.text
        print(ai_output)

        return JSONResponse(content={
            "message": "Datos limpiados y enviados a Llama",
            "ai_result": ai_output
        })

    except Exception as e:
        return JSONResponse(status_code=500, content={"message": "Error en limpiar", "error": str(e)})
