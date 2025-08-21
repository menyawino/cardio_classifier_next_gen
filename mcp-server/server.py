from fastapi import FastAPI
from pydantic import BaseModel
import random

app = FastAPI(title="Cardio MCP Server", version="0.1.0")

class HGVSRequest(BaseModel):
    hgvs: str

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.post("/clinvar")
async def clinvar(req: HGVSRequest):
    # Simulated ClinVar record (random significance for test variability)
    sig = random.choice([None, "Pathogenic", "Likely pathogenic", "VUS", "Benign", None])
    return {"rcv": None, "clinical_significance": sig, "variation_id": None}

@app.post("/gnomad")
async def gnomad(req: HGVSRequest):
    # Simulated population frequency
    af = random.choice([0.00001, 0.0001, 0.001, 0.01])
    return {"allele_frequency": af}

@app.post("/predictions")
async def predictions(req: HGVSRequest):
    # Simulated in-silico tool consensus count deleterious
    deleterious = random.randint(0,5)
    return {"deleterious_tools": deleterious, "total_tools": 5}
