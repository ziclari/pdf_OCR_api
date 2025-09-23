from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pdf2image import convert_from_path
import cv2
import numpy as np
import os

router = APIRouter()

# === Configuración de directorios ===
DEBUG_DIR = "debug"
RESULT_DIR = "result"

os.makedirs(DEBUG_DIR, exist_ok=True)
os.makedirs(RESULT_DIR, exist_ok=True)


# === Función para detectar si un bloque es tipo tabla ===
def is_table_like(block_gray):
    _, bin_img = cv2.threshold(block_gray, 180, 255, cv2.THRESH_BINARY_INV)
    horiz_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (40, 1))
    vert_kernel  = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 40))
    horiz = cv2.morphologyEx(bin_img, cv2.MORPH_OPEN, horiz_kernel)
    vert  = cv2.morphologyEx(bin_img, cv2.MORPH_OPEN, vert_kernel)
    grid_like = cv2.add(horiz, vert)
    density = cv2.countNonZero(grid_like) / (block_gray.shape[0] * block_gray.shape[1])
    return density > 0.05

# === Endpoint: procesamiento del PDF ===
@router.post("/procesamiento/")
def procesamiento(pdf_url: str):
    try:
        if not os.path.exists(pdf_url):
            raise HTTPException(status_code=404, detail="Archivo no encontrado")

        pages = convert_from_path(pdf_url, dpi=300)
        debug_paths = []
        table_paths = []

        for i, page in enumerate(pages):
            img = np.array(page)
            gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
            _, thresh = cv2.threshold(gray, 180, 255, cv2.THRESH_BINARY_INV)
            edges = cv2.Canny(thresh, 50, 150)
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
            dilated = cv2.dilate(edges, kernel, iterations=2)
            contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            debug = img.copy()

            for j, cnt in enumerate(contours):
                x, y, w, h = cv2.boundingRect(cnt)
                if w < 300 or h < 200:
                    continue

                crop = gray[y:y+h, x:x+w]
                if is_table_like(crop):
                    table_path = os.path.join(RESULT_DIR, f"page{i+1}_table{j+1}.png")
                    cv2.imwrite(table_path, img[y:y+h, x:x+w])
                    table_paths.append(table_path)
                    color = (0, 255, 0)
                else:
                    color = (0, 0, 255)

                cv2.rectangle(debug, (x, y), (x+w, y+h), color, 3)

            debug_path = os.path.join(DEBUG_DIR, f"page{i+1}.png")
            cv2.imwrite(debug_path, cv2.cvtColor(debug, cv2.COLOR_RGB2BGR))
            debug_paths.append(debug_path)

        return JSONResponse(content={
            "message": "Procesamiento completado",
            "debug": debug_paths,
            "tables": table_paths
        })

    except Exception as e:
        return JSONResponse(status_code=500, content={"message": "Error en el procesamiento", "error": str(e)})
