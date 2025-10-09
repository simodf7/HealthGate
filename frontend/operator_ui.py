"""
[FRONTEND] operator.py

Modulo per la schermata relativa all'operatore.
"""

import streamlit as st
from config import CSS_STYLE, PAGE_ICON

def interface():
    # Configurazione della pagina Streamlit
    st.set_page_config(
        page_title="Ricerca report", 
        layout="wide",
        page_icon=PAGE_ICON,
        initial_sidebar_state="collapsed"
    )

    st.markdown(CSS_STYLE, unsafe_allow_html=True)

    if st.session_state.patient_login_success:
        st.toast(f"Rieccoti, {st.session_state.firstname} {st.session_state.lastname}!", icon="✅", duration="short")
        st.session_state.patient_login_success = False  # Resetto il FLAG

    # === BARRA SUPERIORE ===
    col1, col2 = st.columns([3, 1])

    with col1:
        st.header("🪪 Ricerca report")

    with col2:
        subcol1, subcol2 = st.columns([2, 1])
        with subcol1:
            st.markdown(f"Ciao, **{st.session_state.firstname.upper()} {st.session_state.lastname.upper()}**!")
        with subcol2:
            if st.button("Logout"):
                st.rerun()
                main.interface()
    
    st.divider()