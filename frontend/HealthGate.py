# python -m streamlit run c:\HealthGate\HealthGate.py
"""
[FRONTEND] HealtGate.py

Modulo principale per l'applicazione HealthGate.
"""

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
elif st.session_state.view == "patient-login" or st.session_state.view == "operator-login":
    login.interface()
elif st.session_state.view == "signup":
    signup.interface()
elif st.session_state.view == "patient-logged-symptoms":
    patient_ui.symptom_interface()
elif st.session_state.view == "patient-logged-reports":
    patient_ui.reports_interface()
elif st.session_state.view == "operator-logged":
    operator_ui.interface()