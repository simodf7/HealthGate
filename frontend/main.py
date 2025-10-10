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
from config_css import CSS_STYLE, PAGE_ICON, initialize_session_state
# from streamlit_navigation_bar import st_navbar 

# Percorsi ai moduli
# sys.path.append('./frontend')

# Metodo di debug
def print_debug(message):
    """Stampa messaggi di debug con timestamp per facilitare il tracciamento degli eventi durante l'esecuzione."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] HealthGate DEBUG: {message}")





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
        page_icon=PAGE_ICON,
        initial_sidebar_state="collapsed"
    )

    initialize_session_state() # Inizializza tutte le variabili di stato

    print_debug("Configurazione pagina Streamlit completata")

    # CSS personalizzato per migliorare l'aspetto grafico
    st.markdown(CSS_STYLE, unsafe_allow_html=True)

    # Gestione ritorno alla home
    if st.session_state.view in ["patient-login", "operator-login", "signup"]:
        if st.button("Torna alla Home", key="back_to_home", type="primary"):
            st.session_state.view = "home"
            st.rerun()

    # Titolo principale e sottotitolo
    col1_header, col2_header = st.columns([0.5,4])

    with col1_header:
        st.image("logo/logo-3.jpeg", width=95)

    with col2_header:
        st.markdown('<h1 class="main-header">HealthGate</h1>', unsafe_allow_html=True)
        st.markdown('<p style="text-align: left; font-size: 1.2rem; color: #666; margin-bottom: 3rem;">Sistema intelligente per il pronto soccorso</p>', unsafe_allow_html=True)

    st.divider()
    
    # Gestione toast per successo registrazione/login
    '''
    
    '''

    # Mostra interfaccia home solo se non siamo in login/signup
    if st.session_state.view == "home":
        col1, col2, col3 = st.columns([1.2,1.5,1])

        with col1:
            st.header("Sei un Paziente?")
            if st.button("Autenticati come Paziente", key="patient_login_start", icon="🙋", type="primary"):
                print_debug("Utente ha cliccato Autenticati come Paziente")
                st.session_state.view = "patient-login"
                # st.session_state.view = "patient-logged" # debug
                st.rerun()

        with col2:
            st.header("Sei un Operatore Sanitario?")
            if st.button("Autenticati come Operatore Sanitario", key="operator_login_start", icon="🧑‍⚕️", type="primary"):
                print_debug("Utente ha cliccato Autenticati come Operatore Sanitario")
                st.session_state.view = "operator-login"
                # st.session_state.view = "operator-logged" # debug
                st.rerun()

        with col3:
            st.header("Sei un nuovo utente?")
            if st.button("Registrati", key="signup_start", icon="➡️", type="primary"):
                print_debug("Utente ha cliccato Registrati")
                st.session_state.view = "signup"
                st.rerun()

    # Gestione login (senza dialog)
    if st.session_state.view in ["patient-login", "operator-login"]:
        login.login_interface()
    
    # Gestione signup
    if st.session_state.view == "signup":
        signup.signup_interface()
    
    # Gestione viste dopo login
    if st.session_state.view == "patient-logged":
        import patient_ui
        patient_ui.interface()
        return
    elif st.session_state.view == "operator-logged":
        import operator_ui
        operator_ui.interface()
        return