"""
[BACKEND] speech_to_text.py

Modulo per la trascrizione audio mediante Whisper AI in locale.
"""

import whisper
import os
import json
from datetime import datetime

def transcribe_audio_file(model, audio_path):
    """
    Trascrive un singolo file audio con Whisper
    """
    try:
        print(f"Trascrizione in corso: {audio_path}")
        result = model.transcribe(audio_path)
        return result["text"]
    except Exception as e:
        print(f"Errore durante la trascrizione di {audio_path}: {e}")
        return None

def save_transcription(text, output_path):
    """
    Salva la trascrizione in JSON con: testo, timestamp
    Utile per identificare l'istante in cui è stata fatta la trascrizione
    Il timestamp fa da identificativo alla singola azione del medico
    """
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump({
                "transcription": text,
                "timestamp": datetime.now().strftime('%Y-%m-%dT%H-%M-%S')
            }, f, indent=2)
        print(f"Trascrizione salvata correttamente in: {output_path}")
    except Exception as e:
        print(f"Errore durante il salvataggio: {e}")

def load_model():
    '''
    Carica il modello.
    '''
    model_name = "base" # 74 M di parametri, meno di 1 GB di VRAM richiesti. Buon compromesso per avere un sistema veloce

    # Caricamento modello Whisper
    print(f"Caricamento del modello Whisper: {model_name}")
    return whisper.load_model(model_name)

def speech_to_text(model, file):
    '''
    Conversione da voce a testo con Whisper dell'audio di interesse
    Assume che il modello sia già caricato!
    '''
    # Configurazione
    input_folder = os.path.join(os.path.dirname(__file__), "audio") # Cartella dove viene salvato l'audio registrato dal medico
    output_folder = os.path.join(os.path.dirname(__file__), "transcripts") # Cartella dove viene salvata la trascrizione di Whisper
    os.makedirs(output_folder, exist_ok=True)

    # Analisi e trascrizione del file audio
    if file.lower().endswith((".mp3", ".wav", ".m4a")):
        input_path = os.path.join(input_folder, file)
        output_file = os.path.splitext(file)[0] + ".json"
        output_path = os.path.join(output_folder, output_file)

        # Trascrizione + Salvataggio
        text = transcribe_audio_file(model, input_path)
        
        if text: # Se il metodo transcribe_audio_file restituisce None, non si salva nulla
            save_transcription(text, output_path)
