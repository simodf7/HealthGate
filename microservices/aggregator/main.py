from fastapi import FastAPI, HTTPException
import httpx
from contextlib import asynccontextmanager
from config import AUTH_SERVICE_URL, REPORT_SERVICE_URL, ROUTE_AUTH_SERVICE, ROUTE_REPORT_SERVICE
from datetime import date

@asynccontextmanager
async def lifespan():
    app.state.client = await httpx.AsyncClient(timeout=20.0)
    app.state.today = await date.today()
    yield  # to be executed at shutdown
    await app.state.client.aclose()


app = FastAPI("Aggregator service", lifespan=lifespan)


@app.get("/")
async def health_check():
    return {"status": "T'appost Aggregator running!"}

@app.get("/aggregator/{patient_id}")
async def get_patient_context(patient_id: id):
        auth_resp = await app.state.client.get(f"{AUTH_SERVICE_URL}{ROUTE_AUTH_SERVICE}/{patient_id}")
        report_resp = await app.state.client.get(f"{REPORT_SERVICE_URL}{ROUTE_REPORT_SERVICE}/{patient_id}")
        
        if auth_resp.status_code != 200 or report_resp.status_code != 200:
            raise HTTPException(status_code=500, detail="Failed to fetch data")
    
        age = app.state.today.year - auth_resp['birth_date'].year - (
        (app.state.today.month, app.state.today.day) < (auth_resp['birth_date'].month, auth_resp['birth_date'].day)
        )
        
        return {
            "patient_id": patient_id,
            "age": age, 
            "sex": auth_resp["sex"],
            "reports": reports
        }
