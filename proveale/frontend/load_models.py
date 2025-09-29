"""
[FRONTEND] load_models.py

Modulo per il caricamento e l'inizializzazione dei modelli AI.
"""

import streamlit as st
import os
import sys

# Ottieni il path assoluto del progetto (cartella superiore)
base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
backend_path = os.path.join(base_path, 'backend')

# Aggiungi 'backend' ai percorsi riconosciuti da Python
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

import speech_to_text as stt
import text_to_json as ttj

# Ottieni la directory assoluta del file corrente (streamlit_app.py)
base_dir = os.path.dirname(os.path.abspath(__file__))

AUDIO_FOLDER = os.path.abspath(os.path.join(base_dir, "..", "backend", "audio"))
TRANSCRIPTS_FOLDER = os.path.abspath(os.path.join(base_dir, "..", "backend", "transcripts"))
REPORTS_FOLDER = os.path.abspath(os.path.join(base_dir, "..", "backend", "reports"))

os.makedirs(REPORTS_FOLDER, exist_ok=True)

def session_init():
    '''
    Registrazione e session states
    '''
    # === SESSION STATE INIT ===
    if "audio_uploaded" not in st.session_state:
        st.session_state.audio_uploaded = False
    if "audio_path" not in st.session_state:
        st.session_state.audio_path = ""
    if "json_path" not in st.session_state:
        st.session_state.json_path = TRANSCRIPTS_FOLDER
    if "transcription_text" not in st.session_state:
        st.session_state.transcription_text = ""
    if "structured_json" not in st.session_state:
        st.session_state.structured_json = {}
    if "edited_json" not in st.session_state:
        st.session_state.edited_json = {}
    if "transcription_done" not in st.session_state:
        st.session_state.transcription_done = False

    # === CARICA MODELLI ===
    # Pulisci le vecchie chiavi della session state se esistono
    for old_key in ['llm_model', 'llm_tokenizer', 'llm_device', 'client', 'model_id']:
        if old_key in st.session_state:
            del st.session_state[old_key]

    if "voice_text_model" not in st.session_state or "api_key" not in st.session_state:
        with st.spinner("Avvio sistema in corso..."):
            st.session_state.voice_text_model = stt.load_model() # Carica il modello Speech to Text
            st.session_state.api_key = ttj.create_client("AIzaSyA5Zg5KHd7bA7k16bEbL5ef8vKYRY0zjkc") # Inizializza client Google AI Studio