from fastapi import FastAPI
from .api import variants

app = FastAPI(title="Cardio Classifier API", version="0.1.0")

app.include_router(variants.router, prefix="/variants", tags=["variants"])

@app.get("/health")
async def health():
    return {"status": "ok"}
