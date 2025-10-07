# Aggiungi questi import all'inizio del file main.py
from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel
from typing import Optional
import uvicorn

# Crea l'app FastAPI
app = FastAPI(title="Report")

# Schema per la richiesta
class GeneratePDFRequest(BaseModel):
    social_sec_number: str
    firstname: Optional[str] = None
    lastname: Optional[str] = None
    birth_date: Optional[str] = None
    sex: Optional[str] = None

# Schema per la risposta
class GeneratePDFResponse(BaseModel):
    success: bool
    pdf_path: Optional[str] = None
    error: Optional[str] = None

# Health check
@app.get("/")
def health_check():
    return {"status": "Report running"}

# Route per generare il PDF
@app.post("/generate-pdf", response_model=GeneratePDFResponse)
async def generate_pdf_endpoint(
    request: GeneratePDFRequest,
    x_user_id: Optional[str] = Header(None),
    x_user_role: Optional[str] = Header(None)
):
    """
    Genera un PDF del report paziente dato il codice fiscale.
    I dati anagrafici possono essere forniti nella richiesta o recuperati da MongoDB.
    """
    try:
        # Cerca il paziente in MongoDB
        paziente = cerca_paziente_per_codice_fiscale(request.social_sec_number)
        
        if not paziente:
            raise HTTPException(
                status_code=404, 
                detail=f"Nessun paziente trovato con codice fiscale {request.social_sec_number}"
            )
        
        # Sovrascrivi i dati anagrafici se forniti nella richiesta
        if request.firstname:
            paziente['firstname'] = request.firstname
        if request.lastname:
            paziente['lastname'] = request.lastname
        if request.birth_date:
            paziente['birth_date'] = request.birth_date
        if request.sex:
            paziente['sex'] = request.sex
        
        print(f"✅ Paziente trovato: {paziente.get('firstname', '')} {paziente.get('lastname', '')}")
        
        # Genera il PDF
        risultato = genera_scheda_pdf_da_json(dati_json=paziente, mantieni_html=False)
        
        if risultato["success"]:
            print(f"🎉 PDF generato con successo: {risultato['pdf']}")
            return GeneratePDFResponse(
                success=True,
                pdf_path=risultato["pdf"]
            )
        else:
            return GeneratePDFResponse(
                success=False,
                error=risultato["error"]
            )
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Errore durante la generazione del PDF: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Errore interno: {str(e)}")


# Avvia il server se eseguito direttamente
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8003)