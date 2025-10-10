"""
[FRONTEND] login.py

Modulo per il login.
"""

import streamlit as st
import requests
from config_css import CSS_STYLE, PAGE_ICON
from config import URL_GATEWAY


def _clean_msg(msg: str) -> str:
    """
    Rimuove prefissi tecnici e formatta il messaggio in modo leggibile.
    """
    msg = msg.strip()
    if msg.lower().startswith("value error,"):
        msg = msg[len("value error,"):].strip()
    elif msg.lower().startswith("type error,"):
        msg = msg[len("type error,"):].strip()
    elif msg.lower().startswith("assertion error,"):
        msg = msg[len("assertion error,"):].strip()
    return msg.capitalize()


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


def interface():
    """
    Funzione che gestisce l'interfaccia di login tramite API Gateway.
    """
    st.set_page_config(
        page_title="Login", 
        layout="centered",
        page_icon=PAGE_ICON,
        initial_sidebar_state="collapsed"
    )

    st.markdown(CSS_STYLE, unsafe_allow_html=True)

    # Gestione toast per successo registrazione/login
    if st.session_state.patient_signup_success:
        st.toast(
            f"Registrazione paziente avvenuta con successo: {st.session_state.firstname} {st.session_state.lastname}",
            icon="✅"
        )
        st.session_state.patient_signup_success = False
    elif st.session_state.operator_signup_success:
        st.toast(
            f"Registrazione operatore avvenuta con successo: {st.session_state.firstname} {st.session_state.lastname}",
            icon="✅"
        )
        st.session_state.operator_signup_success = False

    col1_header, col2_header = st.columns([3, 2])
    with col1_header:
        st.header("Login utente")
    with col2_header:
        if st.button("Torna alla Home", key="cancel_patient_login", icon="🏠", use_container_width=True, type="primary"):
            st.session_state.view = "home"
            st.rerun()

    # Form di login
    if st.session_state.view == "patient-login":
        st.session_state.username = st.text_input("Codice Fiscale", key="login_patient_username")
        st.session_state.login_password = st.text_input("Password", type="password", key="login_patient_password")
    elif st.session_state.view == "operator-login":
        st.session_state.username = st.text_input("Codice Iscrizione Albo", key="login_operator_username")
        st.session_state.login_password = st.text_input("Password", type="password", key="login_operator_password")

    # Mostra eventuali errori precedenti
    if st.session_state.get("login_error"):
        error_message, error_icon = st.session_state.login_error
        st.error(error_message, icon=error_icon)
        st.session_state.login_error = None

    if st.button("Accedi", key="login_button", use_container_width=True, type="primary"):
        _perform_login()


def _perform_login():
    """
    Esegue il login tramite API
    """
    if not all([st.session_state.username, st.session_state.login_password]):
        st.session_state.login_error = ("Tutti i campi sono obbligatori!", "🚨")
        st.rerun()
        return

    if st.session_state.view == "patient-login":
        st.session_state.social_sec_number = st.session_state.username # Update del codice fiscale

        url = f"{URL_GATEWAY}/login/patient"
        payload = {
            "social_sec_number": st.session_state.username,
            "password": st.session_state.login_password
        }
    else:  # operator login
        st.session_state.med_register_code = st.session_state.username # Update del register code
        
        url = f"{URL_GATEWAY}/login/operator"
        payload = {
            "med_register_code": st.session_state.username,
            "password": st.session_state.login_password
        }

    try:
        response = requests.post(url, json=payload)

        if response.status_code == 200:
            data = response.json()
            print(data)
            st.session_state.token = data.get("access_token")

            if st.session_state.view == "patient-login":
                st.session_state.firstname = data.get("firstname")
                st.session_state.lastname = data.get("lastname")
                st.session_state.birth_date = data.get("birth_date")
                st.session_state.sex = data.get("sex")
                st.session_state.birth_place = data.get("birth_place")
                st.session_state.view = "patient-logged-symptoms" 
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
            # Gestione avanzata degli errori backend
            error_message = _parse_backend_error(response)
            st.session_state.login_error = (error_message, "🚨")
            st.rerun()

    except requests.exceptions.ConnectionError:
        st.session_state.login_error = ("Impossibile connettersi al server.", "🚨")
        st.rerun()
    except requests.exceptions.Timeout:
        st.session_state.login_error = ("Timeout nella connessione.", "🚨")
        st.rerun()
    except Exception as e:
        st.session_state.login_error = (f"Errore imprevisto: {e}", "🚨")
        st.rerun()