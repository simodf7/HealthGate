"""
[FRONTEND] signup.py

Modulo per il signup.
"""

import streamlit as st
import requests
import datetime
from config import CSS_STYLE, PAGE_ICON

today = datetime.date.today()
maxDate = today.replace(year=today.year - 18)  # Utente deve avere almeno 18 anni

def signup_interface():
    """
    Funzione che gestisce l'interfaccia di signup.
    Permette agli utenti di registrarsi tramite API Gateway.
    """
    
    # Configurazione della pagina Streamlit
    st.set_page_config(
        page_title="HealthGate", 
        layout="centered",
        page_icon=PAGE_ICON,
        initial_sidebar_state="collapsed"
    )

    # CSS personalizzato per migliorare l'aspetto grafico
    st.markdown(CSS_STYLE, unsafe_allow_html=True)

    col1_header, col2_header = st.columns([3, 2])

    with col1_header:
        st.header("Registrazione utente")

    with col2_header:
        if st.button("Torna alla Home", key="cancel_patient_signup", use_container_width=True):
            st.session_state.view = "home"
            st.rerun()
    
    st.write("Seleziona il tipo di utente da registrare:")
    user_type = st.radio("Tipo utente", ["Paziente", "Operatore"], horizontal=True)

    error_message = None
    error_icon = None

    if user_type == "Paziente":
        st.session_state.firstname = st.text_input("Nome", key="signup_patient_firstname")
        st.session_state.lastname = st.text_input("Cognome", key="signup_patient_lastname")
        st.session_state.birth_date = st.date_input("Data di nascita",
            value=maxDate,
            max_value=maxDate, # Almeno 18 anni
            min_value=datetime.date(1900, 1, 1),
            help="Devi avere almeno 18 anni per registrarti.",
            key="signup_patient_birth_date")
        st.session_state.sex = st.selectbox("Sesso", ["M", "F"], key="signup_patient_sex")
        st.session_state.birth_place = st.text_input("Luogo di nascita", key="signup_patient_birth_place")
        st.session_state.signup_password = st.text_input("Password", type="password", key="signup_patient_password")
        st.session_state.signup_confirm_password = st.text_input("Conferma Password", type="password", key="signup_patient_confirm_password")

        if st.session_state.get("signup_error_paziente"):
            error_message, error_icon = st.session_state.signup_error_paziente
            st.error(error_message, icon=error_icon)
            st.session_state.signup_error_paziente = None

        col1, col2 = st.columns([1, 4])
        
        with col1:
            if st.button("Annulla", key="cancel_patient_signup", use_container_width=True):
                st.session_state.view = "home"
                st.rerun()
        
        with col2:
            if st.button("Registrati come Paziente", key="signup_patient_button", use_container_width=True):
                _perform_patient_signup()

    elif user_type == "Operatore":
        st.session_state.med_register_code = st.text_input("Codice Albo Medico", key="signup_operator_med_register_code")
        st.session_state.firstname = st.text_input("Nome", key="signup_operator_firstname")
        st.session_state.lastname = st.text_input("Cognome", key="signup_operator_lastname")
        st.session_state.email = st.text_input("Email", key="signup_operator_email")
        st.session_state.phone_number = st.text_input("Numero di telefono", key="signup_operator_phone_number")
        st.session_state.signup_password = st.text_input("Password", type="password", key="signup_operator_password")
        st.session_state.signup_confirm_password = st.text_input("Conferma Password", type="password", key="signup_operator_confirm_password")

        if st.session_state.get("signup_error_operatore"):
            error_message, error_icon = st.session_state.signup_error_operatore
            st.error(error_message, icon=error_icon)
            st.session_state.signup_error_operatore = None

        col1, col2 = st.columns([1, 4])
        
        with col1:
            if st.button("Registrati come Operatore", key="signup_operator_button", use_container_width=True):
                _perform_operator_signup()
        
        with col2:
            if st.button("Annulla", key="cancel_operator_signup", use_container_width=True):
                st.session_state.view = "home"
                st.rerun()

def _perform_patient_signup():
    """
    Esegue la registrazione del paziente
    """
    # Validazione campi
    if not all([st.session_state.firstname,
                st.session_state.lastname,
                st.session_state.birth_date,
                st.session_state.sex,
                st.session_state.birth_place,
                st.session_state.signup_password,
                st.session_state.signup_confirm_password]):
        st.session_state.signup_error_paziente = ("Tutti i campi sono obbligatori!", "🚨")
        st.rerun()
    elif st.session_state.signup_password != st.session_state.signup_confirm_password:
        st.session_state.signup_error_paziente = ("Le password non coincidono!", "🚨")
        st.rerun()
    else:
        # Payload da inviare al backend
        payload = {
            "firstname": st.session_state.firstname,
            "lastname": st.session_state.lastname,
            "birth_date": st.session_state.birth_date.strftime("%Y-%m-%d"),
            "sex": st.session_state.sex,
            "birth_place": st.session_state.birth_place,
            "password": st.session_state.signup_password
        }

        try:
            response = requests.post(
                "http://localhost:8001/signup/patient",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            if response.status_code == 200:
                st.session_state.patient_signup_success = True  # FLAG di successo
                st.session_state.view = "home"  # Torno alla home
                st.rerun()
            else:
                # Gestione errore, anche in caso di duplicato
                try:
                    error = response.json().get("detail", "Errore nella registrazione. Riprova.")
                except ValueError:
                    error = f"Errore HTTP {response.status_code}: {response.text}"
                st.session_state.signup_error_paziente = (error, "🚨")
                st.rerun()
        except Exception as e:
            st.session_state.signup_error_paziente = (f"Errore di connessione: {e}", "🚨")
            st.rerun()

def _perform_operator_signup():
    """
    Esegue la registrazione dell'operatore
    """
    if not all([st.session_state.med_register_code,
                st.session_state.firstname,
                st.session_state.lastname,
                st.session_state.email,
                st.session_state.phone_number,
                st.session_state.signup_password,
                st.session_state.signup_confirm_password]):
        st.session_state.signup_error_operatore = ("Tutti i campi sono obbligatori.", "🚨")
        st.rerun()
    elif st.session_state.signup_password != st.session_state.signup_confirm_password:
        st.session_state.signup_error_operatore = ("Le password non coincidono.", "🚨")
        st.rerun()
    else:
        payload = {
            "med_register_code": st.session_state.med_register_code,
            "firstname": st.session_state.firstname,
            "lastname": st.session_state.lastname,
            "email": st.session_state.email,
            "phone_number": st.session_state.phone_number,
            "password": st.session_state.signup_password
        }

        try:
            response = requests.post(
                "http://localhost:8001/signup/operator",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            if response.status_code == 200:
                st.session_state.operator_signup_success = True  # FLAG di successo
                st.session_state.view = "home"  # Torno alla home
                st.rerun()
            else:
                try:
                    error = response.json().get("detail", "Errore nella registrazione. Riprova.")
                except ValueError:
                    error = f"Errore HTTP {response.status_code}: {response.text}"
                st.session_state.signup_error_operatore = (error, "🚨")
                st.rerun()
        except Exception as e:
            st.session_state.signup_error_operatore = (f"Errore di connessione: {e}", "🚨")
            st.rerun()