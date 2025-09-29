"""
[FRONTEND] main_page.py

Modulo principale per l'interfaccia utente di HealthGate.
"""

import sys
import streamlit as st
from datetime import datetime

# Percorsi ai moduli
sys.path.append('./frontend')

import load_models as lm
import input_capture as capt
import filter_data as fd

def print_debug(message):
    """Stampa messaggi di debug con timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] HealthGate DEBUG: {message}")

def reset_transcription_state():
    """Pulisce lo stato della sessione relativo a una trascrizione."""
    print("MAIN_PAGE DEBUG: Chiamata a reset_transcription_state()")
    keys_to_reset = [
        'audio_uploaded',
        'audio_filename',
        'audio_path',
        'transcription_done',
        'transcription_text',
        'structured_json',
        'edited_json',
        'json_path',
    ]
    for key in keys_to_reset:
        if key in st.session_state:
            del st.session_state[key]
            print(f"  -> Chiave '{key}' rimossa da session_state.")
    
    # È buona pratica reinizializzare i flag a uno stato noto
    st.session_state.audio_uploaded = False
    st.session_state.transcription_done = False

def main_interface():
    print_debug("Inizializzazione applicazione HealthGate")
    
    st.set_page_config(
        page_title="HealthGate", 
        layout="wide",
        page_icon="🚑",
        initial_sidebar_state="collapsed"
    )
    
    print_debug("Configurazione pagina Streamlit completata")
    
    # CSS personalizzato
    st.markdown("""
    <style>
    .main-header {
        text-align: center;
        color: #388659; /* sea-green */
        font-size: 3rem;
        font-weight: bold;
        margin-bottom: 2rem;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
    }
    .section-header {
        color: #52aa5e; /* pigment-green */
        font-size: 1.8rem;
        font-weight: 600;
        margin-bottom: 1rem;
        border-bottom: 3px solid #3aaed8; /* process-cyan */
        padding-bottom: 0.5rem;
    }
    .card {
        background: #f5f7fa;
        padding: 2rem;
        border-radius: 12px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        margin-bottom: 1.5rem;
        border: 1px solid #c3cfe2;
    }
    .stButton > button {
        background: #52aa8a; /* zomp */
        color: white;
        border: none;
        border-radius: 10px; /* meno arrotondato */
        padding: 0.6rem 1.5rem;
        font-size: 1.1rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0,0,0,0.3);
    }
    .home-button > button {
        background: #388659; /* sea-green */
    }
    .proceed-button > button {
        background: #2bd9fe; /* vivid-sky-blue */
    }
    .info-box {
        background: #e3f2fd;
        border-left: 5px solid #3aaed8; /* process-cyan */
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Main title with custom styling
    st.markdown('<h1 class="main-header">🚑 HealthGate</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; font-size: 1.2rem; color: #666; margin-bottom: 3rem;">Sistema intelligente per il pronto soccorso</p>', unsafe_allow_html=True)
    
    # Inizializzazione della schermata
    if "view" not in st.session_state:
        st.session_state.view = "home"
        print_debug("Inizializzato session_state.view = 'home'")
    else:
        print_debug(f"Session state view corrente: {st.session_state.view}")

    # Inizializza sempre sessione e modelli
    print_debug("Inizializzazione modelli e sessione...")
    lm.session_init()
    print_debug("Modelli e sessione inizializzati con successo")
    
    def show_home():
        print_debug("Rendering della schermata HOME")


        col1, col2 = st.columns(2, gap="large", vertical_alignment="top")
        
        with col1:
            '''
            # Titolo in riquadro sfumato
            st.markdown("""
            <div class="card">
                <h2 class="section-header">📋 Inserisci sintomi</h2>
            """, unsafe_allow_html=True)
            '''

            st.markdown('<h2 class="section-header">📋 Inserisci sintomi</h2>', unsafe_allow_html=True)
            
            print_debug("Rendering sezione registrazione audio")
            capt.data_insert()
            print_debug("Componente data_insert() completato")

            if st.session_state.audio_uploaded: # andiamo nella schermata di interesse se l'audio è stato salvato correttamente
                print_debug("Audio caricato con successo - mostrando opzioni per procedere")
                st.markdown("""
                <div class="info-box">
                    <strong>ℹ️ Informazione importante:</strong><br>
                    Se l'audio non è corretto, è possibile eliminarlo con l'apposita icona del cestino 
                    in alto a destra della registrazione (per audio registrati) o ricaricare un nuovo file. 
                    Altrimenti, clicca su "Procedi".
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown('<div class="proceed-button">', unsafe_allow_html=True)
                if st.button("🚀 Procedi con la trascrizione", use_container_width=True):
                    print_debug("Utente ha cliccato 'Procedi con la trascrizione' - passaggio a view 'capt'")
                    st.session_state.view = "capt"
                st.markdown('</div>', unsafe_allow_html=True)
            else:
                print_debug("Nessun audio caricato ancora")
            
            st.markdown('</div>', unsafe_allow_html=True)

        with col2:
            '''
            # Titolo in riquadro sfumato
            st.markdown("""
            <div class="card">
            <h2 class="section-header">🗃️ Visualizza storico pazienti</h2>
            """, unsafe_allow_html=True)
            '''

            st.markdown('<h2 class="section-header">🗃️ Visualizza storico pazienti</h2>', unsafe_allow_html=True)
            
            print_debug("Rendering sezione storico pazienti")
            st.markdown("""
            <p style="font-size: 1.1rem; color: #555; margin-bottom: 1.5rem;">
                Accedi allo storico completo dei pazienti per consultare le cartelle cliniche precedenti, 
                filtrare per criteri specifici e visualizzare analisi aggregate.
            </p>
            """, unsafe_allow_html=True)
            
            if st.button("📊 Vai allo storico", use_container_width=True):
                print_debug("Utente ha cliccato 'Vai allo storico' - passaggio a view 'fd'")
                st.session_state.view = "fd"
                
            st.markdown('</div>', unsafe_allow_html=True)

    def show_rec_transcribe():
        print_debug("Rendering della schermata TRASCRIZIONE E REPORT")
        col1, col2 = st.columns([3, 1], gap="large", vertical_alignment="top")

        with col1:
            st.markdown('<h2 class="section-header">✏️ Trascrizione e Report</h2>', unsafe_allow_html=True)

        with col2:
            st.markdown('<div class="home-button">', unsafe_allow_html=True)
            if st.button("🏠 Torna alla Home", use_container_width=True):
                print_debug("Utente ha cliccato 'Torna alla Home' da trascrizione - passaggio a view 'home'")
                reset_transcription_state()
                st.session_state.view = "home"
                st.rerun() 
            st.markdown('</div>', unsafe_allow_html=True)
        
        # st.markdown('<div class="card">', unsafe_allow_html=True)
        print_debug("Avvio interfaccia di trascrizione...")
        capt.interface()
        print_debug("Interfaccia di trascrizione completata")
        # st.markdown('</div>', unsafe_allow_html=True)

    def show_data_filtering():
        print_debug("Rendering della schermata FILTRAGGIO STORICO PAZIENTI")
        col1, col2 = st.columns([3, 1], gap="large", vertical_alignment="top")

        with col1:
            st.markdown('<h2 class="section-header"> 🗂️ Storico pazienti</h2>', unsafe_allow_html=True)

        with col2:
            st.markdown('<div class="home-button">', unsafe_allow_html=True)
            if st.button("🏠 Torna alla Home", use_container_width=True):
                print_debug("Utente ha cliccato 'Torna alla Home' da filtraggio - passaggio a view 'home'")

                st.session_state.view = "home"
            st.markdown('</div>', unsafe_allow_html=True)
        
        # st.markdown('<div class="card">', unsafe_allow_html=True)
        print_debug("Avvio interfaccia di filtraggio dati...")
        fd.interface()
        print_debug("Interfaccia di filtraggio dati completata")
        # st.markdown('</div>', unsafe_allow_html=True)
        
    # Logica di visualizzazione
    print_debug(f"Determinazione della vista da mostrare - view attuale: {st.session_state.view}")
    
    if st.session_state.view == "home":
        print_debug("Mostrando vista HOME")
        show_home()
    elif st.session_state.view == "capt":
        print_debug("Mostrando vista TRASCRIZIONE")
        show_rec_transcribe()
    elif st.session_state.view == "fd":
        print_debug("Mostrando vista FILTRAGGIO DATI")
        show_data_filtering()
    else:
        print_debug(f"Vista non riconosciuta: {st.session_state.view} - ritorno alla HOME")
        st.session_state.view = "home"
        show_home()

if __name__ == "__main__":
    print_debug("=== AVVIO APPLICAZIONE HealthGate ===")
    main_interface()
    print_debug("=== FINE ESECUZIONE MAIN INTERFACE ===")