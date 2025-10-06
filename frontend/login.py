"""
[FRONTEND] login.py

Modulo per il login.
"""

# python -m uvicorn main:app  --reload --host 0.0.0.0 --port 8001

import streamlit as st
import requests
import patient
import operator

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
            # URL dell'API Gateway
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
                    data = response.json() # Tutti i dati della return del login
                    
                    st.session_state.token = data.get("access_token")

                    if st.session_state.view == "patient-login":
                        st.session_state.firstname = data.get("firstname")
                        st.session_state.lastname = data.get("lastname")
                        st.session_state.birth_date = data.get("birth_date")
                        st.session_state.sex = data.get("sex")
                        st.session_state.birth_place = data.get("birth_place")

                        st.session_state.view = "patient-logged"
                    elif st.session_state.view == "operator-login":
                        st.session_state.med_register_code = data.get("med_register_code")
                        st.session_state.firstname = data.get("firstname")
                        st.session_state.lastname = data.get("lastname")
                        st.session_state.email = data.get("email")
                        st.session_state.phone_number = data.get("phone_number")

                        st.session_state.view = "operator-logged"
                    
                    # Chiudi il dialog impostando un flag
                    st.session_state.login_success = True
                    st.rerun()
                else:
                    error = response.json().get("detail", "Credenziali non valide. Riprova.")
                    st.session_state.login_error = (error, "🚨")
                    st.rerun()
            except Exception as e:
                st.session_state.login_error = (f"Errore di connessione: {e}", "🚨")
                st.rerun()

    # Mostra il dialog solo se non c'è stato un login con successo
    if not st.session_state.get("login_success", False):
        login_dialog()
    else:
        # Reset del flag dopo il rerun
        st.session_state.login_success = False