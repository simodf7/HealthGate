"""
[FRONTEND] operator_ui.py

Modulo per la schermata relativa all'operatore - Ricerca e gestione report.
"""

import streamlit as st
import pandas as pd
from datetime import datetime
import os
from config import CSS_STYLE, PAGE_ICON

# --- CONFIGURAZIONE PERCORSI ---
base_dir = os.path.dirname(os.path.abspath(__file__))

AUDIO_FOLDER = os.path.abspath(os.path.join(base_dir, "..", "backend", "audio"))
TRANSCRIPTS_FOLDER = os.path.abspath(os.path.join(base_dir, "..", "backend", "transcripts"))
REPORTS_FOLDER = os.path.abspath(os.path.join(base_dir, "..", "backend", "reports"))

# Inserimenti placeholder
@st.cache_data(ttl=1200)
def load_all_data():
    """Carica tutti i record - Placeholder con formato MongoDB + firstname/lastname."""
    data = [
        {
            'record_id': '1',
            'patient_id': 123456,
            'firstname': 'Mario',
            'lastname': 'Rossi',
            'social_sec_number': 'RSSMRA85T10A562S',
            'date': pd.Timestamp('2025-10-01'),
            'sintomi': 'Febbre, tosse',
            'diagnosi': 'Influenza stagionale',
            'trattamento': 'Antipiretici e riposo',
            'created_at': pd.Timestamp('2025-10-01T08:30')
        },
        {
            'record_id': '2',
            'patient_id': 123457,
            'firstname': 'Luisa',
            'lastname': 'Bianchi',
            'social_sec_number': 'BNCLSU90B02H501Y',
            'date': pd.Timestamp('2025-10-05'),
            'sintomi': 'Caduta, contusione',
            'diagnosi': 'Contusione lieve',
            'trattamento': 'Riposo e ghiaccio',
            'created_at': pd.Timestamp('2025-10-05T09:00')
        },
        {
            'record_id': '3',
            'patient_id': 123457,
            'firstname': 'Luisa',
            'lastname': 'Bianchi',
            'social_sec_number': 'BNCLSU90B02H501Y',
            'date': pd.Timestamp('2025-10-10'),
            'sintomi': 'Mal di testa intenso',
            'diagnosi': 'Emicrania acuta',
            'trattamento': 'Antidolorifici',
            'created_at': pd.Timestamp('2025-10-10T16:15')
        }
    ]
    df = pd.DataFrame(data)
    return df


@st.cache_data(ttl=60)
def get_record_by_id(record_id):
    """Recupera un singolo record - Placeholder senza DB."""
    df = load_all_data()
    record = df[df['record_id'] == record_id]
    if not record.empty:
        return record.iloc[0].to_dict()
    return None

def render_pagination_control(total_pages):
    """Crea e gestisce un controllo di paginazione personalizzato."""
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 1
    
    st.session_state.current_page = min(st.session_state.current_page, total_pages)
    st.session_state.current_page = max(1, st.session_state.current_page)

    col1, col2, col3, col4, col5 = st.columns([1.5, 1.5, 2, 1.5, 1.5])

    with col1:
        if st.button("<< Inizio", use_container_width=True, disabled=(st.session_state.current_page == 1)):
            st.session_state.current_page = 1
            st.rerun()
    with col2:
        if st.button("< Prec.", use_container_width=True, disabled=(st.session_state.current_page == 1)):
            st.session_state.current_page -= 1
            st.rerun()
    with col3:
        st.markdown(
            f"<p style='text-align: center; font-size: 1.1em; margin-top: 0.4rem;'>"
            f"Pagina <b>{st.session_state.current_page}</b> di {total_pages}</p>",
            unsafe_allow_html=True
        )
    with col4:
        if st.button("Succ. >", use_container_width=True, disabled=(st.session_state.current_page == total_pages)):
            st.session_state.current_page += 1
            st.rerun()
    with col5:
        if st.button("Fine >>", use_container_width=True, disabled=(st.session_state.current_page == total_pages)):
            st.session_state.current_page = total_pages
            st.rerun()

    return st.session_state.current_page

def render_data_filter_section(df):
    """Renderizza la sezione di ricerca, filtro e gestione dei record (formato MongoDB con firstname/lastname)."""
    
    # st.markdown("Usa i filtri per trovare record specifici.")
    # with st.expander("⬇️ Apri Pannello Filtri", expanded=True):
    col1, col2 = st.columns(2)
    with col1:
        search_term = st.text_input("Cerca Paziente (Nome, Cognome o SSN):", help="Ricerca non sensibile alle maiuscole.")
    with col2:
        min_date, max_date = (
            df['date'].min().date(),
            df['date'].max().date()
        ) if not df['date'].isnull().all() else (
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
    if len(date_range) == 2:
        start_date = pd.to_datetime(date_range[0])
        end_date = pd.to_datetime(date_range[1]).replace(hour=23, minute=59, second=59)
        filtered_reports = filtered_reports[
            filtered_reports['date'].between(start_date, end_date)
        ]
        
    patient_ids = filtered_reports['social_sec_number'].dropna().unique()

    # Ricerca per nome, cognome o SSN
    if search_term:
        matching_patients = df[
            df['firstname'].str.contains(search_term, case=False, na=False) |
            df['lastname'].str.contains(search_term, case=False, na=False) |
            df['social_sec_number'].str.contains(search_term, case=False, na=False)
        ]['social_sec_number'].unique()
        patient_ids = [pid for pid in patient_ids if pid in matching_patients]

    if len(patient_ids) > 0:
        patient_map_df = df[df['social_sec_number'].isin(patient_ids)][
            ['social_sec_number', 'firstname', 'lastname']
        ].drop_duplicates()
        sorted_patient_map = patient_map_df.sort_values(['lastname', 'firstname'])
        sorted_patient_ids = sorted_patient_map['social_sec_number'].to_numpy()
    else:
        sorted_patient_ids = []

    st.write(f"**Trovati {len(sorted_patient_ids)} pazienti che corrispondono ai criteri di ricerca.**")

    if sorted_patient_ids.any():
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
                    report_date = report.get('date').strftime('%d/%m/%Y')
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
                        if st.button("📄 Genera PDF", key=f"pdf_{report_id}", use_container_width=True):
                            with st.spinner("Generazione PDF..."):
                                full_record = get_record_by_id(str(report_id))
                                if full_record:
                                    dati_per_pdf = {"timestamp": full_record.get('date', ''), "data": full_record}
                                    ssn_pdf = full_record.get('social_sec_number', 'NO_SSN')
                                    timestamp_per_file = str(report_id)
                                    pdf_filename = f"{ssn_pdf}_{timestamp_per_file}_report.pdf"
                                    pdf_path = os.path.join(REPORTS_FOLDER, pdf_filename)
                                    pg.crea_report_medico(dati_per_pdf, filename=pdf_path)
                                    with open(pdf_path, "rb") as pdf_file:
                                        st.download_button(
                                            label="Scarica PDF",
                                            data=pdf_file.read(),
                                            file_name=pdf_filename,
                                            mime="application/pdf",
                                            key=f"download_{report_id}"
                                        )
                                else:
                                    st.error("Dati completi non trovati.")
    else:
        st.info("Nessun paziente corrisponde ai criteri di ricerca.")

def interface():
    # Configurazione della pagina Streamlit
    st.set_page_config(
        page_title="Ricerca report", 
        layout="wide",
        page_icon=PAGE_ICON,
        initial_sidebar_state="collapsed"
    )

    st.markdown(CSS_STYLE, unsafe_allow_html=True)

    """Funzione principale dell'interfaccia operatore."""
    if st.session_state.get('patient_login_success'):
        st.toast(f"Rieccoti, {st.session_state.firstname} {st.session_state.lastname}!", icon="✅")
        st.session_state.patient_login_success = False

    col1, col2 = st.columns([3, 1])
    with col1:
        st.header("🪪 Ricerca report")
    with col2:
        subcol1, subcol2 = st.columns([2, 1])
        with subcol1:
            st.markdown(f"Ciao, **{st.session_state.firstname.upper()} {st.session_state.lastname.upper()}**!")
        with subcol2:
            if st.button("Logout"):
                st.session_state.view = "home"
                st.rerun()
    
    st.divider()
    
    df = load_all_data()
    if df.empty:
        st.warning("⚠️ Nessun dato trovato. Usa i placeholder per testare l'interfaccia.")
        return

    if "pdf_to_download" not in st.session_state:
        st.session_state.pdf_to_download = None

    render_data_filter_section(df)
