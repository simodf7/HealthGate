"""
[FRONTEND] patient.py

Modulo per la schermata relativa al paziente.
"""

import streamlit as st
import main

# === SELEZIONE MODALITÀ ===
def interface():
    # Configurazione della pagina Streamlit
    st.set_page_config(
        page_title="HealthGate - Sintomi", 
        layout="wide",
        page_icon="🚑",
        initial_sidebar_state="collapsed"
    )

    # CSS personalizzato per migliorare l'aspetto grafico
    st.markdown("""
    <style>
    .main-header {
        text-align: left;
        color: #2E86AB;
        font-size: 3rem;
        font-weight: bold;
        margin-bottom: 2rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }

    .stButton > button {
        background: #52aa8a;
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.6rem 1.5rem;
        font-size: 1.1rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }

    .stButton > button:hover {
        background: #74c3a4;
        color: #ffffff;
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0,0,0,0.3);
    }
    .home-button > button:hover {
        background: #4fa070;
    }
    .proceed-button > button:hover {
        background: #53e4ff;
    }
    </style>
    """, unsafe_allow_html=True)

    # === BARRA SUPERIORE ===
    col1, col2 = st.columns([3, 1])
    with col2:
        subcol1, subcol2 = st.columns([2, 1])
        with subcol1:
            if st.session_state.sex == "M":
                st.markdown(f"Bentornato, **{st.session_state.firstname.upper()} {st.session_state.lastname.upper()}**!")
            else:
                st.markdown(f"Bentornata, **{st.session_state.firstname.upper()} {st.session_state.lastname.upper()}**!")
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

    audio_data = None

    if input_mode == "🎙️ Registra audio":
        # === REGISTRAZIONE AUDIO ===
        audio_data = st.audio_input(st.session_state.firstname + ", registra l'audio", label_visibility="visible")
        file_extension = ".wav"
        
    elif input_mode == "📁 Carica file audio":
        # === CARICAMENTO FILE AUDIO ===
        audio_data = st.file_uploader(
            st.session_state.firstname + ", carica un file audio",
            type=["wav", "mp3", "m4a", "ogg", "flac"],
            help="Formati supportati: WAV, MP3, M4A, OGG, FLAC"
        )
        if audio_data:
            file_extension = "." + audio_data.name.split(".")[-1].lower()
    elif input_mode == "🖊️ Trascrivi sintomi":
        st.session_state.transcription_text = st.text_area(st.session_state.firstname + ", trascrivi qui i tuoi sintomi", height="content")

    if audio_data and not st.session_state.get("audio_path"):

        os.makedirs(AUDIO_FOLDER, exist_ok=True)
        os.makedirs(TRANSCRIPTS_FOLDER, exist_ok=True)

        '''
        # Genera nome file con timestamp ed estensione appropriata
        timestamp = datetime.now().strftime('%Y-%m-%dT%H-%M-%S')
        if audio_mode == "📁 Carica file audio":
            # Mantieni il nome originale del file caricato
            original_name = audio_data.name.split(".")[0]
            st.session_state.audio_filename = f"{timestamp}_{original_name}{file_extension}"
        else:
            st.session_state.audio_filename = f"{timestamp}{file_extension}"
            
        audio_path = os.path.join(AUDIO_FOLDER, st.session_state.audio_filename)
        '''
        
        
        # Svuota lo stato precedente per sicurezza
        st.session_state.audio_uploaded = False
        st.session_state.transcription_done = False
        # Genera nome file con timestamp ed estensione appropriata
        timestamp = datetime.now().strftime('%Y-%m-%dT%H-%M-%S')
        # Crea entrambi i nomi file dallo stesso timestamp
        audio_filename = f"{timestamp}{file_extension}"
        json_filename = f"{timestamp}.json"
        # Crea entrambi i percorsi completi
        audio_path = os.path.join(AUDIO_FOLDER, audio_filename)
        json_path = os.path.join(TRANSCRIPTS_FOLDER, json_filename)

            # Salva il file audio
        try:
            with open(audio_path, "wb") as f:
                f.write(audio_data.getvalue())
            st.session_state.audio_path = audio_path
            st.session_state.json_path = json_path 
            st.session_state.audio_filename = audio_filename
            st.session_state.audio_uploaded = True
            st.session_state.paths_set = True
                
            # Mostra informazioni sul file
            if audio_mode == "📁 Carica file audio":
                st.success(f"✅ File '{audio_data.name}' caricato correttamente!")
            else:
                st.success("✅ Registrazione salvata correttamente!")
                    
        except Exception as e:
            st.error(f"❌ Errore nel salvataggio dell'audio: {e}")