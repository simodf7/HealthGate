'''
[FRONTEND] input_capture.py

Modulo per la cattura e l'elaborazione dei dati di input (audio o testo).
Gestisce la logica per la registrazione, il caricamento e la conferma dei dati inseriti dall'utente.
'''

import streamlit as st
import os
import json
import ast
import sys
from codicefiscale import codicefiscale
from datetime import datetime

# Percorsi ai moduli backend
# sys.path.append('./backend')
# sys.path.append('./frontend')

# Ottieni il path assoluto del progetto (cartella superiore)
base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
backend_path = os.path.join(base_path, 'backend')

# Aggiungi 'backend' ai percorsi riconosciuti da Python
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

import speech_to_text as stt
import text_to_json as ttj
import data_check_visualizer as dc
import database.store_data as sd
import pdf_generator as pg

# Ottieni la directory assoluta del file corrente
base_dir = os.path.dirname(os.path.abspath(__file__))

# Cartelle per salvataggio audio, trascrizioni e report
AUDIO_FOLDER = os.path.abspath(os.path.join(base_dir, "..", "backend", "audio"))
TRANSCRIPTS_FOLDER = os.path.abspath(os.path.join(base_dir, "..", "backend", "transcripts"))
REPORTS_FOLDER = os.path.abspath(os.path.join(base_dir, "..", "backend", "reports"))

os.makedirs(REPORTS_FOLDER, exist_ok=True)

def data_insert():
    """
    Gestisce l'inserimento dei dati da parte dell'utente.
    Permette di scegliere tra registrazione audio, caricamento file audio o inserimento testuale.
    Salva i dati inseriti e aggiorna lo stato della sessione.
    """
    # === SELEZIONE MODALITÀ ===
    data_mode = st.radio(
        "Scegli la modalità:",
        ["🎙️ Registra dati", "📁 Carica audio", "🖊️ Trascrivi i sintomi"],
        horizontal=True
    )
    
    # Variabili per dati inseriti e tipo file
    inserted_data = None
    file_extension = None

    if data_mode == "🎙️ Registra dati":
        # === REGISTRAZIONE DATI ===
        inserted_data = st.audio_input("Registra un audio:", label_visibility="visible")
        file_extension = ".wav"
        
    elif data_mode == "📁 Carica audio":
        # === CARICAMENTO FILE DATI ===
        inserted_data = st.file_uploader(
            "Carica un file audio:",
            type=["wav", "mp3", "m4a", "ogg", "flac"],
            help="Formati supportati: WAV, MP3, M4A, OGG, FLAC"
        )
        if inserted_data:
            file_extension = "." + inserted_data.name.split(".")[-1].lower()

    else:
        # === INPUT TESTUALE ===
        text_input = st.text_area(
            "Inserisci i sintomi:",
            placeholder="Descrivi qui i tuoi sintomi...",
            height="content"
        )
        if st.button("✅ Conferma testo", use_container_width=True):
            if text_input.strip():
                inserted_data = text_input.encode('utf-8')
                file_extension = ".txt"
            else:
                st.warning("⚠️ Per favore, inserisci del testo prima di confermare.")

    # Salvataggio dati (audio o testo)
    if inserted_data and not st.session_state.get("data_path"):
        # Crea le cartelle se non esistono
        os.makedirs(AUDIO_FOLDER, exist_ok=True)
        os.makedirs(TRANSCRIPTS_FOLDER, exist_ok=True)
          
        # Svuota lo stato precedente per sicurezza
        st.session_state.data_uploaded = False
        st.session_state.transcription_done = False

        # Genera nome file con timestamp ed estensione appropriata
        timestamp = datetime.now().strftime('%Y-%m-%dT%H-%M-%S')

        # Crea nomi file per dati e json
        data_filename = f"{timestamp}{file_extension}"
        json_filename = f"{timestamp}.json"

        # Percorsi completi per salvataggio
        data_path = os.path.join(AUDIO_FOLDER, data_filename)
        json_path = os.path.join(TRANSCRIPTS_FOLDER, json_filename)

        try:
            # Salva il file dati / testo
            if data_mode == "🖊️ Trascrivi i sintomi":
                with open(data_path, "wb") as f:
                    f.write(inserted_data)
            else:
                with open(data_path, "wb") as f:
                    f.write(inserted_data.getvalue())
            # Aggiorna lo stato della sessione con i percorsi e flag
            st.session_state.data_path = data_path
            st.session_state.json_path = json_path 
            st.session_state.data_filename = data_filename
            st.session_state.data_uploaded = True
            st.session_state.paths_set = True
                
            # Mostra informazioni sul file caricato/inserito
            if data_mode == "📁 Carica audio":
                st.success(f"✅ File '{inserted_data.name}' caricato correttamente!")
            elif data_mode == "🎙️ Registra dati":
                st.success("✅ Registrazione salvata correttamente!")
            else:
                st.success("✅ Testo inserito correttamente!")
            
            # Bottone per procedere solo se audio
            if data_mode != "🖊️ Trascrivi i sintomi":
                st.markdown('<div class="proceed-button">', unsafe_allow_html=True)
                if st.button("🚀 Procedi con la trascrizione", use_container_width=True):
                    print_debug("Utente ha cliccato 'Procedi con la trascrizione' - passaggio a view 'transcribe'")
                    st.session_state.view = "transcribe"
                st.markdown('</div>', unsafe_allow_html=True)
            else:
                # Per input testuale, vai direttamente alla view 'transcribe' e imposta la trascrizione come completata
                st.session_state.transcription_text = text_input
                st.session_state.transcription_done = True
                st.session_state.view = "transcribe"
                
        except Exception as e:
            st.error(f"❌ Errore nel salvataggio dei dati: {e}")

def interface():
    """
    Interfaccia per la trascrizione e l'estrazione delle informazioni cliniche.
    Esegue la trascrizione dell'audio se necessario e aggiorna lo stato della sessione con i risultati.
    """
    # Debug: stampa le chiavi dello stato della sessione
    print(f"DEBUG: Session state keys: {list(st.session_state.keys())}")
    if hasattr(st.session_state, 'api_key'):
        print(f"DEBUG: API key presente: {bool(st.session_state.api_key)}")
    else:
        print("DEBUG: API key NON presente")
    
    # === TRASCRIZIONE ===
    # Solo se non è già stata fatta (audio)
    if st.session_state.get("audio_uploaded") and not st.session_state.transcription_done:
        with st.spinner("⏳ Trascrizione in corso..."):
            # Esegue la trascrizione audio tramite modello selezionato
            stt.speech_to_text(st.session_state.voice_text_model, st.session_state.data_filename)

            json_path = st.session_state.get("json_path")

            if not os.path.exists(json_path):
                st.error("❌ Trascrizione non trovata.")
            else:
                # Carica la trascrizione dal file json
                with open(json_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    st.session_state.transcription_text = data.get("transcription", "")
                               
                # Verifica che l'API key sia disponibile
                try:
                    api_key = st.session_state.api_key
                except AttributeError:
                    st.error("❌ Errore: API key non inizializzata. Ricarica la pagina.")
                    return
                
                # Estrae le informazioni cliniche dalla trascrizione tramite API
                st.session_state.structured_json = ttj.extract_clinical_info(
                    api_key,
                    st.session_state.transcription_text
                )

                # Copia il json strutturato per eventuali modifiche
                st.session_state.edited_json = st.session_state.structured_json.copy()
                st.session_state.transcription_done = True
                st.success("✅ Trascrizione completata!")