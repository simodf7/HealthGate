"""
[FRONTEND] main.py

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

# Metodo di debug
def print_debug(message):
    """Stampa messaggi di debug con timestamp per facilitare il tracciamento degli eventi durante l'esecuzione."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] HealthGate DEBUG: {message}")

# Inizializzazione delle variabili di stato
def initialize_session_state():
    # Patient
    if "patient_signup_success" not in st.session_state:
        st.session_state.patient_signup_success = False
    if "social_sec_number" not in st.session_state:
        st.session_state.social_sec_number = ""
    if "med_register_code" not in st.session_state:
        st.session_state.med_register_code = ""
    if "birth_date" not in st.session_state:
        st.session_state.birth_date = ""
    if "sex" not in st.session_state:
        st.session_state.sex = ""
    if "birth_place" not in st.session_state:
        st.session_state.birth_place = ""

    # Operator
    if "med_register_code" not in st.session_state:
        st.session_state.med_register_code = ""
    if "email" not in st.session_state:
        st.session_state.email = ""
    if "phone_number" not in st.session_state:
        st.session_state.phone_number = ""
    if "operator_signup_success" not in st.session_state:
        st.session_state.operator_signup_success = False

    # Patient & Operator
    if "firstname" not in st.session_state:
        st.session_state.firstname = ""
    if "lastname" not in st.session_state:
        st.session_state.lastname = ""
    if "username" not in st.session_state:
        st.session_state.username = ""
    if "login_password" not in st.session_state:
        st.session_state.login_password = ""
    if "signup_password" not in st.session_state:
        st.session_state.signup_password = ""
    if "signup_confirm_password" not in st.session_state:
        st.session_state.signup_confirm_password = ""

    # Generic
    if "view" not in st.session_state:
        st.session_state.view = "home"



# =================================

# Interfaccia principale

# =================================

def interface():
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

    initialize_session_state() # Inizializza tutte le variabili di stato

    print_debug("Configurazione pagina Streamlit completata")
    
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

    # Titolo principale e sottotitolo
    col1_header, col2_header = st.columns([0.5,4])

    with col1_header:
        st.image("frontend/logo/logo-3.jpeg", width=100)

    with col2_header:
        st.markdown('<h1 class="main-header">🚑 HealthGate</h1>', unsafe_allow_html=True)
        st.markdown('<p style="text-align: left; font-size: 1.2rem; color: #666; margin-bottom: 3rem;">Sistema intelligente per il pronto soccorso</p>', unsafe_allow_html=True)

    if st.session_state.patient_signup_success:
        st.toast(f"Registrazione Paziente avvenuta con successo: {st.session_state.firstname} {st.session_state.lastname}", icon="✅")
        st.session_state.patient_signup_success = False  # Resetto il FLAG
    elif st.session_state.operator_signup_success:
        st.toast(f"Registrazione Operatore avvenuta con successo: {st.session_state.firstname} {st.session_state.lastname}", icon="✅")
        st.session_state.operator_signup_success = False  # Resetto il FLAG

    col1, col2, col3 = st.columns([1.2,1.5,1])

    with col1:
        st.header("Sei un Paziente?")
        if st.button("Autenticati come Paziente"):
            print_debug("Utente ha cliccato Autenticati come Paziente")
            st.session_state.view = "patient-login"
            st.rerun()

    with col2:
        st.header("Sei un Operatore Sanitario?")
        if st.button("Autenticati come Operatore Sanitario"):
            print_debug("Utente ha cliccato Autenticati come Operatore Sanitario")
            st.session_state.view = "operator-login"
            st.rerun()

    with col3:
        st.header("Sei un nuovo utente?")
        if st.button("Registrati"):
            print_debug("Utente ha cliccato Registrati")
            st.session_state.view = "signup"
            st.rerun()