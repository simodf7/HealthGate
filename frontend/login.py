# python -m uvicorn main:app  --reload --host 0.0.0.0 --port 8001

import streamlit as st
import requests

def login_interface():
    """
    Funzione che gestisce l'interfaccia di login tramite API Gateway.
    """
    @st.dialog("Login")
    def login_dialog():
        if st.session_state.view == "patient-login":
            st.session_state.username = st.text_input("Codice Fiscale", key="login_patient_username")
            st.session_state.login_password = st.text_input("Password", type="password", key="login_patient_password")
        elif st.session_state.view == "operator-login":
            st.session_state.username = st.text_input("Codice Iscrizione Albo", key="login_operator_username")
            st.session_state.login_password = st.text_input("Password", type="password", key="login_operator_password")

        error_message = None
        error_icon = None

        if st.session_state.get("login_error") is not None:
            error_message, error_icon = st.session_state.login_error
            st.error(error_message, icon=error_icon)
            st.session_state.login_error = None

        if st.button("Accedi", key="login_button"):
            # URL dell’API Gateway
            if st.session_state.view == "patient-login":
                url = "http://localhost:8001/login/patient"
            else:
                url = "http://localhost:8001/login/operator"

            # Request da inviare al Gateway
            if st.session_state.view == "patient-login":
                url = "http://localhost:8001/login/patient"
                payload = {
                    "social_sec_number": st.session_state.username,
                    "password": st.session_state.login_password
                }
            else:  # operator login
                url = "http://localhost:8001/login/operator"
                payload = {
                    "med_register_code": st.session_state.username,
                    "password": st.session_state.login_password
                }

            try:
                response = requests.post(url, json=payload)
                if response.status_code == 200:
                    st.success("Login effettuato con successo!")
                    st.session_state.view = "home"
                    st.session_state.token = response.json().get("access_token")
                else:
                    error = response.json().get("detail", "Credenziali non valide. Riprova.")
                    st.session_state.login_error = (error, "🚨")
            except Exception as e:
                st.session_state.login_error = (f"Errore di connessione: {e}", "🚨")

    login_dialog()