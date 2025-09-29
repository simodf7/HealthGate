"""
[FRONTEND] login.py

Modulo per la gestione del login degli utenti in HealthGate.
"""

import streamlit as st

def login_interface():
    """
    Funzione che gestisce l'interfaccia di login tramite dialog.
    Permette agli utenti di inserire le proprie credenziali e accedere al sistema.
    """
    
    import requests

    @st.dialog("Login")
    def login_dialog():
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        error_message = None
        error_icon = None

        if st.session_state.get("login_error") is not None:
            error_message, error_icon = st.session_state.login_error
            st.error(error_message, icon=error_icon)
            st.session_state.login_error = None

        if st.button("Accedi"):
            # Scegli endpoint in base al tipo di utente (qui esempio: paziente)
            # Modifica qui se vuoi login operator
            url = "http://localhost:8000/login/patient"  # Cambia porta/host se necessario
            payload = {"social_sec_number": username, "password": password}
            
            try:
                response = requests.post(url, json=payload)
                if response.status_code == 200:
                    st.success("Login effettuato con successo!")
                    st.session_state.view = "main"
                    st.session_state.token = response.json().get("access_token")
                else:
                    error = response.json().get("detail", "Credenziali non valide. Riprova.")
                    st.session_state.login_error = (error, "🚨")
            except Exception as e:
                st.session_state.login_error = (f"Errore di connessione: {e}", "🚨")
    login_dialog()