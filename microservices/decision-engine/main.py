from datetime import datetime
from fastapi import FastAPI, HTTPException, Request
import httpx
from pydantic import BaseModel
from contextlib import asynccontextmanager
from typing import Dict
from model import load_all
import json
import re
from config import *

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
    print("Inizio caricamento modelli...", flush=True)
    llm, embedding_model, vector_store, graph = await load_all()
    print("Modelli caricati correttamente.", flush=True)
    client = httpx.AsyncClient(timeout=20.0)
    yield
    await client.aclose()



app = FastAPI(title="LLM Service", lifespan=lifespan)


class DiagnoseRequest(BaseModel):
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
async def diagnose(data: DiagnoseRequest, request: Request):
    """
    Endpoint che riceve un testo clinico e restituisce JSON strutturato
    dopo correzione, estrazione e validazione.
    """
    try:

        print("Ricevuta richiesta")
        user_id = request.headers.get("X-User-Id")
        resp = await client.get(f"{AGGREGATOR_SERVICE}{AGGREGATOR_ROUTE}/{user_id}")
        resp.raise_for_status()
        
        resp = resp.json()
        print("appost")
        print(resp)
        response = graph.invoke({"sintomi": data.sintomi, "age": resp['age'], "sex": resp['sex'], "reports": resp['reports']})
         
        print("Ripost")

        # Verifica che 'answer' sia presente e non None
        raw_answer = response.get("answer")
        print(raw_answer)

        if not raw_answer:
            # fallback in caso di risposta vuota o assente
            return {"decisione": "N/A", "motivazione": "LLM non ha restituito dati"}
        
        answer_text = re.sub(r"^```json\s*|```$", "", raw_answer.strip(), flags=re.MULTILINE)

        answer_json = json.loads(answer_text)
        
        # Costruisci il payload per /report
        report_payload = {
            "patient_id": resp['patient_id'],
            "social_sec_number": resp['social_sec_number'],
            "date": datetime.now().strftime("%Y-%m-%d"),
            "sintomi": data.sintomi,
            "motivazione": answer_json.get("motivazione", ""),
            "diagnosi": "",
            "trattamento": ""
        }

        print(report_payload)
        
        response = await client.post(f"{REPORT_SERVICE_URL}{REPORT_ROUTE}", json = report_payload)


        return answer_json 
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
