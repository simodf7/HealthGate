'''
[FRONTEND] input_capture.py

Modulo per la cattura e l'elaborazione dei dati di input (audio o testo).
'''


import streamlit as st
import os
import json
import ast
import sys
from codicefiscale import codicefiscale
from datetime import datetime

# Percorsi ai moduli
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

# Ottieni la directory assoluta del file corrente (streamlit_app.py)
base_dir = os.path.dirname(os.path.abspath(__file__))

AUDIO_FOLDER = os.path.abspath(os.path.join(base_dir, "..", "backend", "audio"))
TRANSCRIPTS_FOLDER = os.path.abspath(os.path.join(base_dir, "..", "backend", "transcripts"))
REPORTS_FOLDER = os.path.abspath(os.path.join(base_dir, "..", "backend", "reports"))

os.makedirs(REPORTS_FOLDER, exist_ok=True)

#st.set_page_config(page_title="Trascrizione", layout="wide")
#st.title("🩺 Trascrizione")

'''
def write_and_remove(message, timeout):
    
    # Fa scomparire un messaggio di successo dopo un certo timeout.
    
    placeholder = st.empty()  # crea un contenitore vuoto

    with placeholder:
        st.success(message)
        time.sleep(timeout)  # attende "timeout" secondi

    placeholder.empty()  # svuota il contenitore, facendo sparire il messaggio
'''

def data_insert():
    # === SELEZIONE MODALITÀ ===
    data_mode = st.radio(
        "Scegli la modalità:",
        ["🎙️ Registra dati", "📁 Carica audio", "🖊️ Trascrivi i sintomi"],
        horizontal=True
    )
    
    # Dati audio o testuali
    inserted_data = None
    
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

    if inserted_data and not st.session_state.get("data_path"):

        os.makedirs(AUDIO_FOLDER, exist_ok=True)
        os.makedirs(TRANSCRIPTS_FOLDER, exist_ok=True)
          
        # Svuota lo stato precedente per sicurezza
        st.session_state.data_uploaded = False
        st.session_state.transcription_done = False
        # Genera nome file con timestamp ed estensione appropriata
        timestamp = datetime.now().strftime('%Y-%m-%dT%H-%M-%S')
        # Crea entrambi i nomi file dallo stesso timestamp
        data_filename = f"{timestamp}{file_extension}"
        json_filename = f"{timestamp}.json"
        # Crea entrambi i percorsi completi
        data_path = os.path.join(AUDIO_FOLDER, data_filename)
        json_path = os.path.join(TRANSCRIPTS_FOLDER, json_filename)

         # Salva il file dati / testo
        try:
            with open(data_path, "wb") as f:
                f.write(inserted_data.getvalue())
            st.session_state.data_path = data_path
            st.session_state.json_path = json_path 
            st.session_state.data_filename = data_filename
            st.session_state.data_uploaded = True
            st.session_state.paths_set = True
                
            # Mostra informazioni sul file
            if data_mode == "📁 Carica audio":
                st.success(f"✅ File '{inserted_data.name}' caricato correttamente!")
            elif data_mode == "🎙️ Registra dati":
                st.success("✅ Registrazione salvata correttamente!")
            else:
                st.success("✅ Testo inserito correttamente!")
            
            # === BOTTONE PER PROCEDERE ===
            st.markdown('<div class="proceed-button">', unsafe_allow_html=True)
            if st.button("🚀 Procedi con la trascrizione", use_container_width=True):
                print_debug("Utente ha cliccato 'Procedi con la trascrizione' - passaggio a view 'rec'")
                st.session_state.view = "rec"

            st.markdown('</div>', unsafe_allow_html=True)
                
        except Exception as e:
            st.error(f"❌ Errore nel salvataggio dei dati: {e}")

def interface():
    #PER API , DA COMMENTARE SE NON SI USA
    # Debug per controllare la session state

    print(f"DEBUG: Session state keys: {list(st.session_state.keys())}")
    if hasattr(st.session_state, 'api_key'):
        print(f"DEBUG: API key presente: {bool(st.session_state.api_key)}")
    else:
        print("DEBUG: API key NON presente")
    # === TRASCRIZIONE ===
    if st.session_state.get("audio_uploaded") and not st.session_state.transcription_done:
        with st.spinner("⏳ Trascrizione in corso..."):
            # transcripts_path = os.path.join(TRANSCRIPTS_FOLDER, data_filename)
            # st.session_state.transcripts_path = transcripts_path
            # stt.speech_to_text(st.session_state.voice_text_model, st.session_state.transcripts_path)
            stt.speech_to_text(st.session_state.voice_text_model, st.session_state.data_filename)

            # json_filename = os.path.basename(st.session_state.audio_path).replace(".wav", ".json")
            # json_path = os.path.join(TRANSCRIPTS_FOLDER, json_filename)
            # st.session_state.json_path = json_path
            # with open(json_path, "r", encoding="utf-8") as f:
                # data = json.load(f)
                # st.write("Contenuto JSON:", data)  # Per debug in Streamlit
            json_path = st.session_state.get("json_path")

            if not os.path.exists(json_path):
                st.error("❌ Trascrizione non trovata.")
            else:
                with open(json_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    st.session_state.transcription_text = data.get("transcription", "")
                
                # Per LLM locale!
                '''
                st.session_state.structured_json = ttj.extract_clinical_info(
                    st.session_state.llm_model,
                    st.session_state.llm_tokenizer,
                    st.session_state.llm_device,
                    st.session_state.transcription_text
                )
                '''
                # Per LLM remoto!
                               
                # Verifica che l'API key sia disponibile
                try:
                    api_key = st.session_state.api_key
                except AttributeError:
                    st.error("❌ Errore: API key non inizializzata. Ricarica la pagina.")
                    return
                
                # Per API di Google AI Studio!
                st.session_state.structured_json = ttj.extract_clinical_info(
                    api_key,
                    st.session_state.transcription_text
                )

                st.session_state.edited_json = st.session_state.structured_json.copy()
                st.session_state.transcription_done = True
                st.success("✅ Trascrizione completata!")

    # === MODIFICA JSON ===
    if st.session_state.structured_json:
        # st.subheader("✏️ Modifica dati strutturati")
        st.subheader("🪪 Verifica i dati")

        '''
        # VECCHIA VISUALIZZAZIONE
        col1, col2, col3 = st.columns(3, gap="small", vertical_alignment="top", border=False)

        columns = [col1, col2, col3]  # Lista delle colonne

        for i, key in enumerate(st.session_state.structured_json.keys()):
            default_val = st.session_state.edited_json.get(key, "")
            col = columns[i % 3]
            
            with col:
                if isinstance(default_val, (dict, list)):
                    pretty_json = json.dumps(default_val, indent=2, ensure_ascii=False)
                    user_input = st.text_area(f"{key} (JSON):", value=pretty_json, height=200, key=f"field_{key}")
                    try:
                        st.session_state.edited_json[key] = json.loads(user_input)
                    except json.JSONDecodeError:
                        st.error(f"⚠️ Errore nel formato JSON per il campo: {key}")
                else:
                    new_val = st.text_input(f"{key}:", value=str(default_val), key=f"field_{key}")
                    st.session_state.edited_json[key] = new_val.strip()
        '''

        # === PANNELLO MODIFICA DATI ===
        dc.data_scheme(st.session_state.edited_json)
        
        # === CALCOLA CODICE FISCALE ===
        if st.button("Calcola Codice Fiscale"):
            with st.spinner("⏳ Calcolo in corso..."):
                # I valori dei widget sono salvati nel session state con il path completo
                required_keys = [
                    "dati_paziente.cognome_nome", 
                    "dati_paziente.sesso", 
                    "dati_paziente.luogo_nascita", 
                    "dati_paziente.data_nascita"
                ]
                
                # Verifica che tutti i campi richiesti siano compilati nel session state
                missing_fields = []
                for key in required_keys:
                    value = st.session_state.get(key, "")
                    if not str(value).strip():
                        missing_fields.append(key.split(".")[-1])
                
                if missing_fields:
                    st.error(f"❌ Campi mancanti: {', '.join(missing_fields)}")
                    return

                try:
                    # Recupera i valori dal session state usando le chiavi complete
                    cognome_nome = str(st.session_state.get("dati_paziente.cognome_nome", "")).strip()
                    sesso_input = st.session_state.get("dati_paziente.sesso", "").upper()
                    luogo_nascita = str(st.session_state.get("dati_paziente.luogo_nascita", "")).strip()
                    data_nascita = str(st.session_state.get("dati_paziente.data_nascita", "")).strip()
                    
                    #st.write("DEBUG: Valore di sesso dal widget selectbox:", sesso_input)
                    
                    # Gestisci meglio la divisione cognome/nome
                    parti = cognome_nome.split()
                    if len(parti) >= 2:
                        cognome = parti[0]
                        nome = " ".join(parti[1:])  # In caso di nomi composti
                    else:
                        st.error("❌ Inserire cognome e nome separati da spazio")
                        return                    # Verifica che il sesso sia M o F (richiesto dalla libreria codicefiscale)
                    if sesso_input not in ["M", "F"]:
                        st.error("❌ Seleziona il sesso (M o F) dal menu a tendina")
                        return
                        
                    cf = codicefiscale.encode(
                        lastname=cognome,
                        firstname=nome,
                        gender=sesso_input,  # Usa direttamente M o F
                        birthdate=data_nascita,
                        birthplace=luogo_nascita
                    )
                    
                    st.session_state.edited_json["codice_fiscale"] = cf
                    st.success(f"✅ Codice Fiscale generato: {cf}")
                    
                except Exception as e:
                    st.error(f"❌ Errore nel calcolo del codice fiscale: {e}")
                    print(f"Debug errore CF: {e}")  # Per debug

        '''
        if st.button("Calcola Codice Fiscale"):
            with st.spinner("⏳ Calcolo in corso..."):
                data = st.session_state.edited_json
                required = ["Nome", "Cognome", "Data di nascita", "Sesso", "Luogo di nascita"]
                if all(data.get(f) for f in required):
                    try:
                        cf = codicefiscale.encode(
                            lastname=data["Cognome"],
                            firstname=data["Nome"],
                            gender=data["Sesso"],
                            birthdate=data["Data di nascita"],
                            birthplace=data["Luogo di nascita"]
                        )
                        st.session_state.edited_json["Codice Fiscale"] = cf
                        st.session_state["field_Codice Fiscale"] = cf  # Imposta per il rerun
                        st.success(f"✅ Codice Fiscale generato: {cf}")
                        st.experimental_rerun()  # 🔁 Forza aggiornamento widget
                    except Exception as e:
                        st.warning(f"⚠️ Errore nel calcolo: {e}")                else:
                    st.error("❌ Compila tutti i campi richiesti per il codice fiscale.")
        '''

        # === SALVA SU DB + PDF ===
        if st.button("Salva modifiche"):
            st.session_state.structured_json = st.session_state.edited_json.copy()
            st.success("✅ Modifiche salvate!")

            with st.spinner("⏳ Salvataggio e generazione PDF in corso..."):
                final_data = st.session_state.edited_json
                
                # DEBUG: Stampa la tupla che verrà caricata su MongoDB
                print("DEBUG: Dati che verranno salvati su MongoDB:")
                print(json.dumps(final_data, indent=2, ensure_ascii=False))
                
                try:
                    sd.insert_patient_data(final_data)
                    st.success("✅ Dati salvati su MongoDB!")

                    cf = final_data.get("codice_fiscale", "unknown")
                    print(f"DEBUG: Codice fiscale: {cf}")
                    date = sd.datetime.now().strftime('%Y-%m-%dT%H-%M-%S')
                    
                    # DEBUG: Verifica cosa restituisce get_patient_history
                    records = sd.get_patient_history(cf)
                    print(f"DEBUG: Records trovati per il paziente {cf}: {len(records) if records else 0}")


                    # Prepara i dati per il PDF (usa sempre i dati correnti)
                    dati_per_pdf = {
                        "timestamp": sd.datetime.now().strftime('%Y-%m-%dT%H-%M-%S'),
                        "data": final_data  # Usa i dati appena salvati
                    }

                    report_filename = f"{cf}_{date}_report.pdf"
                    # Usa os.path.join per garantire separatori corretti e path assoluto
                    report_path = os.path.abspath(os.path.normpath(os.path.join(REPORTS_FOLDER, report_filename)))
                    
                    # # DEBUG: Verifica percorsi e directory
                    # print(f"DEBUG: REPORTS_FOLDER: {REPORTS_FOLDER}")
                    # print(f"DEBUG: report_filename: {report_filename}")
                    # print(f"DEBUG: report_path: {report_path}")
                    # print(f"DEBUG: report_path con forward slash: {report_path.replace(os.sep, '/')}")
                    # print(f"DEBUG: Directory reports esiste: {os.path.exists(REPORTS_FOLDER)}")
                    
                    # # Assicurati che la directory reports esista
                    # os.makedirs(REPORTS_FOLDER, exist_ok=True)
                    # print(f"DEBUG: Directory reports dopo makedirs: {os.path.exists(REPORTS_FOLDER)}")
                    
                    # # Verifica anche che la directory padre del file esista
                    # parent_dir = os.path.dirname(report_path)
                    # print(f"DEBUG: Parent directory: {parent_dir}")
                    # print(f"DEBUG: Parent directory esiste: {os.path.exists(parent_dir)}")
                    # os.makedirs(parent_dir, exist_ok=True)
                    
                    
                    # Genera sempre il PDF con i dati correnti
                    print(f"DEBUG: Chiamando pg.crea_report_medico con filename: {report_path}")
                    # try:
                        
                    #     print("DEBUG: pg.crea_report_medico completato senza errori")
                    # except Exception as pdf_error:
                    #     print(f"DEBUG: Errore specifico in pg.crea_report_medico: {pdf_error}")
                    #     # Prova con forward slash
                    #     report_path_unix = report_path.replace('\\', '/')
                    #     print(f"DEBUG: Tentativo con path unix: {report_path_unix}")
                    #     pg.crea_report_medico(dati_per_pdf, filename=report_path_unix)

                    risultato_pdf = pg.crea_report_medico(dati_per_pdf, filename=report_path)

                    if risultato_pdf and risultato_pdf.get("success"):
                        st.success("✅ Report PDF generato correttamente!")
                        print(f"DEBUG: PDF creato con successo in: {risultato_pdf.get('pdf')}")

                        with open(report_path, "rb") as f:
                            st.download_button(
                                label="Scarica Report PDF",
                                data=f.read(),
                                file_name=os.path.basename(report_path), # Usa solo il nome del file, non il percorso completo
                                mime="application/pdf",
                                key="download_pdf_button"
                            )
                    else: # Mostra un errore all'utente!
                        error_message = risultato_pdf.get('error', 'Errore sconosciuto durante la generazione del PDF.')
                        st.error(f"❌ Impossibile generare il PDF: {error_message}")
                        print(f"DEBUG: PDF non creato. Errore: {error_message}") 
                        

                    # Messaggio informativo sui record precedenti
                    if records:
                        if len(records)>1:
                            st.info(f"ℹ️ Trovati {len(records)-1} record precedenti per questo paziente")
                    else:
                        st.info("ℹ️ Primo record per questo paziente - PDF generato con i dati correnti")
                except Exception as e:
                    st.error(f"❌ Errore durante il salvataggio o la generazione del PDF: {e}")

                finally:
                # PULIZIA DEI FILE INTERMEDI 
                    
                    # Controlla che il path esista e non sia vuoto prima di cancellare
                    if st.session_state.audio_path and os.path.exists(st.session_state.audio_path):
                        audio_path = st.session_state.get("audio_path")
                        os.remove(st.session_state.audio_path)
                        st.session_state.audio_path = "" # Resetta subito il path
                      # Stesso controllo per il file JSON
                    if st.session_state.json_path and os.path.exists(st.session_state.json_path):
                        json_path = st.session_state.get("json_path")
                        os.remove(st.session_state.json_path)
                        st.session_state.json_path = "" # Resetta subito il path

                    # Pulisci file audio
                    #print(f"DEBUG: Audio da eliminare: {audio_path}")
                    if audio_path and os.path.exists(audio_path):
                        try:
                            os.remove(audio_path)
                            print(f"File audio eliminato: {audio_path}")
                        except OSError as e:
                            print(f"Errore eliminazione file audio: {e}")

                    # Pulisci file di trascrizione
                    
                    #print(f"DEBUG: JSON da eliminare: {json_path}")
                    if json_path and os.path.exists(json_path):
                        try:
                            os.remove(json_path)
                            print(f"File JSON eliminato: {json_path}")
                        except OSError as e:
                            print(f"Errore eliminazione file JSON: {e}")

                    # 5. RESET DELLO STATO PER PREPARARE L'APP A UNA NUOVA TRASCRIZIONE
                    # Questo è fondamentale per evitare comportamenti imprevisti.
                    keys_to_reset = [
                        'audio_uploaded', 'transcription_done', 'structured_json', 'edited_json', 
                        'audio_path', 'json_path', 'data_filename', 'transcription_text'
                    ]
                    for key in keys_to_reset:
                        if key in st.session_state:
                            del st.session_state[key]
                    
                    st.info("ℹ️ Processo completato. Ricarica la pagina o carica un nuovo audio per iniziare.")