"""
[FRONTEND] login.py

Modulo per la gestione del login degli utenti in HealthGate.
"""

import streamlit as st
import datetime

def signup_interface():
    """
    Funzione che gestisce l'interfaccia di signup tramite dialog.
    Permette agli utenti di registrarsi inserendo username e password.
    """
    
    @st.dialog("Signup")
    def signup_dialog():
        st.write("Seleziona il tipo di utente da registrare:")
        user_type = st.radio("Tipo utente", ["Paziente", "Operatore"], horizontal=True)

        error_message = None
        error_icon = None

        if user_type == "Paziente":
            social_sec_number = st.text_input("Codice Fiscale (max 16 caratteri)")
            firstname = st.text_input("Nome")
            lastname = st.text_input("Cognome")
            birth_date = st.date_input("Data di nascita")
            sex = st.selectbox("Sesso", ["M", "F", "O"])
            birth_place = st.text_input("Luogo di nascita")
            password = st.text_input("Password", type="password")
            confirm_password = st.text_input("Conferma Password", type="password")

            if st.session_state.get("signup_error_paziente") is not None:
                error_message, error_icon = st.session_state.signup_error_paziente
                st.error(error_message, icon=error_icon)
                st.session_state.signup_error_paziente = None

            if st.button("Registrati come Paziente"):
                if not all([social_sec_number, firstname, lastname, birth_date, sex, birth_place, password, confirm_password]):
                    st.session_state.signup_error_paziente = ("Tutti i campi sono obbligatori!", "🚨")
                elif password != confirm_password:
                    st.session_state.signup_error_paziente = ("Le password non coincidono!", "🚨")
                else:
                    # Qui si dovrebbe aggiungere la logica per salvare il paziente nel database
                    st.success(f"Registrazione Paziente avvenuta con successo: {firstname} {lastname}")
                    st.session_state.view = "login"
        else:
            med_register_code = st.text_input("Codice Albo Medico")
            firstname = st.text_input("Nome")
            lastname = st.text_input("Cognome")
            email = st.text_input("Email")
            phone_number = st.text_input("Numero di telefono")
            password = st.text_input("Password", type="password")
            confirm_password = st.text_input("Conferma Password", type="password")

            if st.session_state.get("signup_error_operatore") is not None:
                error_message, error_icon = st.session_state.signup_error_operatore
                st.error(error_message, icon=error_icon)
                st.session_state.signup_error_operatore = None

            if st.button("Registrati come Operatore"):
                if not all([med_register_code, firstname, lastname, email, phone_number, password, confirm_password]):
                    st.session_state.signup_error_operatore = ("Tutti i campi sono obbligatori.", "🚨")
                elif password != confirm_password:
                    st.session_state.signup_error_operatore = ("Le password non coincidono.", "🚨")
                else:
                    # Qui si dovrebbe aggiungere la logica per salvare l'operatore nel database
                    st.success(f"Registrazione Operatore avvenuta con successo: {firstname} {lastname}")
                    st.session_state.view = "login"
    signup_dialog()