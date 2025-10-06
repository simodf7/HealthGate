import os
from datetime import datetime
from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from contextlib import asynccontextmanager
from ingest_ops import transcribe_audio_file, save_transcription, correct_transcription
from model import load_model_stt, load_model_correction
from adapter import DecisionAdapter



@asynccontextmanager
async def lifespan(app: FastAPI):
    # Caricamento modello Whisper all'avvio del servizio
    global stt_model, correction_model
    # Creazione cartelle se non esistono    
    os.makedirs("audio", exist_ok=True)
    os.makedirs("transcripts", exist_ok=True)
    stt_model = load_model_stt()
    correction_model = load_model_correction() 
    print("Modello caricato correttamente.")
    yield


app = FastAPI(title="Ingestion Microservice", lifespan=lifespan)

@app.get("/")
async def health_check():
    return {"status": "T'appost ! Il microservizio di ingestion è attivo."}



@app.post("/ingestion", response_model=dict)
async def ingest(
            file: UploadFile = File(None),
            text: str = Form(None)
        ):
    
    """
    Endpoint per ricevere o un file audio o un testo manuale
    """
    print("File:" , file)
    print("FIle filename: ", file.filename)

    try:
        if file:
            audio_path = os.path.join("audio", file.filename)
            print("Audio path:", audio_path)
            with open(audio_path, "wb") as buffer:
                buffer.write(await file.read())
 
            # Trascrizione
            raw_text = transcribe_audio_file(stt_model, audio_path)

            try:
                os.remove(audio_path)
                print(f"Audio {audio_path} eliminato")
            except Exception as cleanup_error:
                print(f"Errore eliminazione {audio_path}: {cleanup_error}")
    
 
        elif text:
            raw_text = text
 
        else:
           
            raise HTTPException(status_code=400, detail="Devi fornire un file audio o del testo")
 
        # Correzione
        corrected_text = correct_transcription(correction_model, transcription=raw_text)
 
        # Salvataggio transcript (usiamo timestamp come nome se non è audio)
        base_filename = os.path.splitext(file.filename)[0] if file else f"manual_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        save_transcription(corrected_text, base_filename)
    
       

        output_ingest = {
            "input_type": "audio" if file else "text",
            "filename": file.filename if file else None,
            "corrected_text": corrected_text,
            "timestamp": datetime.now().strftime('%Y-%m-%dT%H-%M-%S')
        }

        # vedi nel file adapter perchè 
        adapter = DecisionAdapter()
        response = await adapter.send(output_ingest)

        print("Response:", response)    
        return response
 
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Errore durante l'ingestione: {e}")
    

