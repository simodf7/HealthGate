# python -m streamlit run c:\HealthGate\HealthGate.py
"""
[FRONTEND] HealtGate.py

Modulo principale per l'applicazione HealthGate.
"""

import sys
import os

# Ottieni la directory del file corrente
current_dir = os.path.dirname(os.path.abspath(__file__))

# Aggiungi la sottocartella "frontend" al path
frontend_path = os.path.join(current_dir, 'frontend')
sys.path.append(frontend_path)

import main
import patient_ui
import operator_ui
import login
import signup
import streamlit as st

if "view" not in st.session_state:
    st.session_state.view = "home"

# Avvio dell'interfaccia principale
if st.session_state.view == "home":
    main.interface()
elif st.session_state.view == "patient-login":
    login.login_interface()
elif st.session_state.view == "operator-login":
    login.login_interface()
elif st.session_state.view == "signup":
    signup.signup_interface()
elif st.session_state.view == "patient-logged":
    patient_ui.interface()
elif st.session_state.view == "operator-logged":
    operator_ui.interface()