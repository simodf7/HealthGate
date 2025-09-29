"""
[FRONTEND] main_page.py

Modulo principale per l'interfaccia utente di HealthGate.
Gestisce l'autenticazione.
"""

import sys
import streamlit as st
from datetime import datetime
import login
import signup

# Percorsi ai moduli
sys.path.append('./frontend')

def print_debug(message):
    """Stampa messaggi di debug con timestamp per facilitare il tracciamento degli eventi durante l'esecuzione."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] HealthGate DEBUG: {message}")

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
    .main-header {
        text-align: center;
        color: #2E86AB;
        font-size: 3rem;
        font-weight: bold;
        margin-bottom: 2rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
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
    st.markdown('<h1 class="main-header">🚑 HealthGate</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; font-size: 1.2rem; color: #666; margin-bottom: 3rem;">Sistema intelligente per il pronto soccorso</p>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1.2,1.5,1])

    with col1:
        st.header("Sei un Paziente?")
        if st.button("Autenticati come Paziente", on_click=login.login_interface):
            print_debug("Utente ha cliccato Autenticati come Paziente")
            st.session_state.view = "patient-login"

    with col2:
        st.header("Sei un Operatore Sanitario?")
        if st.button("Autenticati come Operatore Sanitario", on_click=login.login_interface):
            print_debug("Utente ha cliccato Autenticati come Operatore Sanitario")
            st.session_state.view = "operator-login"

    with col3:
        st.header("Sei un nuovo utente?")
        if st.button("Registrati", on_click=signup.signup_interface):
            print_debug("Utente ha cliccato Registrati")
            st.session_state.view = "signup"