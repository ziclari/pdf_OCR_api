from fastapi import FastAPI
from upload import router as upload_router
from process import router as process_router
from predict import router as predict_router
from clean import router as clean_router
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

app = FastAPI()

origins = [
    "http://localhost:8080",  # tu frontend en dev
    "http://127.0.0.1:8080",
    # puedes poner "*" en desarrollo para permitir todo
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.mount("/debug", StaticFiles(directory="debug"), name="debug")
app.mount("/predicciones", StaticFiles(directory="predicciones"), name="predicciones")
app.mount("/result", StaticFiles(directory="result"), name="result")
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# incluir routers
app.include_router(upload_router)
app.include_router(process_router)
app.include_router(predict_router)
app.include_router(clean_router)
