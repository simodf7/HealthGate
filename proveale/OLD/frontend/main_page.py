"""
[FRONTEND] main_page.py

Modulo principale per l'interfaccia utente di HealthGate.
Gestisce la logica di visualizzazione delle diverse schermate e l'inizializzazione della sessione.
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
    """Stampa messaggi di debug con timestamp per facilitare il tracciamento degli eventi durante l'esecuzione."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] HealthGate DEBUG: {message}")

def reset_transcription_state():
    """
    Pulisce lo stato della sessione relativo a una trascrizione.
    Rimuove tutte le chiavi associate alla trascrizione e reinizializza i flag.
    Utile quando si torna alla home per evitare dati residui.
    """
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
    st.session_state.text = False

def main_interface():
    """
    Funzione principale che gestisce l'interfaccia utente.
    Inizializza la pagina, imposta lo stile, gestisce la navigazione tra le viste e richiama i moduli appropriati.
    """
    print_debug("Inizializzazione applicazione HealthGate")
    
    # Configurazione della pagina Streamlit
    st.set_page_config(
        page_title="HealthGate", 
        layout="wide",
        page_icon="🚑",
        initial_sidebar_state="collapsed"
    )
    
    print_debug("Configurazione pagina Streamlit completata")
    
    # CSS personalizzato per migliorare l'aspetto grafico
    st.markdown("""
    <style>
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
        background: #74c3a4; /* colore più chiaro per maggiore leggibilità */
        color: #ffffff; /* testo sempre bianco */
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0,0,0,0.3);
    }
    .home-button > button:hover {
        background: #4fa070; /* versione più chiara del sea-green */
    }
    .proceed-button > button:hover {
        background: #53e4ff; /* versione più chiara del vivid-sky-blue */
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Titolo principale e sottotitolo con bottoni in alto a destra
    col_title, col_signup, col_login = st.columns([4, 0.5, 0.5], gap="large")

    with col_title:
        st.markdown('<h1 class="main-header">🚑 HealthGate</h1>', unsafe_allow_html=True)
        st.markdown('<p style="text-align: left; font-size: 1.2rem; color: #666; margin-bottom: 3rem;">Sistema intelligente per il pronto soccorso</p>', unsafe_allow_html=True)

    with col_signup:
        st.markdown('<div style="text-align: right; margin-top: 1rem;">', unsafe_allow_html=True)
        signup_clicked = st.button("Signup", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

        if signup_clicked:
            print_debug("Utente ha cliccato Signup")
            st.session_state.view = "signup"  # puoi creare una view dedicata alla registrazione
    
    with col_login:
        st.markdown('<div style="text-align: right; margin-top: 1rem;">', unsafe_allow_html=True)
        login_clicked = st.button("Login", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

        if login_clicked:
            print_debug("Utente ha cliccato Login")
            st.session_state.view = "login"  # puoi creare una view dedicata al login

    # Inizializzazione della schermata: imposta la vista di default su 'home'
    if "view" not in st.session_state:
        st.session_state.view = "home"
        print_debug("Inizializzato session_state.view = 'home'")
    else:
        print_debug(f"Session state view corrente: {st.session_state.view}")

    # Inizializza sempre sessione e modelli (caricamento modelli ML, parametri, ecc.)
    print_debug("Inizializzazione modelli e sessione...")
    lm.session_init()
    print_debug("Modelli e sessione inizializzati con successo")
    
    def show_home():
        """
        Visualizza la schermata principale (HOME) dove l'utente può inserire sintomi (audio o testo)
        e accedere allo storico pazienti.
        """
        print_debug("Rendering della schermata HOME")
        col1, col2 = st.columns([2.5, 1.5], gap="large", vertical_alignment="top")
        
        with col1:
            # Sezione per inserimento sintomi
            st.markdown('<h2 class="section-header">📋 Inserisci sintomi</h2>', unsafe_allow_html=True)
            
            print_debug("Rendering sezione registrazione audio")
            capt.data_insert()
            print_debug("Componente data_insert() completato")

            # Se l'audio è stato caricato, mostra opzioni per procedere
            if st.session_state.audio_uploaded:
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
                    print_debug("Utente ha cliccato 'Procedi con la trascrizione' - passaggio a view 'transcribe'")
                    st.session_state.view = "transcribe"
                st.markdown('</div>', unsafe_allow_html=True)
            else:
                print_debug("Nessun audio caricato ancora")
            
            st.markdown('</div>', unsafe_allow_html=True)

        with col2:
            # Sezione per visualizzare lo storico pazienti
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
        """
        Visualizza la schermata di trascrizione e report.
        Permette di tornare alla home e avvia l'interfaccia di trascrizione.
        """
        print_debug("Rendering della schermata TRASCRIZIONE E REPORT")
        col1, col2 = st.columns([4, 0.5], gap="large", vertical_alignment="top")

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
        
        # Avvia l'interfaccia di trascrizione
        print_debug("Avvio interfaccia di trascrizione...")
        capt.interface()
        print_debug("Interfaccia di trascrizione completata")

    def show_data_filtering():
        """
        Visualizza la schermata di filtraggio dello storico pazienti.
        Permette di tornare alla home e avvia l'interfaccia di filtraggio dati.
        """
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
        
        # Avvia l'interfaccia di filtraggio dati
        print_debug("Avvio interfaccia di filtraggio dati...")
        fd.interface()
        print_debug("Interfaccia di filtraggio dati completata")
        
    # Logica di visualizzazione: determina quale vista mostrare in base allo stato della sessione
    print_debug(f"Determinazione della vista da mostrare - view attuale: {st.session_state.view}")
    
    if st.session_state.view == "home":
        print_debug("Mostrando vista HOME")
        show_home()
    elif st.session_state.view == "transcribe":
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
    # Avvio dell'applicazione Streamlit
    print_debug("=== AVVIO APPLICAZIONE HealthGate ===")
    main_interface()
    print_debug("=== FINE ESECUZIONE MAIN INTERFACE ===")