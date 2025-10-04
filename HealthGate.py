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
import operator
import patient
import streamlit as st

if "view" not in st.session_state:
    st.session_state.view = "home"

# Avvio dell'interfaccia principale
if st.session_state.view == "home":
    main.interface()
elif st.session_state.view == "patient-logged":
    patient.interface()
elif st.session_state.view == "operator-logged":
    operator.interface()