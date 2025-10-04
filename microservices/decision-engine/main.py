from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from contextlib import asynccontextmanager
from typing import Dict
from model import load_embedding_model, load_llm, load_vector_store
from rag_setup import graph_building


@asynccontextmanager
async def lifespan(app: FastAPI):
    global embedding_model, llm, vector_store, graph
    llm = load_llm()
    embedding_model = load_embedding_model() 
    vector_store = load_vector_store(embedding_model)
    graph = graph_building(vector_store, llm)
    print("Modelli caricati correttamente.")
    yield


app = FastAPI(title="LLM Service", lifespan=lifespan)



# Schema input per la richiesta
class ClinicalRequest(BaseModel):
    storia: str
    sintomi: str



@app.get("/")
def health():
    """Health check"""
    return {"status": "LLM Service running"}

@app.get("/llm")
def health_token():
    """Testing >Oken check"""
    return {"status": "Token Check running"}



@app.post("/llm/diagnose", response_model=Dict)
async def extract(req: ClinicalRequest):
    """
    Endpoint che riceve un testo clinico e restituisce JSON strutturato
    dopo correzione, estrazione e validazione.
    """
    try:
        response = graph.invoke({"sintomi": req.sintomi, "storia_paziente": req.storia})
        return response["answer"]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
