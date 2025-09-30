import streamlit as st
import requests
import datetime
import main_page as mp
import login

today = datetime.date.today()
maxDate = today.replace(year=today.year - 18)  # Utente deve avere almeno 18 anni

def signup_interface():
    """
    Funzione che gestisce l'interfaccia di signup tramite dialog.
    Permette agli utenti di registrarsi tramite API Gateway.
    """
    
    @st.dialog("Signup")
    def signup_dialog():
        st.write("Seleziona il tipo di utente da registrare:")
        user_type = st.radio("Tipo utente", ["Paziente", "Operatore"], horizontal=True)

        error_message = None
        error_icon = None

        if user_type == "Paziente":
            st.session_state.firstname = st.text_input("Nome")
            st.session_state.lastname = st.text_input("Cognome")
            st.session_state.birth_date = st.date_input("Data di nascita",
                value=maxDate,
                max_value=maxDate, # Almeno 18 anni
                min_value=datetime.date(1900, 1, 1),
                help="Devi avere almeno 18 anni per registrarti.")
            st.session_state.sex = st.selectbox("Sesso", ["M", "F"])
            st.session_state.birth_place = st.text_input("Luogo di nascita")
            st.session_state.password = st.text_input("Password", type="password")
            st.session_state.confirm_password = st.text_input("Conferma Password", type="password")

            if st.session_state.get("signup_error_paziente"):
                error_message, error_icon = st.session_state.signup_error_paziente
                st.error(error_message, icon=error_icon)
                st.session_state.signup_error_paziente = None

            if st.button("Registrati come Paziente"):
                # Validazione campi
                if not all([st.session_state.firstname,
                    st.session_state.lastname,
                    st.session_state.birth_date,
                    st.session_state.sex,
                    st.session_state.birth_place,
                    st.session_state.password,
                    st.session_state.confirm_password]):
                    st.session_state.signup_error_paziente = ("Tutti i campi sono obbligatori!", "🚨")
                elif st.session_state.password != st.session_state.confirm_password:
                    st.session_state.signup_error_paziente = ("Le password non coincidono!", "🚨")
                else:
                    # Payload da inviare al backend
                    payload = {
                        "firstname": st.session_state.firstname,
                        "lastname": st.session_state.lastname,
                        "birth_date": st.session_state.birth_date.strftime("%Y-%m-%d"),
                        "sex": st.session_state.sex,
                        "birth_place": st.session_state.birth_place,
                        "password": st.session_state.password
                    }

                    try:
                        response = requests.post(
                            "http://localhost:8001/signup/patient",
                            json=payload,
                            headers={"Content-Type": "application/json"}
                        )
                        if response.status_code == 200:
                                st.session_state.patient_signup_success = True  # FLAG di successo
                                st.rerun() # Torno alla home
                        else:
                            # Gestione errore, anche in caso di duplicato
                            try:
                                error = response.json().get("detail", "Errore nella registrazione. Riprova.")
                            except ValueError:
                                error = f"Errore HTTP {response.status_code}: {response.text}"
                            st.session_state.signup_error_paziente = (error, "🚨")
                    except Exception as e:
                        st.session_state.signup_error_paziente = (f"Errore di connessione: {e}", "🚨")

        else:  # Operatore
            st.session_state.med_register_code = st.text_input("Codice Albo Medico")
            st.session_state.firstname = st.text_input("Nome")
            st.session_state.lastname = st.text_input("Cognome")
            st.session_state.email = st.text_input("Email")
            st.session_state.phone_number = st.text_input("Numero di telefono")
            st.session_state.password = st.text_input("Password", type="password")
            st.session_state.confirm_password = st.text_input("Conferma Password", type="password")

            if st.session_state.get("signup_error_operatore"):
                error_message, error_icon = st.session_state.signup_error_operatore
                st.error(error_message, icon=error_icon)
                st.session_state.signup_error_operatore = None

            if st.button("Registrati come Operatore"):
                if not all([st.session_state.med_register_code,
                    st.session_state.firstname,
                    st.session_state.lastname,
                    st.session_state.email,
                    st.session_state.phone_number,
                    st.session_state.password,
                    st.session_state.confirm_password]):
                    st.session_state.signup_error_operatore = ("Tutti i campi sono obbligatori.", "🚨")
                elif st.session_state.password != st.session_state.confirm_password:
                    st.session_state.signup_error_operatore = ("Le password non coincidono.", "🚨")
                else:
                    payload = {
                        "med_register_code": st.session_state.med_register_code,
                        "firstname": st.session_state.firstname,
                        "lastname": st.session_state.lastname,
                        "email": st.session_state.email,
                        "phone_number": st.session_state.phone_number,
                        "password": st.session_state.password
                    }

                    try:
                        response = requests.post(
                            "http://localhost:8001/signup/operator",
                            json=payload,
                            headers={"Content-Type": "application/json"}
                        )
                        if response.status_code == 200:
                                st.session_state.operator_signup_success = True  # FLAG di successo
                                st.rerun() # Torno alla home
                        else:
                            try:
                                error = response.json().get("detail", "Errore nella registrazione. Riprova.")
                            except ValueError:
                                error = f"Errore HTTP {response.status_code}: {response.text}"
                            st.session_state.signup_error_operatore = (error, "🚨")
                    except Exception as e:
                        st.session_state.signup_error_operatore = (f"Errore di connessione: {e}", "🚨")

    signup_dialog()
