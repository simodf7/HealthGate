# python -m uvicorn main:app --reload --host 0.0.0.0 --port 8003

from fastapi import FastAPI, HTTPException, status, Header
from pydantic import BaseModel
from typing import Dict, List, Optional
from mongodb import connect_db, get_db
from contextlib import asynccontextmanager
from mongodb import reports, cerca_paziente_per_codice_fiscale
from pdf_generator import genera_scheda_pdf_da_json


# ================== MODELLI PYDANTIC ==================

class GeneratePDFRequest(BaseModel):
    social_sec_number: str
    firstname: Optional[str] = None
    lastname: Optional[str] = None
    birth_date: Optional[str] = None
    sex: Optional[str] = None


class GeneratePDFResponse(BaseModel):
    success: bool
    pdf_path: Optional[str] = None
    error: Optional[str] = None


# ================== LIFESPAN ==================

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Qui potresti inizializzare connessioni se necessario
    global db
    client = await connect_db()
    db = await get_db(client)
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
    
    ## SE PUOI IMPLEMENTA UNA FUNZ SIMILE A CERCA PER CODICE FISCALE, MA CON L'ID 

    ## GET_REPORTS_BY_PATIENT 

    return reports 


# route per ottenere tutti i report di un paziente con il codice fiscale (RICHIAMATO DALL'OPERATORE)
@app.get("/reports/{social_sec_number}", response_model = List[Dict])
async def get_reports():
    
    ## GET_REPORTS_BY_PATIENT 

    return reports 



# route per generare un nuovo report 
@app.post("/report", response_model=GeneratePDFResponse)
async def generate_report(
    data: GeneratePDFRequest,
    x_user_id: Optional[str] = Header(None),
    x_user_role: Optional[str] = Header(None)
):
    """
    Genera un PDF del report paziente dato il codice fiscale.
    I dati anagrafici possono essere forniti nella richiesta o recuperati da MongoDB.
    
    Args:
        data: Richiesta contenente social_sec_number e opzionalmente dati anagrafici
        x_user_id: ID utente dal gateway (opzionale)
        x_user_role: Ruolo utente dal gateway (opzionale)
    
    Returns:
        GeneratePDFResponse con success, pdf_path o error
    """
    try:
        print(f"🔍 Ricerca paziente con codice fiscale: {data.social_sec_number}")
        
        # Cerca il paziente in MongoDB
        paziente = cerca_paziente_per_codice_fiscale(data.social_sec_number)
        
        if not paziente:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Nessun paziente trovato con codice fiscale {data.social_sec_number}"
            )
        
        # Sovrascrivi i dati anagrafici se forniti nella richiesta
        if data.firstname:
            paziente['firstname'] = data.firstname
        if data.lastname:
            paziente['lastname'] = data.lastname
        if data.birth_date:
            paziente['birth_date'] = data.birth_date
        if data.sex:
            paziente['sex'] = data.sex
        
        print(f"✅ Paziente trovato: {paziente.get('firstname', '')} {paziente.get('lastname', '')}")
        

        ## CARICA IN MONGODB IL REPORT; QUI NON TI DEVI PREOCCUPARE DEI DATI ANAGRAFICI.
        ## DEVI SOLO CARICARE SINTOMI ETC.

        ## SOLO NELL'ALTRA ROUTE DI GENERAZIONE PDF, DEVI CHIAMARE LA FUNZ SUCCESSIVA



        # Genera il PDF
        risultato = genera_scheda_pdf_da_json(
            dati_json=paziente, 
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

# route per ottenere il pdf di un report
@app.get("/report/pdf/{report_id}")



# ================== ESEMPIO D'USO ==================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)