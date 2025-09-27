from fastapi import APIRouter
from fastapi.responses import JSONResponse
import re
import os
import requests
from dotenv import load_dotenv
from pydantic import BaseModel
from google import genai
import json

load_dotenv()

router = APIRouter()

api_key_value =os.getenv("GOOGLE_API_KEY")

class LimpiarRequest(BaseModel):
    string_result: list[str]

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

@router.post("/limpiar/")
def limpiar(data: LimpiarRequest):
    results = []
    """
    # leer el prompt base desde archivo
    with open("prompt.txt", "r", encoding="utf-8") as f:
        base_prompt = f.read()

    if not data.string_result:
        return JSONResponse(status_code=400, content={"message": "No se recibieron textos para limpiar"})
    
    if not base_prompt:
        return JSONResponse(status_code=400, content={"message": "No hay prompt base en prompt.txt"})

    if not api_key_value:
        return JSONResponse(status_code=400, content={"message": "La variable de entorno GOOGLE_API_KEY no está configurada o está vacía."})

    client = genai.Client(api_key=api_key_value)

    for raw_text in data.string_result:
        try:
            cleaned = discard_after_headers(raw_text)
            if not cleaned:
                results.append([])
                continue

            full_prompt = base_prompt.format(input_tokens=cleaned)
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=full_prompt
            )
            ai_output = response.text.strip()

            # Limpieza y parseo seguro
            ai_clean = ai_output.replace("```json", "").replace("```", "").strip()
            parsed = json.loads(ai_clean)
            results.append(parsed if isinstance(parsed, list) else [])
        except Exception as e:
            print(f"Error limpiando texto: {e}")
            results.append([])  # fallback vacío
    print(results)
    """
    return JSONResponse(content={
        "message": "Datos limpiados y enviados a Gemini",
        "ai_result": results
    })
