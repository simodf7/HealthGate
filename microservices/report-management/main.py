# python -m uvicorn main:app --reload --host 0.0.0.0 --port 8003

from fastapi import FastAPI, HTTPException, status, Header
from pydantic import BaseModel
from typing import Dict, List, Optional
import mongodb
from contextlib import asynccontextmanager
from pg_db import get_patient_anagrafica
from pdf_generator import genera_scheda_pdf_da_json


# ================== MODELLI PYDANTIC ==================

class CreateReportRequest(BaseModel):
    social_sec_number: str
    date: str  # data del report
    diagnosi: Optional[str] = None
    sintomi: Optional[str] = None
    trattamento: Optional[str] = None


class CreateReportResponse(BaseModel):
    success: bool
    report_id: Optional[str] = None
    error: Optional[str] = None


class GeneratePDFResponse(BaseModel):
    success: bool
    pdf_path: Optional[str] = None
    error: Optional[str] = None


# ================== LIFESPAN ==================

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Qui potresti inizializzare connessioni se necessario
    global db
    client = await mongodb.connect_db()
    db = await mongodb.get_db(client)
    yield  # to be executed at shutdown
    print("🛑 Report Management Service terminato")


app = FastAPI(title="Report Management Service", lifespan=lifespan)



# ================== ROUTES ==================

@app.get("/", response_model=dict)
async def health():
    return {"Status": "T'appost! Report Management Service running"}


# route per ottenere tutti i report di un paziente
@app.get("/reports/{patient_id}", response_model = List[Dict])
async def get_reports(patient_id: int):
    return mongodb.get_reports_by_patient(db, patient_id) 


# route per creare un nuovo report (solo dati clinici + CF)
@app.post("/report", response_model=CreateReportResponse)
async def create_report(
    data: CreateReportRequest,
    x_user_id: Optional[str] = Header(None),
    x_user_role: Optional[str] = Header(None)
):
    """
    Crea un nuovo report clinico salvando solo i dati clinici e il codice fiscale.
    NON salva i dati anagrafici.
    
    Args:
        data: Richiesta contenente social_sec_number, data, diagnosi, sintomi, trattamento
        x_user_id: ID utente dal gateway (opzionale)
        x_user_role: Ruolo utente dal gateway (opzionale)
    
    Returns:
        CreateReportResponse con success, report_id o error
    """
    try:
        print(f"📝 Creazione report per CF: {data.social_sec_number}")
        
        # Prepara i dati del report (solo dati clinici + CF)
        report_data = {
            "social_sec_number": data.social_sec_number,
            "date": data.date,
            "diagnosi": data.diagnosi,
            "sintomi": data.sintomi,
            "trattamento": data.trattamento
        }
        
        # Salva il report in MongoDB
        report_id = mongodb.save_report(patient_id, db, report_data)
        
        print(f"✅ Report creato con ID: {report_id}")
        return CreateReportResponse(
            success=True,
            report_id=report_id
        )
            
    except Exception as e:
        print(f"❌ Errore durante la creazione del report: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Errore interno: {str(e)}"
        )


# route per generare il PDF di un report esistente
@app.get("/report/pdf/{report_id}", response_model=GeneratePDFResponse)
async def generate_report_pdf(
    report_id: str,
    x_user_id: Optional[str] = Header(None),
    x_user_role: Optional[str] = Header(None)
):
    """
    Genera un PDF per un report esistente, unendo i dati clinici del report 
    con i dati anagrafici da PostgreSQL.
    
    Args:
        report_id: ID del report MongoDB
        x_user_id: ID utente dal gateway (opzionale)
        x_user_role: Ruolo utente dal gateway (opzionale)
    
    Returns:
        GeneratePDFResponse con success, pdf_path o error
    """
    try:
        print(f"🔍 Ricerca report con ID: {report_id}")
        
        # Recupera il report da MongoDB
        report = get_report_by_id(db, report_id)
        
        if not report:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Report non trovato con ID {report_id}"
            )
        
        print(f"✅ Report trovato per CF: {report.get('social_sec_number')}")
        
        # Recupera i dati anagrafici da PostgreSQL usando il codice fiscale
        # Assumendo che pg_db abbia una funzione per cercare per CF
        # Se non esiste, dovrai adattare questa parte
        patient_id = report.get('patient_id')  # se hai salvato anche patient_id
        if patient_id:
            anagrafica = get_patient_anagrafica(patient_id)
            if anagrafica:
                # Unisci anagrafica e dati del report
                dati_completi = {**anagrafica, **report}
            else:
                dati_completi = report
        else:
            # Se non hai patient_id, usa solo i dati del report
            dati_completi = report
        
        # Genera il PDF
        risultato = genera_scheda_pdf_da_json(
            dati_json=dati_completi, 
            mantieni_html=False
        )
        
        if risultato["success"]:
            print(f"🎉 PDF generato con successo: {risultato['pdf']}")
            return GeneratePDFResponse(
                success=True,
                pdf_path=risultato["pdf"]
            )
        else:
            print(f"❌ Errore nella generazione PDF: {risultato['error']}")
            return GeneratePDFResponse(
                success=False,
                error=risultato["error"]
            )
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Errore critico durante la generazione del PDF: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Errore interno: {str(e)}"
        )


# ================== ESEMPIO D'USO ==================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8005)