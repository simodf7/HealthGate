# ===================================================
# = SESSION STATE CONFIGURATION
# ===================================================

import streamlit as st

# Inizializzazione delle variabili di stato
def initialize_session_state():
    # Patient
    if "patient_signup_success" not in st.session_state:
        st.session_state.patient_signup_success = False
    if "patient_login_success" not in st.session_state:
        st.session_state.patient_login_success = False
    if "social_sec_number" not in st.session_state:
        st.session_state.social_sec_number = ""
    if "med_register_code" not in st.session_state:
        st.session_state.med_register_code = ""
    if "birth_date" not in st.session_state:
        st.session_state.birth_date = ""
    if "sex" not in st.session_state:
        st.session_state.sex = ""
    if "birth_place" not in st.session_state:
        st.session_state.birth_place = ""

    # Operator
    if "operator_signup_success" not in st.session_state:
        st.session_state.operator_signup_success = False
    if "operator_login_success" not in st.session_state:
        st.session_state.operator_login_success = False
    if "med_register_code" not in st.session_state:
        st.session_state.med_register_code = ""
    if "email" not in st.session_state:
        st.session_state.email = ""
    if "phone_number" not in st.session_state:
        st.session_state.phone_number = ""

    # Patient & Operator
    if "firstname" not in st.session_state:
        st.session_state.firstname = ""
    if "lastname" not in st.session_state:
        st.session_state.lastname = ""
    if "username" not in st.session_state:
        st.session_state.username = ""
    if "login_password" not in st.session_state:
        st.session_state.login_password = ""
    if "signup_password" not in st.session_state:
        st.session_state.signup_password = ""
    if "signup_confirm_password" not in st.session_state:
        st.session_state.signup_confirm_password = ""

    # Sezione Report
    if "pdf_to_download" not in st.session_state:
        st.session_state.pdf_to_download = None
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 1

    # Generic
    if "view" not in st.session_state:
        st.session_state.view = "home"



# ===================================================
# = LOGOUT FORM
# ===================================================

# Dialogo di logout
@st.dialog("Logout")
def logout_form():
    # Contenitore principale centrato
    with st.container():
        if st.session_state.sex == "M":
            st.write(
                """
                <div style='text-align: center;'>
                    <p style='font-size: 1.2rem; margin-bottom: 1.5rem;'>Sei sicuro di voler uscire?</p>
                </div>
                """,
                unsafe_allow_html=True
            )
        elif st.session_state.sex == "F":
            st.write(
                """
                <div style='text-align: center;'>
                    <p style='font-size: 1.2rem; margin-bottom: 1.5rem;'>Sei sicura di voler uscire?</p>
                </div>
                """,
                unsafe_allow_html=True
            )

        # Colonne centrate (spazi laterali + bottoni centrali)
        col_spacer1, col1, col2, col_spacer2 = st.columns([3, 2, 2, 3])

        with col1:
            if st.button("No", key="patient-logout-no", type="secondary", use_container_width=True):
                st.rerun()

        with col2:
            if st.button("Sì", key="patient-logout-yes", type="primary", use_container_width=True):
                st.session_state.view = "home"
                initialize_session_state()
                st.rerun()
        


# ===================================================
# = ICON OPTIONS
# ===================================================

PAGE_ICON = "./logo/logo-3-squared-nobg.png"
PAGE_ICON_OLD = "🚑"



# ===================================================
# = CSS OPTIONS
# ===================================================

CSS_STYLE = """
<style>
.main-header {
    text-align: left;
    color: #3232a8;
    font-size: 3rem;
    font-weight: bold;
    margin-bottom: 2rem;
    text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
}

.stButton > button:not([kind="secondary"]) {
    background: #42a9df;
    color: white;
    border: none;
    border-radius: 10px;
    padding: 0.6rem 1.5rem;
    font-size: 1.1rem;
    font-weight: 600;
    transition: all 0.3s ease;
    box-shadow: 0 2px 10px rgba(0,0,0,0.2);
}

.stButton > button[kind="secondary"] {
    background: white;
    color: black;
    border: none;
    border-radius: 10px;
    padding: 0.6rem 1.5rem;
    font-size: 1.1rem;
    font-weight: 600;
    transition: all 0.3s ease;
    box-shadow: 0 2px 10px rgba(0,0,0,0.2);
}

.stDownloadButton > button {
    background: #2ec400;
    color: white;
    border: none;
    border-radius: 10px;
    padding: 0.6rem 1.5rem;
    font-size: 1.1rem;
    font-weight: 600;
    transition: all 0.3s ease;
    box-shadow: 0 2px 10px rgba(0,0,0,0.2);
}

.stButton > button:hover:not([kind="secondary"]) {
    background: #05a0e3;
    color: #ffffff;
    transform: translateY(-2px);
    box-shadow: 0 2px 15px rgba(0,0,0,0.3);
}

.stButton > button:hover[kind="secondary"] {
    background: #6290a8;
    color: #ffffff;
    transform: translateY(-2px);
    box-shadow: 0 2px 15px rgba(0,0,0,0.3);
}

.stDownloadButton > button:hover {
    background: #008f0c;
    color: #ffffff;
    transform: translateY(-2px);
    box-shadow: 0 2px 15px rgba(0,0,0,0.3);
}
</style>
"""

CSS_STYLE_OLD1 = """
<style>
.main-header {
    text-align: left;
    color: #3232a8;
    font-size: 3rem;
    font-weight: bold;
    margin-bottom: 2rem;
    text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
}

.stButton > button {
    background: #32a860;
    color: white;
    border: none;
    border-radius: 10px;
    padding: 0.6rem 1.5rem;
    font-size: 1.1rem;
    font-weight: 600;
    transition: all 0.3s ease;
    box-shadow: 0 4px 15px rgba(0,0,0,0.2);
}

.stButton > button:hover {
    background: #74c3a4;
    color: #ffffff;
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(0,0,0,0.3);
}
</style>
"""

CSS_STYLE_OLD2 = """
<style>
.main-header {
    text-align: left;
    color: #2E86AB;
    font-size: 3rem;
    font-weight: bold;
    margin-bottom: 2rem;
    text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
}

.stButton > button {
    background: #52aa8a;
    color: white;
    border: none;
    border-radius: 10px;
    padding: 0.6rem 1.5rem;
    font-size: 1.1rem;
    font-weight: 600;
    transition: all 0.3s ease;
    box-shadow: 0 4px 15px rgba(0,0,0,0.2);
}

.stButton > button:hover {
    background: #74c3a4;
    color: #ffffff;
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(0,0,0,0.3);
}
.home-button > button:hover {
    background: #4fa070;
}
.proceed-button > button:hover {
    background: #53e4ff;
}
</style>
"""



# ===================================================
# = NAVBAR OPTIONS
# ===================================================

NAVBAR_PAGES = ["Home", "Library", "Tutorials", "Development", "Download"]

NAVBAR_STYLES = {
    "nav": {
        "background-color": "#3232a8",
    },
    "div": {
        "max-width": "32rem",
    },
    "span": {
        "border-radius": "0.5rem",
        "color": "rgb(49, 51, 63)",
        "margin": "0 0.125rem",
        "padding": "0.4375rem 0.625rem",
    },
    "active": {
        "background-color": "rgba(255, 255, 255, 0.25)",
    },
    "hover": {
        "background-color": "rgba(255, 255, 255, 0.35)",
    },
}