"""
[FRONTEND] patient.py

Modulo per la schermata relativa al paziente.
"""

import streamlit as st
import os
from datetime import datetime
from config import CSS_STYLE, PAGE_ICON

# Definisci le cartelle per audio e trascrizioni
INPUT_FOLDER = "./frontend/input_files"
TRANSCRIPTS_FOLDER = "./frontend/transcripts"

# === SELEZIONE MODALITÀ ===
def interface():
    # Configurazione della pagina Streamlit
    st.set_page_config(
        page_title="Registrazione sintomi", 
        layout="wide",
        page_icon=PAGE_ICON,
        initial_sidebar_state="collapsed"
    )

    st.markdown(CSS_STYLE, unsafe_allow_html=True)

    if st.session_state.patient_login_success:
        st.toast(f"Rieccoti, {st.session_state.firstname} {st.session_state.lastname}!", icon="✅", duration="short")
        st.session_state.patient_login_success = False  # Resetto il FLAG

    # === BARRA SUPERIORE ===
    col1, col2 = st.columns([3, 1])

    with col1:
        st.header("🚑 Registrazione sintomi")

    with col2:
        subcol1, subcol2 = st.columns([2, 1])
        with subcol1:
            st.markdown(f"Ciao, **{st.session_state.firstname.upper()} {st.session_state.lastname.upper()}**!")
        with subcol2:
            if st.button("Logout"):
                st.session_state.view = "home"
                st.rerun()
    
    st.divider()

    input_mode = st.radio(
        "Scegli la modalità:",
        ["🎙️ Registra audio", "📁 Carica file audio", "🖊️ Trascrivi sintomi"],
        horizontal=True
    )

    input_ready = False

    if input_mode == "🎙️ Registra audio":
        # === REGISTRAZIONE AUDIO ===
        input_data = st.audio_input(st.session_state.firstname + ", registra l'audio", label_visibility="visible")
        
        if input_data:
            os.makedirs(INPUT_FOLDER, exist_ok=True)
            timestamp = datetime.now().strftime('%Y-%m-%dT%H-%M-%S')
            audio_filename = f"{timestamp}.wav"
            audio_path = os.path.join(INPUT_FOLDER, audio_filename)
            
            try:
                with open(audio_path, "wb") as f:
                    f.write(input_data.getvalue())
                st.session_state.audio_path = audio_path
                st.toast("Registrazione salvata correttamente!", icon="✅", duration="short")
                input_ready = True
            except Exception as e:
                st.error(f"❌ Errore nel salvataggio dell'audio: {e}")
        
    elif input_mode == "📁 Carica file audio":
        # === CARICAMENTO FILE AUDIO ===
        input_data = st.file_uploader(
            st.session_state.firstname + ", carica un file audio",
            type=["wav", "mp3", "m4a", "ogg", "flac"],
            help="Formati supportati: WAV, MP3, M4A, OGG, FLAC"
        )
        
        if input_data:
            os.makedirs(INPUT_FOLDER, exist_ok=True)
            file_extension = "." + input_data.name.split(".")[-1].lower()
            timestamp = datetime.now().strftime('%Y-%m-%dT%H-%M-%S')
            audio_filename = f"{timestamp}{file_extension}"
            audio_path = os.path.join(INPUT_FOLDER, audio_filename)
            
            try:
                with open(audio_path, "wb") as f:
                    f.write(input_data.getvalue())
                st.session_state.audio_path = audio_path
                st.toast(f"File '{input_data.name}' caricato correttamente!", icon="✅", duration="short")
                input_ready = True
            except Exception as e:
                st.error(f"❌ Errore nel salvataggio dell'audio: {e}")

    elif input_mode == "🖊️ Trascrivi sintomi":
        # === CARICAMENTO TESTO SCRITTO ===
        transcription_text = st.text_area(
            st.session_state.firstname + ", trascrivi qui i tuoi sintomi", 
            height="content",
            key="symptom_text_area"
        )
        
        if transcription_text and transcription_text.strip():
            st.session_state.transcription_text = transcription_text
            st.toast("Testo inserito correttamente!", icon="✅")
            input_ready = True

    # === BOTTONE PER PROCEDERE ===
    if input_ready:
            col1,col2,col3 = st.columns(3)

            with col2:
                if st.button("➡️ Procedi", use_container_width=True):
                    # Diramazione in base alla modalità di input
                    if input_mode in ["🎙️ Registra audio", "📁 Carica file audio"]:
                        st.info("🔄 Elaborazione: Whisper + LLM + RAG")
                        # Qui inserire la logica per: trascrizione audio -> elaborazione LLM -> RAG

                        with st.spinner("Procedendo con l'elaborazione..."):
                            import time
                            time.sleep(10)
                            st.success("Fatto!")
                            # Ad esempio: chiamare una funzione di processing, cambiare pagina, etc.
                    elif input_mode == "🖊️ Trascrivi sintomi":
                        st.info("🔄 Elaborazione: LLM + RAG")
                        # Qui inserire la logica per: elaborazione LLM -> RAG

                        with st.spinner("Procedendo con l'elaborazione..."):
                            import time
                            time.sleep(10)
                            st.success("Fatto!")
                            # Ad esempio: chiamare una funzione di processing, cambiare pagina, etc.