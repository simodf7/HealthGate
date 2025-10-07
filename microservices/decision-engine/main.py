from fastapi import FastAPI, HTTPException, Request
import httpx
from pydantic import BaseModel
from contextlib import asynccontextmanager
from typing import Dict
from model import load_all
import json
import re
from config import AGGREGATOR_SERVICE, AGGREGATOR_ROUTE

"""
@asynccontextmanager
async def lifespan(app: FastAPI):
    global embedding_model, llm, vector_store, graph
    llm = load_llm()
    embedding_model = load_embedding_model() 
    vector_store = load_vector_store(embedding_model, port=8010)
    graph = graph_building(vector_store, llm)
    print("Modelli caricati correttamente.")
    yield
"""


@asynccontextmanager
async def lifespan(app: FastAPI):
    global embedding_model, llm, vector_store, graph, client
    llm, embedding_model, vector_store, graph = await load_all()
    client = await httpx.AsyncClient()
    print("Modelli caricati correttamente.")
    yield



app = FastAPI(title="LLM Service", lifespan=lifespan)



# Schema input per la richiesta
class ClinicalRequest(BaseModel):
    # storia: str
    sintomi: str



@app.get("/")
def health():
    """Health check"""
    return {"status": "T'appost!! LLM Service running"}

@app.get("/llm")
def health_token():
    """Testing >Oken check"""
    return {"status": "Token Check running"}



@app.post("/llm/diagnose", response_model=Dict)
async def diagnose(req: ClinicalRequest, request: Request):
    """
    Endpoint che riceve un testo clinico e restituisce JSON strutturato
    dopo correzione, estrazione e validazione.
    """
    try:

        user_id = request.headers.get("X-User-Id")
        resp = await client.get(f"{AGGREGATOR_SERVICE}{AGGREGATOR_ROUTE}/{user_id}")
        resp.raise_for_status()
        

        response = graph.invoke({"sintomi": req.sintomi, "age": resp['age'], "sex": resp['sex'], "reports": resp['reports']})
         
        # Verifica che 'answer' sia presente e non None
        raw_answer = response.get("answer")
        print(raw_answer)

        if not raw_answer:
            # fallback in caso di risposta vuota o assente
            return {"decisione": "N/A", "motivazione": "LLM non ha restituito dati"}
        
        answer_text = re.sub(r"^```json\s*|```$", "", raw_answer.strip(), flags=re.MULTILINE)
    
        return json.loads(answer_text)  # rimuove eventuali backticks
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
