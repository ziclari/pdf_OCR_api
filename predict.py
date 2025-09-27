from fastapi import APIRouter
from fastapi.responses import JSONResponse
from doctr.io import DocumentFile
from doctr.models import ocr_predictor
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import cv2
import os
import uuid
from pydantic import BaseModel
from typing import List

router = APIRouter()

RESULT_DIR = "result"
PREDICT_DIR = "predicciones"
os.makedirs(PREDICT_DIR, exist_ok=True)

class PredictRequest(BaseModel):
    tables: List[str]

def draw_overlay(image_path: str, page, save_dir: str) -> str:
    """
    Dibuja un overlay con bounding boxes sobre la imagen original.

    Args:
        image_path (str): Ruta de la imagen original.
        page (doctr.models.Page): Página OCR con bloques, líneas y palabras.
        save_dir (str): Directorio donde guardar el resultado.

    Returns:
        str: Ruta del archivo generado.
    """
    # cargar imagen con OpenCV en RGB
    image = cv2.imread(image_path)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    h, w, _ = image.shape

    fig, ax = plt.subplots(figsize=(12, 16))
    ax.imshow(image)
    ax.axis("off")

    # recorrer las palabras detectadas
    for block in page.blocks:
        for line in block.lines:
            for word in line.words:
                (xmin, ymin), (xmax, ymax) = word.geometry
                x0, y0 = xmin * w, ymin * h
                width, height = (xmax - xmin) * w, (ymax - ymin) * h

                rect = patches.Rectangle(
                    (x0, y0), width, height,
                    linewidth=0, facecolor="blue", alpha=0.3
                )
                ax.add_patch(rect)

    # guardar resultado
    os.makedirs(save_dir, exist_ok=True)
    save_path = os.path.join(save_dir, f"overlay_{uuid.uuid4()}.png")
    plt.savefig(save_path, dpi=300, bbox_inches="tight")
    plt.close(fig)

    return save_path

# === Endpoint: predecir con OCR ===
@router.post("/predecir/")
def predecir(request: PredictRequest):
    try:
        archivos = request.tables

        if not archivos:
            return JSONResponse(status_code=404, content={"message": "No hay imágenes para procesar en result/"})

        # cargar imágenes como documento
        doc = DocumentFile.from_images(archivos)

        # modelo OCR
        predictor = ocr_predictor(pretrained=True)
        result = predictor(doc)

        # generar visualización
        predicciones = []
        for i, (page, img_path) in enumerate(zip(result.pages, archivos)):
            save_path = draw_overlay(img_path, page, PREDICT_DIR)
            predicciones.append({
                "imagen": img_path,
                "overlay": save_path,
                "texto": page.render()
            })
        print(predicciones)
        return JSONResponse(content={
            "message": "OCR completado",
            "predicciones": predicciones
        })

    except Exception as e:
        return JSONResponse(status_code=500, content={"message": "Error en la predicción", "error": str(e)})
