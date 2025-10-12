import os
from datetime import datetime


from fastapi import FastAPI, UploadFile, File, HTTPException, Form, Request
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
    request: Request, 
    file: UploadFile = File(None),
    text: str = Form(None)
):
    """
    Endpoint per ricevere un file audio o un testo manuale.
    Include gestione errori dettagliata per ogni fase.
    """
    print("File:", file)
    if file:
        print("File filename:", file.filename)

    try:
    
        if not file and not text:
            raise HTTPException(status_code=400, detail="Devi fornire un file audio o del testo")


        if file:
            audio_path = os.path.join("audio", file.filename)
            os.makedirs("audio", exist_ok=True)

            try:
                with open(audio_path, "wb") as buffer:
                    buffer.write(await file.read())
                print(f"Audio salvato: {audio_path}")
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Errore salvataggio file audio: {e}")

            try:
                print("Trascrizione in corso:", audio_path)
                raw_text = transcribe_audio_file(stt_model, audio_path)
            except FileNotFoundError:
                raise HTTPException(status_code=500, detail="File audio non trovato per la trascrizione.")
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Errore durante la trascrizione: {e}")

            finally:
                try:
                    os.remove(audio_path)
                    print(f"Audio {audio_path} eliminato")
                except Exception as cleanup_error:
                    print(f"Errore eliminazione {audio_path}: {cleanup_error}")


        elif text:
            print("testo ricevuto")
            raw_text = text.strip()
            if not raw_text:
                raise HTTPException(status_code=400, detail="Testo vuoto non valido.")

        try:
            corrected_text = correct_transcription(correction_model, transcription=raw_text)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Errore durante la correzione: {e}")

        print("testo corretto")

        try:
            os.makedirs("transcripts", exist_ok=True)
            base_filename = os.path.splitext(file.filename)[0] if file else f"manual_{datetime.now().strftime('%Y%m%d%H%M%S')}"
            save_transcription(corrected_text, base_filename)
            print(f"Trascrizione salvata: {base_filename}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Errore durante il salvataggio della trascrizione: {e}")

        
        output_ingest = {
            "input_type": "audio" if file else "text",
            "filename": file.filename if file else None,
            "corrected_text": corrected_text,
            "timestamp": datetime.now().strftime('%Y-%m-%dT%H-%M-%S')
        }

        print("Sending Decision")

        try:
            adapter = DecisionAdapter()
            response = await adapter.send(headers=request.headers, ingestion_output=output_ingest)
            print("Risposta dal Decision Service:", response)
            return response

        except ConnectionError as e:
            raise HTTPException(status_code=502, detail=f"Decision Service non raggiungibile: {e}")

    except HTTPException:
        # Propaga le eccezioni già gestite
        raise

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Errore interno non gestito: {e}")
