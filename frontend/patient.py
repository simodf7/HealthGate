"""
[FRONTEND] patient.py

Modulo per la schermata relativa al paziente.
"""

import streamlit as st
import main
import os
from datetime import datetime
from config import CSS_STYLE

# Definisci le cartelle per audio e trascrizioni
INPUT_FOLDER = "./input_files"
TRANSCRIPTS_FOLDER = "./transcripts"

# === SELEZIONE MODALITÀ ===
def interface():
    # Configurazione della pagina Streamlit
    st.set_page_config(
        page_title="HealthGate - Sintomi", 
        layout="wide",
        page_icon="🚑",
        initial_sidebar_state="collapsed"
    )

    st.markdown(CSS_STYLE, unsafe_allow_html=True)

    if st.session_state.patient_login_success:
        st.toast(f"Rieccoti, {st.session_state.firstname} {st.session_state.lastname}!", icon="✅")
        st.session_state.patient_login_success = False  # Resetto il FLAG

    # === BARRA SUPERIORE ===
    col1, col2 = st.columns([3, 1])
    with col2:
        subcol1, subcol2 = st.columns([2, 1])
        with subcol1:
            st.markdown(f"Ciao, **{st.session_state.firstname.upper()} {st.session_state.lastname.upper()}**!")
        with subcol2:
            if st.button("Logout"):
                st.rerun()
                main.interface()
    
    st.divider()

    input_mode = st.radio(
        "Scegli la modalità:",
        ["🎙️ Registra audio", "📁 Carica file audio", "🖊️ Trascrivi sintomi"],
        horizontal=True
    )

    input_data = None

    if input_mode == "🎙️ Registra audio":
        # === REGISTRAZIONE AUDIO ===
        input_data = st.audio_input(st.session_state.firstname + ", registra l'audio", label_visibility="visible")
        file_extension = ".wav"
        
    elif input_mode == "📁 Carica file audio":
        # === CARICAMENTO FILE AUDIO ===
        input_data = st.file_uploader(
            st.session_state.firstname + ", carica un file audio",
            type=["wav", "mp3", "m4a", "ogg", "flac"],
            help="Formati supportati: WAV, MP3, M4A, OGG, FLAC"
        )
        if input_data:
            file_extension = "." + input_data.name.split(".")[-1].lower()

    elif input_mode == "🖊️ Trascrivi sintomi":
        # === CARICAMENTO TESTO SCRITTO ===
        st.session_state.transcription_text = st.text_area(st.session_state.firstname + ", trascrivi qui i tuoi sintomi", height="content")

    if input_data and not st.session_state.get("audio_path"):

        os.makedirs(INPUT_FOLDER, exist_ok=True)
        os.makedirs(TRANSCRIPTS_FOLDER, exist_ok=True)        
        
        # Svuota lo stato precedente per sicurezza
        st.session_state.audio_uploaded = False
        st.session_state.transcription_done = False
        # Genera nome file con timestamp ed estensione appropriata
        timestamp = datetime.now().strftime('%Y-%m-%dT%H-%M-%S')
        # Crea entrambi i nomi file dallo stesso timestamp
        audio_filename = f"{timestamp}{file_extension}"
        json_filename = f"{timestamp}.json"
        # Crea entrambi i percorsi completi
        audio_path = os.path.join(INPUT_FOLDER, audio_filename)
        json_path = os.path.join(TRANSCRIPTS_FOLDER, json_filename)

            # Salva il file audio
        try:
            with open(audio_path, "wb") as f:
                f.write(input_data.getvalue())
            st.session_state.audio_path = audio_path
            st.session_state.json_path = json_path 
            st.session_state.audio_filename = audio_filename
            st.session_state.audio_uploaded = True
            st.session_state.paths_set = True
                
            # Mostra informazioni sul file
            if input_mode == "📁 Carica file audio":
                st.success(f"✅ File '{input_data.name}' caricato correttamente!")
            else:
                st.success("✅ Registrazione salvata correttamente!")
                    
        except Exception as e:
            st.error(f"❌ Errore nel salvataggio dell'audio: {e}")