# python -m uvicorn main:app --reload --host 0.0.0.0 --port 8005

from fastapi import FastAPI, HTTPException, status, Header
from pydantic import BaseModel
from typing import Dict, List, Optional
import mongodb
from contextlib import asynccontextmanager
from pg_db import get_patient_anagrafica, get_patient_id_by_cf
from pdf_generator import genera_scheda_pdf_da_json
from bson import ObjectId
from datetime import datetime


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

class SyncPatientRequest(BaseModel):
    social_sec_number: str
    firstname: str
    lastname: str
    birth_date: str
    sex: str
    patient_id: int

class SyncPatientResponse(BaseModel):
    success: bool
    message: Optional[str] = None
    error: Optional[str] = None


# ================== FUNZIONI HELPER ==================

def get_patient_id_from_cf(social_sec_number: str) -> Optional[int]:
    """
    Cerca il patient_id dal codice fiscale in PostgreSQL
    """
    try:
        patient_id = get_patient_id_by_cf(social_sec_number)
        if patient_id:
            print(f"✅ Trovato patient_id {patient_id} per CF: {social_sec_number}")
            return patient_id
        else:
            print(f"❌ Nessun patient_id trovato per CF: {social_sec_number}")
            return None
    except Exception as e:
        print(f"❌ Errore nella ricerca patient_id per CF {social_sec_number}: {str(e)}")
        return None

def get_report_by_id(db, report_id: str):
    """
    Recupera un report da MongoDB per ID
    """
    try:
        # Converti string ID in ObjectId
        object_id = ObjectId(report_id)
        report = db.find_one({"_id": object_id})
        
        if report:
            # Converti ObjectId in string per il JSON
            report["_id"] = str(report["_id"])
            print(f"✅ Report trovato: {report_id}")
        else:
            print(f"❌ Report non trovato: {report_id}")
            
        return report
    except Exception as e:
        print(f"❌ Errore nel recupero report {report_id}: {str(e)}")
        return None

def save_patient_data_to_mongodb(db, patient_data: Dict):
    """
    Salva i dati del paziente in MongoDB per riferimento futuro
    """
    try:
        # Usa una collection separata per i dati paziente
        patients_collection = db.client.healthgate_db.patients
        
        # Aggiungi timestamp di sincronizzazione
        patient_data["synced_at"] = datetime.now().isoformat()
        patient_data["last_updated"] = datetime.now().isoformat()
        
        # Upsert: aggiorna se esiste, altrimenti inserisci
        result = patients_collection.update_one(
            {"patient_id": patient_data["patient_id"]},
            {"$set": patient_data},
            upsert=True
        )
        
        if result.upserted_id:
            print(f"✅ Nuovo paziente salvato in MongoDB: {patient_data['patient_id']}")
        else:
            print(f"✅ Paziente aggiornato in MongoDB: {patient_data['patient_id']}")
            
        return True
        
    except Exception as e:
        print(f"❌ Errore nel salvataggio paziente in MongoDB: {str(e)}")
        return False


# ================== LIFESPAN ==================

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Inizializza connessioni al database
    global db
    client = await mongodb.connect_db()
    db = await mongodb.get_db(client)
    print("✅ Connessione a MongoDB stabilita")
    yield
    print("🛑 Report Management Service terminato")

app = FastAPI(title="Report Management Service", lifespan=lifespan)


# ================== ROUTES ==================

@app.get("/", response_model=dict)
async def health():
    return {"Status": "T'appost! Report Management Service running"}

@app.post("/patient/sync", response_model=SyncPatientResponse)
async def sync_patient_data(patient_data: SyncPatientRequest):
    """
    Sincronizza i dati del paziente dall'Authentication Service
    """
    try:
        print(f"🔄 Sincronizzazione dati paziente: {patient_data.firstname} {patient_data.lastname}")
        
        # Converti il Pydantic model in dict
        patient_dict = patient_data.dict()
        
        # Salva i dati del paziente in MongoDB
        save_success = save_patient_data_to_mongodb(db, patient_dict)
        
        if save_success:
            message = f"Dati paziente {patient_data.firstname} {patient_data.lastname} sincronizzati con successo"
            print(f"✅ {message}")
            return SyncPatientResponse(success=True, message=message)
        else:
            error_msg = "Errore nel salvataggio dei dati paziente"
            print(f"❌ {error_msg}")
            return SyncPatientResponse(success=False, error=error_msg)
        
    except Exception as e:
        error_msg = f"Errore nella sincronizzazione paziente: {str(e)}"
        print(f"❌ {error_msg}")
        return SyncPatientResponse(success=False, error=error_msg)

@app.get("/reports/{patient_id}", response_model=List[Dict])
async def get_reports(patient_id: int):
    """
    Ottiene tutti i report di un paziente tramite patient_id
    """
    try:
        reports = mongodb.get_reports_by_patient(db, patient_id)
        print(f"✅ Trovati {len(reports)} report per patient_id: {patient_id}")
        return reports
    except Exception as e:
        print(f"❌ Errore nel recupero report per patient_id {patient_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Errore interno: {str(e)}"
        )

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
        report_id = mongodb.save_report(patient_id, db, report_data)
        
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

@app.get("/report/pdf/cf/{social_sec_number}", response_model=GeneratePDFResponse)
async def generate_report_pdf_by_cf(
    social_sec_number: str,
    x_user_id: Optional[str] = Header(None),
    x_user_role: Optional[str] = Header(None)
):
    """
    Genera un PDF per un report esistente cercando tramite codice fiscale
    """
    try:
        print(f"🔍 Ricerca report con codice fiscale: {social_sec_number}")
        print(f"👤 Utente: {x_user_id}, Ruolo: {x_user_role}")
        
        # Recupera il report più recente da MongoDB tramite codice fiscale
        report = mongodb.cerca_paziente_per_codice_fiscale(db, social_sec_number)
        
        if not report:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Report non trovato per CF {social_sec_number}"
            )
        
        print(f"✅ Report trovato per CF: {social_sec_number}")
        
        # Recupera i dati anagrafici dal patient_id se esiste
        patient_id = report.get('patient_id')
        if patient_id:
            anagrafica = get_patient_anagrafica(patient_id)
            if anagrafica:
                dati_completi = {**anagrafica, **report}
                print(f"✅ Dati anagrafici recuperati per patient_id: {patient_id}")
            else:
                dati_completi = report
                print(f"⚠️ Dati anagrafici non trovati per patient_id: {patient_id}")
        else:
            dati_completi = report
            print("⚠️ Nessun patient_id trovato nel report")
        
        # Genera il PDF
        print("🔄 Generazione PDF in corso...")
        risultato = genera_scheda_pdf_da_json(dati_json=dati_completi, mantieni_html=False)
        
        if risultato["success"]:
            print(f"🎉 PDF generato con successo: {risultato['pdf']}")
            return GeneratePDFResponse(success=True, pdf_path=risultato["pdf"])
        else:
            print(f"❌ Errore nella generazione PDF: {risultato['error']}")
            return GeneratePDFResponse(success=False, error=risultato["error"])
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Errore critico durante la generazione del PDF: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Errore interno: {str(e)}"
        )


@app.get("/reports/cf/{social_sec_number}", response_model=List[Dict])
async def get_reports_by_cf(social_sec_number: str):
    """
    Ottiene tutti i report di un paziente tramite codice fiscale
    """
    try:
        # Cerca prima il patient_id
        patient_id = get_patient_id_from_cf(social_sec_number)
        
        if not patient_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Paziente non trovato con codice fiscale: {social_sec_number}"
            )
        
        # Poi recupera i report
        reports = mongodb.get_reports_by_patient(db, patient_id)
        print(f"✅ Trovati {len(reports)} report per CF: {social_sec_number} (patient_id: {patient_id})")
        return reports
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Errore nel recupero report per CF {social_sec_number}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Errore interno: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8005)