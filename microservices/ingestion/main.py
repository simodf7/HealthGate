import os
import json
from datetime import datetime
import whisper
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse

# Caricamento modello Whisper una sola volta
MODEL_NAME = "base"
print(f"Caricamento del modello Whisper: {MODEL_NAME}")
model = whisper.load_model(MODEL_NAME)

# Config cartelle
AUDIO_FOLDER = os.path.join(os.path.dirname(__file__), "audio")
TRANSCRIPTS_FOLDER = os.path.join(os.path.dirname(__file__), "transcripts")
os.makedirs(AUDIO_FOLDER, exist_ok=True)
os.makedirs(TRANSCRIPTS_FOLDER, exist_ok=True)

app = FastAPI(title="Ingestion Microservice - Speech to Text")

def transcribe_audio_file(audio_path: str) -> str:
    """
    Trascrive un singolo file audio con Whisper
    """
    try:
        print(f"Trascrizione in corso: {audio_path}")
        result = model.transcribe(audio_path)
        return result["text"]
    except Exception as e:
        print(f"Errore durante la trascrizione di {audio_path}: {e}")
        raise

def save_transcription(text: str, filename: str) -> str:
    """
    Salva la trascrizione in JSON con testo e timestamp
    """
    try:
        output_path = os.path.join(TRANSCRIPTS_FOLDER, filename + ".json")
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump({
                "transcription": text,
                "timestamp": datetime.now().strftime('%Y-%m-%dT%H-%M-%S')
            }, f, indent=2)
        print(f"Trascrizione salvata correttamente in: {output_path}")
        return output_path
    except Exception as e:
        print(f"Errore durante il salvataggio: {e}")
        raise

@app.post("/ingestion/transcribe")
async def transcribe(file: UploadFile = File(...)):
    """
    Endpoint per ricevere un file audio, trascriverlo e restituire il testo
    """
    try:
        # Salvataggio temporaneo file audio
        audio_path = os.path.join(AUDIO_FOLDER, file.filename)
        with open(audio_path, "wb") as buffer:
            buffer.write(await file.read())

        # Trascrizione
        text = transcribe_audio_file(audio_path)

        # Salvataggio transcript
        base_filename = os.path.splitext(file.filename)[0]
        save_transcription(text, base_filename)

        # Risposta API
        return JSONResponse(content={
            "filename": file.filename,
            "transcription": text,
            "timestamp": datetime.now().strftime('%Y-%m-%dT%H-%M-%S')
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Errore durante la trascrizione: {e}")
