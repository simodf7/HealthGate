"""
[FRONTEND] login.py

Modulo per il login.
"""

import streamlit as st
import requests
from config import CSS_STYLE, PAGE_ICON

def login_interface():
    """
    Funzione che gestisce l'interfaccia di login tramite API Gateway.
    """
    st.set_page_config(
        page_title="Login", 
        layout="centered",
        page_icon=PAGE_ICON,
        initial_sidebar_state="collapsed"
    )

    # CSS personalizzato per migliorare l'aspetto grafico
    st.markdown(CSS_STYLE, unsafe_allow_html=True)

    col1_header, col2_header = st.columns([3, 2])

    with col1_header:
        st.header("Login utente")

    with col2_header:
        if st.button("Torna alla Home", key="cancel_patient_login", icon="🏠", use_container_width=True):
            st.session_state.view = "home"
            st.rerun()
    
    # Form di login
    if st.session_state.view == "patient-login":
        st.session_state.username = st.text_input("Codice Fiscale", key="login_patient_username")
        st.session_state.login_password = st.text_input("Password", type="password", key="login_patient_password")
    elif st.session_state.view == "operator-login":
        st.session_state.username = st.text_input("Codice Iscrizione Albo", key="login_operator_username")
        st.session_state.login_password = st.text_input("Password", type="password", key="login_operator_password")

    # Mostra errori precedenti
    if st.session_state.get("login_error") is not None:
        error_message, error_icon = st.session_state.login_error
        st.error(error_message, icon=error_icon)
        st.session_state.login_error = None

    
    if st.button("Accedi", key="login_button", use_container_width=True):
        _perform_login()

def _perform_login():
    """
    Esegue il login tramite API
    """
    # Validazione campi
    if not all([st.session_state.username, st.session_state.login_password]):
        st.session_state.login_error = ("Tutti i campi sono obbligatori!", "🚨")
        st.rerun()
        return

    # Request da inviare al Gateway
    if st.session_state.view == "patient-login":
        url = "http://localhost:8000/login/patient"
        payload = {
            "social_sec_number": st.session_state.username,
            "password": st.session_state.login_password
        }
    else:  # operator login
        url = "http://localhost:8000/login/operator"
        payload = {
            "med_register_code": st.session_state.username,
            "password": st.session_state.login_password
        }

    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            data = response.json() # Tutti i dati della return del login
            
            st.session_state.token = data.get("access_token")

            if st.session_state.view == "patient-login":
                st.session_state.firstname = data.get("firstname")
                st.session_state.lastname = data.get("lastname")
                st.session_state.birth_date = data.get("birth_date")
                st.session_state.sex = data.get("sex")
                st.session_state.birth_place = data.get("birth_place")

                st.session_state.view = "patient-logged"
                st.session_state.patient_login_success = True
            elif st.session_state.view == "operator-login":
                st.session_state.med_register_code = data.get("med_register_code")
                st.session_state.firstname = data.get("firstname")
                st.session_state.lastname = data.get("lastname")
                st.session_state.email = data.get("email")
                st.session_state.phone_number = data.get("phone_number")

                st.session_state.view = "operator-logged"
                st.session_state.operator_login_success = True
            
            st.rerun()
        else:
            # Gestione errore, anche in caso di credenziali non valide
            try:
                error = response.json().get("detail", "Errore nel login. Riprova.")
            except ValueError:
                error = f"Errore HTTP {response.status_code}: {response.text}"
            st.session_state.login_error = (error, "🚨")
            st.rerun()
    except Exception as e:
        st.session_state.login_error = (f"Errore di connessione: {e}", "🚨")
        st.rerun()