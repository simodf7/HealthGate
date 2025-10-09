# python -m uvicorn main:app --reload --host 0.0.0.0 --port 8005

from fastapi import FastAPI
from typing import List
from mongodb import * 
from contextlib import asynccontextmanager
from pdf_generator import genera_scheda_pdf_da_json
from validation import *
from report_ops import get_anagrafica

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Inizializza connessioni al database
    global db
    db = await connect_db()
    print("Connessione a MongoDB stabilita")
    yield
    print("Report Management Service terminato")

app = FastAPI(title="Report Management Service", lifespan=lifespan)


# ================== ROUTES ==================

@app.get("/", response_model=dict)
async def health():
    return {"Status": "T'appost! Report Management Service running"}


## ROUTE PER RICAVARE TUTTI I REPORT
@app.get("/reports", response_model=List[Report])
async def find_all_reports():
    collection = db['reports']
    reports = await get_reports(collection)
    return reports
        

## ROUTE PER CREARE UN REPORT

# Test report insert  METTERE I DATI CORRETTI
@app.post("/report", response_model=CreateReportResponse)
async def create_report(data: TestCreateReportRequest):
   
    collection = db['reports']

    # Prepara i dati del report
    report_data = {
        "patient_id": data.patient_id,
        "social_sec_number": data.social_sec_number,
        "date": data.date,
        "sintomi": data.sintomi,
        "diagnosi": "",
        "trattamento": ""
    }
    
    # Salva il report in MongoDB
    report_id = await save_report(collection, report_data)
    
    print(f"✅ Report creato con ID: {report_id}")
    return CreateReportResponse(success=True, report_id=report_id)


## ROUTE PER RICAVARE I REPORT DI UN PAZIENTE

@app.get("/reports/id/{patient_id}", response_model=List[Report])
async def find_report_by_patient_id(patient_id: int):
    """
    Ottiene tutti i report di un paziente tramite patient_id
    """
    collection = db['reports']
    reports = await get_reports_by_patient_id(collection, patient_id)
    return reports



@app.get("/reports/ssn/{social_sec_number}", response_model=List[Report])
async def find_report_by_patient_ssn(social_sec_number: str):
    """
    Ottiene tutti i report di un paziente tramite codice fiscale
    """
    collection = db['reports']
    reports = await get_reports_by_patient_ssn(collection, social_sec_number)
    return reports


## ROUTE PER RICAVARE UN SINGOLO REPORT (CON REPORT_ID)

@app.get("/report/{report_id}", response_model=Report)
async def find_report_by_id(report_id: str):
    collection = db['reports']
    return await get_report_by_id(collection, report_id)



## ROUTE PER AGGIORNARE UN SINGOLO REPORT
@app.put("/report/{report_id}", response_model=Report)
async def update_report(data: UpdateRequest):
    collection = db['reports']
    return await modify_report(collection, data.report_id, data.diagnosi, data.trattamento)

    
## ROUTE PER GENERARE UN PDF 
@app.get("/report/pdf/{report_id}", response_model=GeneratePDFResponse)
async def pdf_from_report(report_id: str):
    collection = db['reports']
    report = await get_report_by_id(collection, report_id)
    anagrafica = await get_anagrafica(report)
    dati_completi = {**anagrafica, **report}
    return await genera_scheda_pdf_da_json(dati_json=dati_completi, mantieni_html=False)







''' 
@app.post("/report", response_model=CreateReportResponse)
async def create_report(data: CreateReportRequest, request: Request):
        
    patient_id = request.headers["X-user-id"],
    
    # Prepara i dati del report
    report_data = {
        "patient_id": patient_id,
        "social_sec_number": data.social_sec_number,
        "date": data.date,
        "sintomi": data.sintomi,
        "diagnosi": "",
        "trattamento": ""
    }
    
    # Salva il report in MongoDB
    report_id = await save_report(patient_id, db, report_data)
    
    print(f"✅ Report creato con ID: {report_id} per patient_id: {patient_id}")
    return CreateReportResponse(success=True, report_id=report_id)
            
'''














'''
@app.post("/report", response_model=CreateReportResponse)
async def create_report(
    data: CreateReportRequest,
    x_user_id: Optional[str] = Header(None),
    x_user_role: Optional[str] = Header(None)
):
    """
    Crea un nuovo report clinico salvando solo i dati clinici e il codice fiscale.
    Recupera automaticamente il patient_id dal codice fiscale.
    """
    try:
        print(f"📝 Creazione report per CF: {data.social_sec_number}")
        print(f"👤 Utente: {x_user_id}, Ruolo: {x_user_role}")
        
        # Cerca il patient_id dal codice fiscale
        patient_id = get_patient_id_from_cf(data.social_sec_number)
        
        if not patient_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Paziente non trovato con codice fiscale: {data.social_sec_number}"
            )
        
        # Prepara i dati del report
        report_data = {
            "social_sec_number": data.social_sec_number,
            "patient_id": patient_id,
            "date": data.date,
            "diagnosi": data.diagnosi,
            "sintomi": data.sintomi,
            "trattamento": data.trattamento
        }
        
        # Salva il report in MongoDB
        report_id = save_report(patient_id, db, report_data)
        
        print(f"✅ Report creato con ID: {report_id} per patient_id: {patient_id}")
        return CreateReportResponse(success=True, report_id=report_id)
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Errore durante la creazione del report: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Errore interno: {str(e)}"
        )
'''




if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8005)