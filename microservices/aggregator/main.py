from fastapi import FastAPI, HTTPException
import httpx
from contextlib import asynccontextmanager
from config import AUTH_SERVICE_URL, REPORT_SERVICE_URL, ROUTE_AUTH_SERVICE, ROUTE_REPORT_SERVICE
from datetime import date, datetime

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.client = httpx.AsyncClient(timeout=20.0)
    app.state.today = date.today()
    yield  # to be executed at shutdown
    await app.state.client.aclose()


app = FastAPI(title="Aggregator service", lifespan=lifespan)


@app.get("/")
async def health_check():
    return {"status": "T'appost Aggregator running!"}

@app.get("/aggregator/{patient_id}")
async def get_patient_context(patient_id: int):
    auth_resp = await app.state.client.get(f"{AUTH_SERVICE_URL}{ROUTE_AUTH_SERVICE}/{patient_id}")
    report_resp = await app.state.client.get(f"{REPORT_SERVICE_URL}{ROUTE_REPORT_SERVICE}/{patient_id}")
    
    if auth_resp.status_code != 200 or report_resp.status_code != 200:
        raise HTTPException(status_code=500, detail="Failed to fetch data")
    
    auth_data = auth_resp.json()
     # 🔹 Converti la data ISO in datetime.date
    
    # 🔹 Converte la stringa ISO in datetime.date
    birth_date = datetime.fromisoformat(auth_data['birth_date']).date()

    age = app.state.today.year - birth_date.year - (
        (app.state.today.month, app.state.today.day) < (birth_date.month, birth_date.day)
        )
    
    print("Age:", age)

    report_data = report_resp.json()

    print(report_data)
    # 🔹 Estrazione campi dai report
    reports_list = [
        {
            "data": r["date"],
            "motivazione": r["motivazione"],
            "diagnosi": r["diagnosi"],
            "sintomi": r["sintomi"],
            "trattamento": r["trattamento"]
        }
        for r in report_data
    ]

    # 🔹 Risposta aggregata
    return {
        "patient_id": patient_id,
        "social_sec_number": auth_data['social_sec_number'],
        "age": age,
        "sex": auth_data["sex"],
        "reports": reports_list
    }
    
