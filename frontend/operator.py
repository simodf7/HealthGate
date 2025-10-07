"""
[FRONTEND] operator.py

Modulo per la schermata relativa all'operatore.
"""

import streamlit as st

def interface():
    st.header("ciao")

    if st.session_state.operator_login_success:
        st.toast(f"Rieccoti, {st.session_state.firstname} {st.session_state.lastname}!", icon="✅")
        st.session_state.operator_login_success = False  # Resetto il FLAG