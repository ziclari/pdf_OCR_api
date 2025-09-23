from fastapi import FastAPI
from upload import router as upload_router
from process import router as process_router
from predict import router as predict_router
from clean import router as clean_router

app = FastAPI()

# incluir routers
app.include_router(upload_router)
app.include_router(process_router)
app.include_router(predict_router)
app.include_router(clean_router)
