"""
[FRONTEND] operator_ui.py

Modulo per la schermata relativa all'operatore - Ricerca e gestione report.
"""

import streamlit as st
import pandas as pd
from datetime import datetime
import os
import requests
from config_css import CSS_STYLE, PAGE_ICON, initialize_session_state, logout_form
from config import URL_GATEWAY

# --- CONFIGURAZIONE PERCORSI ---
base_dir = os.path.dirname(os.path.abspath(__file__))

AUDIO_FOLDER = os.path.abspath(os.path.join(base_dir, "..", "backend", "audio"))
TRANSCRIPTS_FOLDER = os.path.abspath(os.path.join(base_dir, "..", "backend", "transcripts"))
REPORTS_FOLDER = os.path.abspath(os.path.join(base_dir, "..", "backend", "reports"))

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@st.cache_data(ttl=300)  # Cache di 5 minuti
def load_all_data():
    """Carica tutti i record dal database tramite API Gateway."""
    try:
        # Recupera il token JWT dalla sessione

        headers = {
            "Authorization": f"Bearer {st.session_state.token}",
            "Content-Type": "application/json"
        }

        # Chiamata all'API Gateway per ottenere tutti i report
        response = requests.get(f"{URL_GATEWAY}/reports", headers=headers)
        
        if response.status_code == 200:
            reports_data = response.json()
            
            # Converti i dati in DataFrame
            if isinstance(reports_data, list) and len(reports_data) > 0:
                # Normalizza i dati per gestire diverse strutture
                normalized_data = []
                for report in reports_data:
                    # Gestisci diversi formati di ID
                    record_id = report.get('_id', {}).get('$oid', '') if isinstance(report.get('_id'), dict) else report.get('_id', '')
                    
                    normalized_report = {
                        'record_id': str(record_id),
                        'patient_id': report.get('patient_id', ''),
                        'firstname': report.get('firstname', ''),
                        'lastname': report.get('lastname', ''),
                        'social_sec_number': report.get('social_sec_number', ''),
                        'date': pd.to_datetime(report.get('date', '')),
                        'sintomi': report.get('sintomi', ''),
                        'diagnosi': report.get('diagnosi', ''),
                        'trattamento': report.get('trattamento', ''),
                        'created_at': pd.to_datetime(report.get('created_at', ''))
                    }
                    normalized_data.append(normalized_report)
                
                df = pd.DataFrame(normalized_data)
                return df
            else:
                st.info("Nessun report trovato nel database.")
                return pd.DataFrame()
        else:
            st.error(f"Errore nel caricamento dei dati: {response.status_code} - {response.text}")
            return pd.DataFrame()

    except requests.exceptions.ConnectionError:
        st.error("Impossibile connettersi all'API Gateway. Verifica che il servizio sia in esecuzione.")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Errore durante il caricamento dei dati: {str(e)}")
        return pd.DataFrame()


@st.cache_data(ttl=60)
def get_record_by_id(record_id):
    """Recupera un singolo record dal database."""
    try:

        headers = {
            "Authorization": f"Bearer {st.session_state.token}",
            "Content-Type": "application/json"
        }

        response = requests.get(f"{URL_GATEWAY}/report/{record_id}", headers=headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Errore nel recupero del record: {response.status_code}")
            return None

    except Exception as e:
        st.error(f"Errore durante il recupero del record: {str(e)}")
        return None

def generate_pdf_for_report(report_id):
    """Genera il PDF per un report specifico."""
    try:
    

        headers = {
            "Authorization": f"Bearer {st.session_state.token}",
            "Content-Type": "application/json"
        }

        response = requests.get(f"{URL_GATEWAY}/report/pdf/{report_id}", headers=headers)
        
        if response.status_code == 200:
            # Estrai il filename dall'header Content-Disposition se presente
            content_disposition = response.headers.get('Content-Disposition', '')
            if 'filename=' in content_disposition:
                filename = content_disposition.split('filename=')[1].strip('"')
            else:
                filename = f"report_{report_id}.pdf"
            
            return response.content, filename
        else:
            st.error(f"Errore nella generazione del PDF: {response.status_code}")
            return None, None

    except Exception as e:
        st.error(f"Errore durante la generazione del PDF: {str(e)}")
        return None, None

def render_pagination_control(total_pages):
    """Crea e gestisce un controllo di paginazione personalizzato."""
    
    st.session_state.current_page = min(st.session_state.current_page, total_pages)
    st.session_state.current_page = max(1, st.session_state.current_page)

    col1, col2, col3, col4, col5 = st.columns([1.5, 1.5, 2, 1.5, 1.5])

    with col1:
        if st.button("<< Inizio", use_container_width=True, disabled=(st.session_state.current_page == 1), type="primary"):
            st.session_state.current_page = 1
            st.rerun()
    with col2:
        if st.button("< Prec.", use_container_width=True, disabled=(st.session_state.current_page == 1), type="primary"):
            st.session_state.current_page -= 1
            st.rerun()
    with col3:
        st.markdown(
            f"<p style='text-align: center; font-size: 1.1em; margin-top: 0.4rem;'>"
            f"Pagina <b>{st.session_state.current_page}</b> di {total_pages}</p>",
            unsafe_allow_html=True
        )
    with col4:
        if st.button("Succ. >", use_container_width=True, disabled=(st.session_state.current_page == total_pages), type="primary"):
            st.session_state.current_page += 1
            st.rerun()
    with col5:
        if st.button("Fine >>", use_container_width=True, disabled=(st.session_state.current_page == total_pages), type="primary"):
            st.session_state.current_page = total_pages
            st.rerun()

    return st.session_state.current_page

def render_data_filter_section(df):
    """Renderizza la sezione di ricerca, filtro e gestione dei record."""
    
    col1, col2 = st.columns(2)
    with col1:
        search_term = st.text_input("Cerca Paziente (Nome, Cognome o SSN):", help="Ricerca non sensibile alle maiuscole.")
    with col2:
        min_date, max_date = (
            df['date'].min().date(),
            df['date'].max().date()
        ) if not df['date'].isnull().all() and len(df) > 0 else (
            datetime.today().date(),
            datetime.today().date()
        )
        date_range = st.date_input("Filtra report per data:",
            (min_date, max_date),
            min_value=min_date,
            max_value=max_date,
            format="DD/MM/YYYY")

    st.divider()
    filtered_reports = df.copy()
    
    # Filtro per intervallo di date
    if len(date_range) == 2 and len(filtered_reports) > 0:
        start_date = pd.to_datetime(date_range[0])
        end_date = pd.to_datetime(date_range[1]).replace(hour=23, minute=59, second=59)
        filtered_reports = filtered_reports[
            filtered_reports['date'].between(start_date, end_date)
        ]
    
    if len(filtered_reports) > 0:
        patient_ids = filtered_reports['social_sec_number'].dropna().unique()
    else:
        patient_ids = []

    # Ricerca per nome, cognome o SSN
    if search_term and len(filtered_reports) > 0:
        matching_patients = filtered_reports[
            filtered_reports['firstname'].str.contains(search_term, case=False, na=False) |
            filtered_reports['lastname'].str.contains(search_term, case=False, na=False) |
            filtered_reports['social_sec_number'].str.contains(search_term, case=False, na=False)
        ]['social_sec_number'].unique()
        patient_ids = [pid for pid in patient_ids if pid in matching_patients]

    st.write(f"**Trovati {len(patient_ids)} pazienti che corrispondono ai criteri di ricerca.**")

    if len(patient_ids) > 0:
        patient_map_df = filtered_reports[filtered_reports['social_sec_number'].isin(patient_ids)][
            ['social_sec_number', 'firstname', 'lastname']
        ].drop_duplicates()
        sorted_patient_map = patient_map_df.sort_values(['lastname', 'firstname'])
        sorted_patient_ids = sorted_patient_map['social_sec_number'].to_numpy()

        items_per_page = 100
        total_pages = max(1, (len(sorted_patient_ids) - 1) // items_per_page + 1)
        page_number = render_pagination_control(total_pages)
        start_idx = (page_number - 1) * items_per_page
        paginated_patient_ids = sorted_patient_ids[start_idx : start_idx + items_per_page]

        for ssn in paginated_patient_ids:
            patient_reports = filtered_reports[
                filtered_reports['social_sec_number'] == ssn
            ].sort_values('date', ascending=False)
            
            patient_row = patient_reports.iloc[0]
            firstname = patient_row['firstname']
            lastname = patient_row['lastname']
            
            with st.container(border=True):
                st.markdown(f"### 👤 {firstname} {lastname}")
                st.markdown(f"**Codice Fiscale:** `{ssn}`")
                st.markdown(f"*{len(patient_reports)} report trovati con i filtri attuali.*")
                
                for _, report in patient_reports.iterrows():
                    report_date = report.get('date').strftime('%d/%m/%Y') if pd.notna(report.get('date')) else 'Data non disponibile'
                    report_id = report['record_id']
                    
                    with st.expander(f"**Report del {report_date}**"):
                        col1, col2, col3, col4 = st.columns([2, 2, 2, 2])
                        with col1:
                            st.markdown(f"**Data:** {report_date}")
                        with col2:
                            symptoms = report.get('sintomi', 'Nessuno')
                            st.markdown(f"**Sintomi:** {symptoms}")
                        with col3:
                            diagnosis = report.get('diagnosi', 'N/A')
                            st.markdown(f"**Diagnosi:** {diagnosis}")
                        with col4:
                            treatment = report.get('trattamento', 'N/A')
                            st.markdown(f"**Trattamento:** {treatment}")
                        
                        # Bottone PDF
                        if st.button("📄 Genera PDF", key=f"pdf_{report_id}", use_container_width=True, type="primary"):
                            with st.spinner("Generazione PDF in corso..."):
                                pdf_content, pdf_filename = generate_pdf_for_report(report_id)
                                
                                if pdf_content and pdf_filename:
                                    col1, col2 = st.columns([9, 1], gap="medium")
                                    
                                    with col1:
                                        # Visualizza il PDF direttamente in Streamlit
                                        st.pdf(pdf_content, height=350)
                                    
                                    with col2:
                                        # Bottone per scaricare il PDF
                                        st.download_button(
                                            label="📩 Scarica PDF",
                                            data=pdf_content,
                                            file_name=pdf_filename,
                                            mime="application/pdf",
                                            key=f"download_{report_id}"
                                        )
                                else:
                                    st.error("Impossibile generare il PDF per questo report.")
    else:
        st.info("Nessun paziente corrisponde ai criteri di ricerca.")



def render_query_results(df):
    """Mostra i risultati di una query in formato leggibile, senza filtri o ricerca."""

    if df is None or len(df) == 0:
        st.info("Nessun risultato trovato per la query eseguita.")
        return

    '''
    # Verifica che le colonne principali esistano
    required_columns = ['record_id', 'firstname', 'lastname', 'social_sec_number', 'date']
    for col in required_columns:
        if col not in df.columns:
            st.error(f"Manca la colonna obbligatoria '{col}' nel DataFrame.")
            return
    ''' 

    st.markdown("## 🩺 Risultati")
    st.write(f"**Totale Report trovati:** {len(df)}")

   # Ordina i report per data (dal più recente)
    df = df.sort_values('date', ascending=False)

    # Prendi i dati anagrafici dal primo record
    patient_row = df.iloc[0]
    ssn = patient_row['social_sec_number']

    # Mostra intestazione del paziente
    with st.container(border=True):
        st.markdown(f"**Codice Fiscale:** `{ssn}`")


   # Cicla su ogni report
    for _, report in df.iterrows():
        report_date = (
            report.get('date').strftime('%d/%m/%Y')
            if pd.notna(report.get('date')) else 'Data non disponibile'
        )
        report_id = report['id']
        ssn = report["social_sec_number"]

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

            # --- Riquadro azioni PDF + Modifica ---
            with st.container():
                col_pdf, col_edit = st.columns([1, 1])

                # Pulsante PDF
                pdf_url = f"{URL_GATEWAY}/report/pdf/{report_id}"
                headers = {"Authorization": f"Bearer {st.session_state.token}"}
                try:
                    pdf_response = requests.get(pdf_url, headers=headers)
                    if pdf_response.status_code == 200:
                        pdf_filename = f"Report_Completo_{ssn}_{datetime.now().strftime('%Y%m%d')}.pdf"
                        with col_pdf:
                            st.download_button(
                                label="📄 Scarica PDF",
                                data=pdf_response.content,
                                file_name=pdf_filename,
                                mime="application/pdf",
                                key=f"download_{report_id}"
                            )
                    elif pdf_response.status_code == 404:
                        st.warning("⚠️ Nessun report trovato per questo codice fiscale.")
                    else:
                        st.error(f"❌ Errore generazione PDF: {pdf_response.status_code}")
                except Exception as e:
                    st.error(f"❌ Errore durante la generazione del PDF: {e}")

                # Pulsante Modifica + form inline
                # Pulsante Modifica + form inline senza usare st.form
                with col_edit:
                    if st.button("✏️ Modifica report", key=f"edit_{report_id}"):
                        st.session_state[f"edit_report_{report_id}"] = True

                    if st.session_state.get(f"edit_report_{report_id}", False):
                        # Mostra campi inline direttamente sotto il pulsante
                        diagnosi_input = st.text_area(
                            "Diagnosi",
                            value=report.get("diagnosi", ""),
                            height=100,
                            key=f"diagnosi_{report_id}"
                        )
                        trattamento_input = st.text_area(
                            "Trattamento",
                            value=report.get("trattamento", ""),
                            height=100,
                            key=f"trattamento_{report_id}"
                        )
                        if st.button("💾 Salva modifiche", key=f"save_{report_id}"):
                            payload = {
                                "diagnosi": diagnosi_input,
                                "trattamento": trattamento_input
                            }
                            response = requests.put(
                                f"{URL_GATEWAY}/report/{report_id}",
                                headers={"Authorization": f"Bearer {st.session_state.token}"},
                                json=payload
                            )
                            if response.status_code == 200:
                                st.success("✅ Modifiche salvate con successo!")
                                st.session_state[f"edit_report_{report_id}"] = False
                                st.experimental_rerun()
                            else:
                                st.error(f"❌ Errore nel salvataggio: {response.status_code}")







def interface():
    # Configurazione della pagina Streamlit
    st.set_page_config(
        page_title="Ricerca report", 
        layout="wide",
        page_icon=PAGE_ICON,
        initial_sidebar_state="collapsed"
    )

    st.markdown(CSS_STYLE, unsafe_allow_html=True)

    # Gestione toast per successo registrazione/login
    if st.session_state.operator_login_success:
        st.toast(f"Rieccoti, {st.session_state.firstname} {st.session_state.lastname}!", icon="✅")
        st.session_state.operator_login_success = False  # Resetto il FLAG

    # === BARRA SUPERIORE ===
    col1, col2 = st.columns([5, 2])
    
    with col1:
        st.header("🪪 Ricerca report")
    with col2:
        subcol1, subcol2 = st.columns([2, 1])
        with subcol1:
            st.markdown(f"Ciao, **{st.session_state.firstname.upper()} {st.session_state.lastname.upper()}**!")
        with subcol2:
            if st.button("🚪 Logout", type="primary"):
                logout_form()
    
    st.divider()
    
    # Pulsante per ricaricare i dati
    col1, col2 = st.columns([4, 1])
    with col2:
        if st.button("🔄 Aggiorna dati", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
    
    '''
    df = load_all_data()
    if df.empty:
        st.warning("⚠️ Nessun dato trovato nel database.")
        return
    '''




# === LA TUA FUNZIONE INTERFACE ADATTATA ===
def alt_interface():
    st.set_page_config(
        page_title="Ricerca report", 
        layout="wide",
        page_icon="🔍",
        initial_sidebar_state="collapsed"
    )

    headers = {"Authorization": f"Bearer {st.session_state.token}"}

    # === HEADER ===
    col1, col2 = st.columns([5, 2])
    with col1:
        st.header("🪪 Ricerca report")
    with col2:
        subcol1, subcol2 = st.columns([2, 1])
        with subcol1:
            st.markdown(f"Ciao, **{st.session_state.firstname.upper()} {st.session_state.lastname.upper()}**!")
        with subcol2:
            if st.button("🚪 Logout", type="primary"):
                logout_form()

    st.divider()

    # === CAMPO DI RICERCA ===
    st.markdown("### 🔎 Ricerca per codice fiscale")
    search_text = st.text_input("Inserisci il testo da cercare:")

    # === PULSANTE PER ESEGUIRE LA QUERY ===
    if st.button("Esegui ricerca", type="primary", use_container_width=True):
        if not search_text.strip():
            st.warning("⚠️ Inserisci un valore per la ricerca.")
        else:
            with st.spinner("Eseguo la query..."):
                response = requests.get(f"{URL_GATEWAY}/reports/ssn/{search_text}", headers=headers)
                if response.status_code == 200:
                    reports = response.json()
                    logger.info(f"Reports response: {reports}")
                    df = pd.DataFrame(reports)
                    
                    if df.empty:
                        st.warning("⚠️ Nessun report disponibile per il paziente.")
                        return

                    if 'date' in df.columns:
                        df['date'] = pd.to_datetime(df['date'])
                    if 'created_at' in df.columns:
                        df['created_at'] = pd.to_datetime(df['created_at'])

                    render_query_results(df)

    # === PULSANTE PER RICARICARE I DATI (opzionale) ===
    st.divider()
    if st.button("🔄 Aggiorna dati", use_container_width=True):
        st.cache_data.clear()
        st.rerun()
