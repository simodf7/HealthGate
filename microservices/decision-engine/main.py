from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict
import os
from dotenv import load_dotenv
load_dotenv()


# importa il modulo che contiene tutta la logica Gemini
from llm_module import create_client, extract_clinical_info  

app = FastAPI(title="LLM Service")

# Recupera la API key di Gemini dall'ambiente
API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise RuntimeError("Variabile GEMINI_API_KEY non trovata nelle variabili d'ambiente")

# Schema input per la richiesta
class ClinicalRequest(BaseModel):
    text: str

@app.get("/")
def health():
    """Health check"""
    return {"status": "LLM Service running"}

@app.post("/llm/extract", response_model=Dict)
async def extract(req: ClinicalRequest):
    """
    Endpoint che riceve un testo clinico e restituisce JSON strutturato
    dopo correzione, estrazione e validazione.
    """
    try:
        # create_client ritorna la chiave API, usata da extract_clinical_info
        client = create_client(API_KEY)
        data = extract_clinical_info(client, req.text)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
