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
    
    @st.dialog("Login")
    def login_dialog():
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Accedi"):
            if username == "admin" and password == "admin":  # Esempio di autenticazione semplice
                st.success("Login effettuato con successo!")
                st.session_state.view = "main"
            else:
                st.error("Credenziali non valide. Riprova.")
    login_dialog()