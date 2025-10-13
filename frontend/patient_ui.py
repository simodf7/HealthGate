"""
[FRONTEND] patient.py
 
Modulo per la schermata relativa al paziente.
"""
 
import pandas as pd
import requests
import streamlit as st
import os
from datetime import datetime
<<<<<<< Updated upstream
from config_css import CSS_STYLE, PAGE_ICON, initialize_session_state, logout_form
from config import URL_GATEWAY
 
=======
from config import CSS_STYLE, PAGE_ICON, initialize_session_state, logout_form

>>>>>>> Stashed changes
# Definisci le cartelle per audio e trascrizioni
INPUT_FOLDER = "./input_files"
TRANSCRIPTS_FOLDER = "./transcripts"
 
# === SELEZIONE MODALITÀ ===
def symptom_interface():

    # Configurazione della pagina Streamlit
    st.set_page_config(
        page_title="Registrazione sintomi",
        layout="wide",
        page_icon=PAGE_ICON,
        initial_sidebar_state="expanded"
    )
 
    with st.sidebar:
        if st.button("🚑 Registrazione sintomi", key="symptom-inserting", type="secondary"):
            st.session_state.view = "patient-logged-symptoms"
        if st.button("🗂️ Visualizzazione report", key="report-visualizing", type="secondary"):
            st.session_state.view = "patient-logged-reports"
 
    st.markdown(CSS_STYLE, unsafe_allow_html=True)
 
    # Gestione toast per successo registrazione/login
    if st.session_state.patient_login_success:
        st.toast(f"Rieccoti, {st.session_state.firstname} {st.session_state.lastname}!", icon="✅")
        st.session_state.patient_login_success = False  # Resetto il FLAG
 

    # === BARRA SUPERIORE ===
    col1, col2 = st.columns([5, 2])
 
    with col1:
        st.header("🚑 Registrazione sintomi")
 
    with col2:
        subcol1, subcol2 = st.columns([2, 1])
        with subcol1:
            st.markdown(f"Ciao, **{st.session_state.firstname.upper()} {st.session_state.lastname.upper()}**!")
        with subcol2:
            if st.button("🚪 Logout", type="primary"):
                logout_form()
                # st.session_state.view = "home"
                # st.rerun()
   
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
            st.session_state.audio_filename = f"{timestamp}{file_extension}"
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
            if st.button("➡️ Procedi", use_container_width=True, type="primary"):
                st.info("🔄 Elaborazione in corso...")
                headers = {"Authorization": f"Bearer {st.session_state.token}"}


                try:
                    with st.spinner("Procedendo con l'elaborazione..."):

                        # === Caso AUDIO ===
                        if input_mode in ["🎙️ Registra audio", "📁 Carica file audio"]:
                            if "audio_path" not in st.session_state:
                                st.error("⚠️ Nessun file audio trovato.")
                            else:
                                audio_path = st.session_state.audio_path
                                filename = os.path.basename(audio_path)

                                # Apri il file binario per l’invio
                                with open(audio_path, "rb") as f:
                                    files = {"file": (filename, f, "audio/wav")}
                                    response = requests.post(f"{URL_GATEWAY}/diagnose", files=files, headers=headers)

                        # === Caso TESTO ===
                        elif input_mode == "🖊️ Trascrivi sintomi":
                            if "transcription_text" not in st.session_state or not st.session_state.transcription_text.strip():
                                st.error("⚠️ Inserisci del testo prima di procedere.")
                            else:
                                data = {"text": st.session_state.transcription_text}
                                response = requests.post(f"{URL_GATEWAY}/diagnose", data=data, headers=headers)

                        # === Gestione risposta ===
                        if response.status_code == 200:
                            response = response.json()
                            st.success("✅ Elaborazione completata!")
                            st.write("**Decisione**:", response["decisione"])
                            st.write("**Motivazione**:", response["motivazione"])
                            
                            if input_mode in ["🎙️ Registra audio", "📁 Carica file audio"]:
                                os.remove(st.session_state.audio_path)
                                st.toast("🧹 File audio locale eliminato", icon="🗑️")
                                del st.session_state.audio_path  # rimuove la variabile dalla sessione
                        
                        else:
                            st.error(f"❌ Errore: {response.status_code} - {response.text}")

                except Exception as e:
                    st.error(f"❌ Errore durante la chiamata all'API: {e}")
 



def reports_interface():
    # Configurazione della pagina Streamlit
    st.set_page_config(
        page_title="Visualizzazione report",
        layout="wide",
        page_icon=PAGE_ICON,
        initial_sidebar_state="expanded"
    )
<<<<<<< Updated upstream
 
=======

>>>>>>> Stashed changes
    with st.sidebar:
        if st.button("🚑 Registrazione sintomi", key="symptom-inserting", type="secondary"):
            st.session_state.view = "patient-logged-symptoms"
        if st.button("🗂️ Visualizzazione report", key="report-visualizing", type="secondary"):
            st.session_state.view = "patient-logged-reports"
 
    st.markdown(CSS_STYLE, unsafe_allow_html=True)
 
    # === BARRA SUPERIORE ===
    col1, col2 = st.columns([5, 2])
<<<<<<< Updated upstream
 
=======
>>>>>>> Stashed changes
    with col1:
        st.header("🗂️ Visualizzazione report")
 
    with col2:
        subcol1, subcol2 = st.columns([2, 1])
        with subcol1:
            st.markdown(f"Ciao, **{st.session_state.firstname.upper()} {st.session_state.lastname.upper()}**!")
        with subcol2:
            if st.button("🚪 Logout", type="primary"):
                logout_form()
 
    st.divider()
<<<<<<< Updated upstream
 
    patient_id = st.session_state.id
    headers = {"Authorization": f"Bearer {st.session_state.token}"}
    response = requests.get(f"{URL_GATEWAY}/reports/id/{patient_id}", headers=headers)

    if response.status_code == 200:
        reports = response.json()
        df = pd.DataFrame(reports)
        
        if df.empty:
            st.warning("⚠️ Nessun report disponibile.")
            return

        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'])
        if 'created_at' in df.columns:
            df['created_at'] = pd.to_datetime(df['created_at'])


        st.dataframe(df)

        # --- Filtra e mostra tutti i report del paziente loggato ---
        ssn = st.session_state.social_sec_number

        if not ssn:
            st.warning("⚠️ Codice fiscale non disponibile.")
            return

        patient_reports = df[df['social_sec_number'] == ssn].sort_values('date', ascending=False)
        if patient_reports.empty:
            st.info("Nessun report trovato per te.")
            return

        patient_row = patient_reports.iloc[0]
        firstname = patient_row['firstname']
        lastname = patient_row['lastname']

        st.markdown(f"### 👤 {firstname} {lastname}")
        st.markdown(f"**Codice Fiscale:** `{ssn}`")
        st.markdown(f"*{len(patient_reports)} report trovati.*")
        st.divider()

        for _, report in patient_reports.iterrows():
            report_date = report.get('date').strftime('%d/%m/%Y')
            report_id = report['record_id']

            with st.expander(f"**Report del {report_date}**"):
                col1, col2, col3, col4 = st.columns([2, 2, 2, 2])
                with col1:
                    st.markdown(f"**Data:** {report_date}")
                with col2:
                    st.markdown(f"**Sintomi:** {report.get('sintomi', 'Nessuno')}")
                with col3:
                    st.markdown(f"**Diagnosi:** {report.get('diagnosi', 'N/A')}")
                with col4:
                    st.markdown(f"**Trattamento:** {report.get('trattamento', 'N/A')}")

                if st.button("📄 Genera PDF", key=f"pdf_{report_id}", use_container_width=True, type="primary"):
                    pdf_path = "microservices/report-management/pdf/20251006_133030_Campanella_Ale-Report.pdf"
                    pdf_filename = os.path.basename(pdf_path)
                    st.pdf(pdf_path, height=350)

                    with open(pdf_path, "rb") as pdf_file:
                        st.download_button(
                            label="📩 Scarica PDF",
                            data=pdf_file.read(),
                            file_name=pdf_filename,
                            mime="application/pdf",
                            key=f"download_{report_id}"
                        )
    else:
        st.error(f"Errore nel recupero report: {response.status_code}")
=======

    # --- Carica i dati (placeholder) ---
    from frontend.operator_ui import load_all_data  # riutilizzo della funzione placeholder (sposta in config)
    df = load_all_data()
    
    if df.empty:
        st.warning("⚠️ Nessun report disponibile.")
        return

    # --- Filtra e mostra tutti i report del paziente loggato ---
    ssn = st.session_state.social_sec_number

    if not ssn:
        st.warning("⚠️ Codice fiscale non disponibile.")
        return

    patient_reports = df[df['social_sec_number'] == ssn].sort_values('date', ascending=False)
    if patient_reports.empty:
        st.info("Nessun report trovato per te.")
        return

    patient_row = patient_reports.iloc[0]
    firstname = patient_row['firstname']
    lastname = patient_row['lastname']
    
    st.markdown(f"### 👤 {firstname} {lastname}")
    st.markdown(f"**Codice Fiscale:** `{ssn}`")
    st.markdown(f"*{len(patient_reports)} report trovati.*")
    st.divider()

    for _, report in patient_reports.iterrows():
        report_date = report.get('date').strftime('%d/%m/%Y')
        report_id = report['record_id']
        
        with st.expander(f"**Report del {report_date}**"):
            col1, col2, col3, col4 = st.columns([2, 2, 2, 2])
            with col1:
                st.markdown(f"**Data:** {report_date}")
            with col2:
                st.markdown(f"**Sintomi:** {report.get('sintomi', 'Nessuno')}")
            with col3:
                st.markdown(f"**Diagnosi:** {report.get('diagnosi', 'N/A')}")
            with col4:
                st.markdown(f"**Trattamento:** {report.get('trattamento', 'N/A')}")

            # Bottone PDF (placeholder)
            if st.button("📄 Genera PDF", key=f"pdf_{report_id}", use_container_width=True, type="primary"):
                pdf_path = "microservices/report-management/pdf/20251006_133030_Campanella_Ale-Report.pdf"
                pdf_filename = os.path.basename(pdf_path)
                st.pdf(pdf_path, height=350)
                
                with open(pdf_path, "rb") as pdf_file:
                    st.download_button(
                        label="📩 Scarica PDF",
                        data=pdf_file.read(),
                        file_name=pdf_filename,
                        mime="application/pdf",
                        key=f"download_{report_id}"
                    )
>>>>>>> Stashed changes
