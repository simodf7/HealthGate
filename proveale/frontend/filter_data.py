"""
[FRONTEND] filter_data.py

Modulo per la gestione, visualizzazione e analisi dei dati dei pazienti.
"""


import streamlit as st
import pandas as pd
from pyecharts import options as opts
from pyecharts.charts import Bar, Pie, HeatMap, Boxplot, Line, Grid
from streamlit_echarts import st_pyecharts
import folium
from streamlit_folium import st_folium
from pyecharts.commons.utils import JsCode
from datetime import datetime
import os
import sys
import branca.colormap as cm
from bson.objectid import ObjectId

# --- CONFIGURAZIONE PERCORSI ---
# Ottieni il path assoluto del progetto (cartella superiore)
base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
backend_path = os.path.join(base_path, 'backend')

# Aggiungi 'backend' ai percorsi riconosciuti da Python
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

import database.store_data as sd
import pdf_generator as pg

base_dir = os.path.dirname(os.path.abspath(__file__))

AUDIO_FOLDER = os.path.abspath(os.path.join(base_dir, "..", "backend", "audio"))
TRANSCRIPTS_FOLDER = os.path.abspath(os.path.join(base_dir, "..", "backend", "transcripts"))
REPORTS_FOLDER = os.path.abspath(os.path.join(base_dir, "..", "backend", "reports"))

# Dizionario coordinate province (per la mappa)
provincia_coords = {
    "AG": [37.3111, 13.5765], "AL": [44.9122, 8.6150], "AN": [43.6167, 13.5167],
    "AO": [45.7370, 7.3201], "AR": [43.4633, 11.8807], "AP": [42.8546, 13.5760],
    "AT": [44.9000, 8.2046], "AV": [40.9140, 14.7909], "BA": [41.1171, 16.8719],
    "BT": [41.3143, 16.2804], "BL": [46.1416, 12.2153], "BN": [41.1299, 14.7819],
    "BG": [45.6983, 9.6773], "BI": [45.5661, 8.0536], "BO": [44.4949, 11.3426],
    "BZ": [46.4983, 11.3548], "BS": [45.5416, 10.2118], "BR": [40.6327, 17.9368],
    "CA": [39.2238, 9.1217], "CL": [37.4897, 14.0615], "CB": [41.5606, 14.6621],
    "CE": [41.0739, 14.3323], "CT": [37.5079, 15.0830], "CZ": [38.9098, 16.5877],
    "CH": [42.3477, 14.1675], "CO": [45.8080, 9.0852], "CS": [39.2983, 16.2536],
    "CR": [45.1333, 10.0333], "KR": [39.0833, 17.1167], "CN": [44.3883, 7.5476],
    "EN": [37.5675, 14.2772], "FM": [43.1615, 13.7186], "FE": [44.8381, 11.6198],
    "FI": [43.7696, 11.2558], "FG": [41.4622, 15.5446], "FC": [44.2227, 12.0407],
    "FR": [41.6412, 13.3514], "GE": [44.4056, 8.9463], "GO": [45.9409, 13.6269],
    "GR": [42.7638, 11.1096], "IM": [43.8896, 8.0395], "IS": [41.5953, 14.2336],
    "AQ": [42.3506, 13.3995], "LT": [41.4676, 13.4432], "LE": [40.3529, 18.1743],
    "LC": [45.8566, 9.3977], "LI": [43.5485, 10.3106], "LO": [45.3142, 9.5037],
    "LU": [43.8430, 10.5086], "MC": [43.2991, 13.4533], "MN": [45.1564, 10.7914],
    "MS": [44.0351, 10.1440], "MT": [40.6685, 16.6016], "ME": [38.1938, 15.5540],
    "MI": [45.4642, 9.1900], "MO": [44.6460, 10.9252], "MB": [45.5845, 9.2744],
    "NA": [40.8522, 14.2681], "NO": [45.4469, 8.6222], "NU": [40.3202, 9.3264],
    "OR": [39.9034, 8.5912], "PD": [45.4064, 11.8768], "PA": [38.1157, 13.3615],
    "PR": [44.8015, 10.3279], "PV": [45.1847, 9.1582], "PG": [43.1122, 12.3888],
    "PU": [43.9090, 12.9120], "PE": [42.4618, 14.2161], "PC": [45.0522, 9.6926],
    "PN": [45.9560, 12.6605], "PZ": [40.6395, 15.8055], "PO": [43.8777, 11.1022],
    "RG": [36.9256, 14.7243], "RA": [44.4170, 12.1991], "RC": [38.1110, 15.6613],
    "RE": [44.6983, 10.6298], "RI": [42.4048, 12.8620], "RN": [44.0600, 12.5653],
    "RO": [45.0705, 11.7905], "SA": [40.6824, 14.7681], "SS": [40.7272, 8.5600],
    "SV": [44.3084, 8.4810], "SI": [43.3188, 11.3308], "SR": [37.0755, 15.2866],
    "SO": [46.1698, 9.8710], "TA": [40.4720, 17.2286], "TE": [42.6589, 13.7052],
    "TR": [42.5580, 12.6444], "TO": [45.0703, 7.6869], "TP": [38.0183, 12.5130],
    "TN": [46.0700, 11.1200], "TV": [45.6669, 12.2431], "TS": [45.6495, 13.7768],
    "UD": [46.0667, 13.2333], "VA": [45.8170, 8.8252], "VE": [45.4408, 12.3155],
    "VB": [45.9292, 8.5518], "VC": [45.3202, 8.4199], "VR": [45.4384, 10.9916],
    "VV": [38.6765, 16.1001], "VI": [45.5455, 11.5354], "VT": [42.4207, 12.1077]
}

# --- FUNZIONI DI SUPPORTO ---
@st.cache_data(ttl=1200) # Cache per 5 minuti
def load_all_data():
    """Carica tutti i record da MongoDB e li converte in DataFrame."""
    collection = sd.connect_to_mongo()
    if collection is None:
        return pd.DataFrame() # Restituisce un DF vuoto se la connessione fallisce
    data = list(collection.find({}))
    if not data:
        return pd.DataFrame()
    
    # Usiamo json_normalize per appiattire la struttura e creare il DataFrame
    df = pd.json_normalize(data, sep='_')
    
    # Conversione tipi di dato per filtri e grafici
    if 'chiamata_data' in df.columns:
        df['chiamata_data'] = pd.to_datetime(df['chiamata_data'], errors='coerce')
    if 'dati_paziente_data_nascita' in df.columns:
        df['dati_paziente_data_nascita'] = pd.to_datetime(df['dati_paziente_data_nascita'], errors='coerce')
    
    # Rinominiamo la colonna _id per facilità d'uso
    if '_id' in df.columns:
        df.rename(columns={'_id': 'record_id'}, inplace=True)
        
    return df

def calculate_age(born):
    """Calcola l'età a partire dalla data di nascita."""
    if pd.isna(born): return None
    today = datetime.today()
    return today.year - born.year - ((today.month, today.day) < (born.month, born.day))

@st.cache_data(ttl=60)
def get_record_by_id(record_id):
    """Recupera un singolo record completo dal DB usando il suo ID."""
    collection = sd.connect_to_mongo()
    if collection is None: return None
    # L'ID deve essere convertito in un oggetto ObjectId di MongoDB
    return collection.find_one({"_id": ObjectId(record_id)})

# --- NUOVA FUNZIONE PER LA PAGINAZIONE PERSONALIZZATA ---
def render_pagination_control(total_pages):
    """
    Crea e gestisce un controllo di paginazione personalizzato.
    """
    # Inizializza la pagina corrente in session_state se non esiste
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 1
    
    # Assicura che la pagina corrente sia valida (potrebbe cambiare se i filtri riducono le pagine totali)
    st.session_state.current_page = min(st.session_state.current_page, total_pages)
    st.session_state.current_page = max(1, st.session_state.current_page)

    # Layout orizzontale per i controlli
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
        # Indicatore di pagina centrale e stilizzato
        st.markdown(f"<p style='text-align: center; font-size: 1.1em; margin-top: 0.4rem;'>Pagina <b>{st.session_state.current_page}</b> di {total_pages}</p>", unsafe_allow_html=True)
    with col4:
        if st.button("Succ. >", use_container_width=True, disabled=(st.session_state.current_page == total_pages)):
            st.session_state.current_page += 1
            st.rerun()
    with col5:
        if st.button("Fine >>", use_container_width=True, disabled=(st.session_state.current_page == total_pages)):
            st.session_state.current_page = total_pages
            st.rerun()

    return st.session_state.current_page


# --- SEZIONE DI RICERCA E FILTRO DATI ---
def render_data(df):
    """Renderizza la sezione di ricerca, filtro e gestione dei record."""
    st.markdown("### 🔍 Ricerca e Filtraggio Dati Paziente")
    st.markdown("Usa i filtri per trovare record specifici e agire su di essi.")

    # --- PANNELLO FILTRI ESPANDIBILE ---
    with st.expander("⬇️ Apri Pannello Filtri", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            search_term = st.text_input("Cerca Paziente per Nome/Cognome o CF:", help="Ricerca non sensibile alle maiuscole.")
            min_date, max_date = (df['chiamata_data'].min().date(), df['chiamata_data'].max().date()) if not df['chiamata_data'].isnull().all() else (datetime.today().date(), datetime.today().date())
            date_range = st.date_input("Filtra interventi per data:", (min_date, max_date), min_value=min_date, max_value=max_date)
        with col2:
            unique_codes = sorted(df['chiamata_codice_uscita'].dropna().unique()) if 'chiamata_codice_uscita' in df.columns else []
            selected_code = st.selectbox("Filtra per Codice di Uscita:", ["Tutti"] + unique_codes)
            all_conditions = sorted(df.explode('condizioni_croniche')['condizioni_croniche'].dropna().unique()) if 'condizioni_croniche' in df.columns else []
            selected_conditions = st.multiselect("Filtra per Condizioni Croniche:", options=all_conditions)

    # --- APPLICAZIONE DEI FILTRI ---
    filtered_interventions = df.copy()
    
    # Applica filtri sugli interventi
    if len(date_range) == 2:
        start_date, end_date = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1]).replace(hour=23, minute=59, second=59)
        filtered_interventions = filtered_interventions[filtered_interventions['chiamata_data'].between(start_date, end_date)]
    if selected_code != "Tutti":
        filtered_interventions = filtered_interventions[filtered_interventions['chiamata_codice_uscita'] == selected_code]
    if selected_conditions:
        filtered_interventions = filtered_interventions[filtered_interventions['condizioni_croniche'].apply(lambda x: isinstance(x, list) and any(item in selected_conditions for item in x))]
        
    # Ottieni la lista di pazienti UNICI che hanno avuto interventi filtrati
    patient_ids = filtered_interventions['codice_fiscale'].dropna().unique()

    # Applica filtro per nome/CF sulla lista dei pazienti già filtrati
    if search_term:
        # Troviamo i CF dei pazienti che matchano la ricerca sul DataFrame originale
        matching_patients_cf = df[
            df['dati_paziente_cognome_nome'].str.contains(search_term, case=False, na=False) |
            (df['codice_fiscale'].str.contains(search_term, case=False, na=False) if 'codice_fiscale' in df.columns else False)
        ]['codice_fiscale'].unique()
        # Manteniamo solo i pazienti che sono in entrambe le liste
        patient_ids = [pid for pid in patient_ids if pid in matching_patients_cf]

    # --- BLOCCO PER L'ORDINAMENTO ALFABETICO ---
    if len(patient_ids) > 0:
        # Crea una mappatura CF -> Nome per i pazienti trovati
        patient_map_df = df[df['codice_fiscale'].isin(patient_ids)][['codice_fiscale', 'dati_paziente_cognome_nome']].drop_duplicates()
        
        # Ordina la mappa per nome paziente
        sorted_patient_map = patient_map_df.sort_values('dati_paziente_cognome_nome')
        
        # Estrai la lista di CF ordinata
        sorted_patient_ids = sorted_patient_map['codice_fiscale'].to_numpy()
    else:
        sorted_patient_ids = []

    st.markdown("---")
    st.write(f"**Trovati {len(sorted_patient_ids)} pazienti che corrispondono ai criteri di ricerca.**")

    if sorted_patient_ids.any():
        # --- PAGINAZIONE PER PAZIENTI ---
        items_per_page = 100
        total_pages = max(1, (len(sorted_patient_ids) - 1) // items_per_page + 1)
        
        page_number = render_pagination_control(total_pages)
        
        start_idx = (page_number - 1) * items_per_page
        paginated_patient_ids = sorted_patient_ids[start_idx : start_idx + items_per_page]

        # --- VISUALIZZAZIONE PAZIENTE-CENTRICA ---
        for cf in paginated_patient_ids:
            # Estrai i dati anagrafici del paziente (prendiamo la prima occorrenza)
            patient_data = df[df['codice_fiscale'] == cf].iloc[0]
            patient_name = patient_data.get('dati_paziente_cognome_nome', 'N/A')
            birth_date = patient_data.get('dati_paziente_data_nascita', pd.NaT)
            
            # Estrai TUTTI gli interventi del paziente che rispettano i filtri
            patient_interventions = filtered_interventions[filtered_interventions['codice_fiscale'] == cf].sort_values('chiamata_data', ascending=False)
            
            with st.container(border=True):
                # Anagrafica del Paziente
                st.markdown(f"### {patient_name}")
                st.markdown(f"**Codice Fiscale:** `{cf}` | **Data di Nascita:** `{birth_date.strftime('%d/%m/%Y') if pd.notna(birth_date) else 'N/A'}`")
                st.markdown(f"*{len(patient_interventions)} interventi trovati con i filtri attuali.*")
                
                # Timeline degli interventi
                for _, intervention in patient_interventions.iterrows():
                    intervention_date = intervention.get('chiamata_data').strftime('%d/%m/%Y alle %H:%M')
                    intervention_id = intervention['record_id']
                    
                    with st.expander(f"**Intervento del {intervention_date}** - Codice Uscita: `{intervention.get('chiamata_codice_uscita', 'N/A')}`"):
                        col1, col2, col3 = st.columns([2, 2, 1])
                        with col1:
                            st.markdown(f"**Luogo:** {intervention.get('chiamata_luogo_intervento', 'N/A')}")
                            st.markdown(f"**Condizione riferita:** {intervention.get('chiamata_condizione_riferita', 'N/A')}")
                        with col2:
                            st.markdown(f"**Condizioni Croniche:** {', '.join(intervention.get('condizioni_croniche', [])) or 'Nessuna'}")
                            # Qui puoi aggiungere altri dettagli dell'intervento
                        with col3:
                            # Bottoni per azioni specifiche sull'intervento
                            if st.button("📄 Genera PDF", key=f"pdf_{intervention_id}", use_container_width=True):
                                with st.spinner("Generazione PDF..."):
                                    if full_record := get_record_by_id(str(intervention_id)):
                                        dati_per_pdf = {
                                            "timestamp": full_record.get('timestamp', ''),
                                            "data": full_record  # Passiamo l'intero record piatto come sotto-chiave 'data'
                                        }
                                        codice_fiscale = full_record.get('codice_fiscale', 'NO_CF')
                                        timestamp_per_file = full_record.get('timestamp', str(intervention_id))
                                        pdf_filename = f"{codice_fiscale}_{timestamp_per_file}_report.pdf"

                                        pdf_path = os.path.join(REPORTS_FOLDER, pdf_filename)

                                        pg.crea_report_medico(dati_per_pdf, filename=pdf_path)

                                        with open(pdf_path, "rb") as pdf_file:
                                            st.download_button(
                                                label="Scarica PDF",
                                                data=pdf_file.read(),
                                                file_name=pdf_filename,
                                                mime="application/pdf",
                                                key=f"download_{intervention_id}"
                                            )
                                    else: st.error("Dati completi non trovati.")
                            
                            if st.button("🗑️ Elimina", type="primary", key=f"del_{intervention_id}", use_container_width=True):
                                if sd.delete_patient_data(intervention_id):
                                    st.success(f"Intervento del {intervention_date} eliminato.")
                                    st.rerun()
                                else: st.error("Errore durante l'eliminazione.")
    else:
        st.info("Nessun paziente corrisponde ai criteri di ricerca.")


# --- FUNZIONE PRINCIPALE DELL'INTERFACCIA ---
def interface():
    """Funzione principale che organizza l'intera pagina dello storico."""
    
    df = load_all_data()

    if df.empty:
        st.warning("⚠️ Nessun dato trovato nel database. Registra qualche intervento per poter usare questa sezione.")
        return

    # Inizializza lo stato per il download del PDF se non esiste
    if "pdf_to_download" not in st.session_state:
        st.session_state.pdf_to_download = None

    render_data(df)