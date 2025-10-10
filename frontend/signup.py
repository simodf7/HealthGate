"""
[FRONTEND] signup.py

Modulo per il signup.
"""

import streamlit as st
import requests
import datetime
import pandas as pd
from config_css import CSS_STYLE, PAGE_ICON
from config import URL_GATEWAY 

today = datetime.date.today()
maxDate = today.replace(year=today.year - 18)  # Utente deve avere almeno 18 anni

# Caricamento lista dei comuni italiani
@st.cache_data(ttl=1200)
def load_comuni():
    try:
        # Il file usa ";" come separatore
        df = pd.read_csv("birthplaces/comuni_italiani.csv", sep=";", dtype=str)

        # Usa la colonna 'denominazione_ita' per i nomi dei comuni
        comuni = sorted(df["denominazione_ita"].dropna().unique().tolist())
        return comuni

    except Exception as e:
        st.warning(f"Impossibile caricare la lista dei comuni: {e}")
        return []

COMUNI_ITALIANI = load_comuni()

def interface():
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

    # Gestione toast per successo registrazione/login

    col1_header, col2_header = st.columns([3, 2])

    with col1_header:
        st.header("Registrazione utente")

    with col2_header:
        if st.button("Torna alla Home", key="cancel_patient_signup_returnhome", icon="🏠", use_container_width=True, type="primary"):
            st.session_state.view = "home"
            st.rerun()

    #st.write("Seleziona il tipo di utente da registrare:")
    user_type = st.radio("Tipo utente", ["Paziente", "Operatore"], horizontal=True)

    error_message = None
    error_icon = None

    if user_type == "Paziente":
        col1, col2 = st.columns(2)

        with col1:
            st.session_state.firstname = st.text_input("Nome", key="signup_patient_firstname")
            st.session_state.sex = st.selectbox("Sesso", ["M", "F"], key="signup_patient_sex")

        with col2:
            st.session_state.lastname = st.text_input("Cognome", key="signup_patient_lastname")
            st.session_state.birth_date = st.date_input("Data di nascita",
                value=maxDate,
                max_value=maxDate, # Almeno 18 anni
                min_value=datetime.date(1900, 1, 1),
                help="Devi avere almeno 18 anni per registrarti.",
                key="signup_patient_birth_date",
                format="DD/MM/YYYY")

        st.session_state.birth_place = st.selectbox(
            "Luogo di nascita",
            options=[""] + COMUNI_ITALIANI,
            key="signup_patient_birth_place",
            help="Seleziona il comune di nascita."
        )

        col1_final, col2_final = st.columns(2)

        with col1_final:
            st.session_state.signup_password = st.text_input("Password", type="password", key="signup_patient_password")

        with col2_final:  
            st.session_state.signup_confirm_password = st.text_input("Conferma Password", type="password", key="signup_patient_confirm_password")

        if st.session_state.get("signup_error_paziente"):
            error_message, error_icon = st.session_state.signup_error_paziente
            st.error(error_message, icon=error_icon)
            st.session_state.signup_error_paziente = None

        if st.button("Registrati come Paziente", key="signup_patient_button", use_container_width=True, type="primary"):
            _perform_patient_signup()

    elif user_type == "Operatore":
        st.session_state.med_register_code = st.text_input("Codice Albo Medico", key="signup_operator_med_register_code")

        col1, col2 = st.columns(2)

        with col1:
            st.session_state.firstname = st.text_input("Nome", key="signup_operator_firstname")
            st.session_state.email = st.text_input("Email", key="signup_operator_email")
            st.session_state.signup_password = st.text_input("Password", type="password", key="signup_operator_password")

        with col2:
            st.session_state.lastname = st.text_input("Cognome", key="signup_operator_lastname")
            st.session_state.phone_number = st.text_input("Numero di telefono", key="signup_operator_phone_number")
            st.session_state.signup_confirm_password = st.text_input("Conferma Password", type="password", key="signup_operator_confirm_password")

        if st.session_state.get("signup_error_operatore"):
            error_message, error_icon = st.session_state.signup_error_operatore
            st.error(error_message, icon=error_icon)
            st.session_state.signup_error_operatore = None

        if st.button("Registrati come Operatore", key="signup_operator_button", use_container_width=True, type="primary"):
            _perform_operator_signup()

# Gestione errori
def _parse_backend_error(response):
    """
    Interpreta e restituisce un messaggio di errore leggibile proveniente dal backend,
    rimuovendo prefissi tecnici come 'Value error,' o 'Type error,'.
    """
    try:
        data = response.json()

        # Caso 1: errore standard FastAPI
        if isinstance(data, dict) and "detail" in data:
            detail = data["detail"]
            if isinstance(detail, list):
                messages = [_clean_msg(err.get("msg", str(err))) for err in detail]
                return " | ".join(messages)
            return _clean_msg(str(detail))

        # Caso 2: lista di errori Pydantic
        elif isinstance(data, list):
            messages = []
            for err in data:
                msg = _clean_msg(err.get("msg", "Errore di validazione"))
                loc = " → ".join(str(x) for x in err.get("loc", []))
                if loc:
                    messages.append(f"{loc}: {msg}")
                else:
                    messages.append(msg)
            return " | ".join(messages)

        # Caso 3: JSON valido ma sconosciuto
        return f"Errore sconosciuto: {data}"

    except ValueError:
        return f"Errore HTTP {response.status_code}: {response.text}"

def _clean_msg(msg: str) -> str:
    """
    Rimuove prefissi tecnici e formatta il messaggio in modo leggibile.
    """
    msg = msg.strip()
    # Elimina prefissi come "Value error," o "Type error,"
    if msg.lower().startswith("value error,"):
        msg = msg[len("value error,"):].strip()
    elif msg.lower().startswith("type error,"):
        msg = msg[len("type error,"):].strip()
    elif msg.lower().startswith("assertion error,"):
        msg = msg[len("assertion error,"):].strip()
    return msg.capitalize()

def _perform_patient_signup():
    """
    Esegue la registrazione del paziente
    """
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
                f"{URL_GATEWAY}/signup/patient",
                json=payload,
                headers={"Content-Type": "application/json"}
            )

            if response.status_code == 200:
                st.session_state.patient_signup_success = True
                st.session_state.view = "patient-login"
                st.rerun()
            else:
                error_message = _parse_backend_error(response)
                st.session_state.signup_error_paziente = (error_message, "🚨")
                st.rerun()

        except requests.exceptions.ConnectionError:
            st.session_state.signup_error_paziente = ("Impossibile connettersi al server.", "🚨")
            st.rerun()
        except requests.exceptions.Timeout:
            st.session_state.signup_error_paziente = ("Timeout nella connessione.", "🚨")
            st.rerun()
        except Exception as e:
            st.session_state.signup_error_paziente = (f"Errore imprevisto: {e}", "🚨")
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
                f"{URL_GATEWAY}/signup/operator",
                json=payload,
                headers={"Content-Type": "application/json"}
            )

            if response.status_code == 200:
                st.session_state.operator_signup_success = True
                st.session_state.view = "operator-login"
                st.rerun()
            else:
                error_message = _parse_backend_error(response)
                st.session_state.signup_error_paziente = (error_message, "🚨")
                st.rerun()

        except requests.exceptions.ConnectionError:
            st.session_state.signup_error_operatore = ("Impossibile connettersi al server.", "🚨")
            st.rerun()
        except requests.exceptions.Timeout:
            st.session_state.signup_error_operatore = ("Timeout nella connessione.", "🚨")
            st.rerun()
        except Exception as e:
            st.session_state.signup_error_operatore = (f"Errore imprevisto: {e}", "🚨")
            st.rerun()