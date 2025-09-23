from fastapi import APIRouter
from fastapi.responses import JSONResponse
from doctr.io import DocumentFile
from doctr.models import ocr_predictor
from doctr.utils.visualization import visualize_page
import matplotlib.pyplot as plt
import os
import uuid

router = APIRouter()

RESULT_DIR = "result"
PREDICT_DIR = "predicciones"
os.makedirs(PREDICT_DIR, exist_ok=True)

# === Endpoint: predecir con OCR ===
@router.post("/predecir/")
def predecir():
    try:
        archivos = [os.path.join(RESULT_DIR, f) for f in os.listdir(RESULT_DIR) if os.path.isfile(os.path.join(RESULT_DIR, f))]

        if not archivos:
            return JSONResponse(status_code=404, content={"message": "No hay imágenes para procesar en result/"})

        # cargar imágenes como documento
        doc = DocumentFile.from_images(archivos)

        # modelo OCR
        predictor = ocr_predictor(pretrained=True)
        result = predictor(doc)

        # generar visualización
        pred_images = []
        for i, page in enumerate(result.pages):
            fig = plt.figure(figsize=(10, 10))
            visualize_page(page, doc[0], interactive=False)
            save_path = os.path.join(PREDICT_DIR, f"pred_{uuid.uuid4()}.png")
            plt.savefig(save_path)
            plt.close(fig)
            pred_images.append(save_path)

        return JSONResponse(content={
            "message": "OCR completado",
            "predicciones": pred_images
        })

    except Exception as e:
        return JSONResponse(status_code=500, content={"message": "Error en la predicción", "error": str(e)})
