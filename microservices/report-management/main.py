# endpoint: id paziente, così fa query su mongodb e stampa i dati del paziente, + stato
# ingestion chiama report management che fa query mongodb
# i dati ottenuti dal report vengono uniti con l'info del sesso e dell'età e viene creata la storia

# decisione finale: decision passa tutto a report, tanto comunque decision si prende i sintomi

# Exec:
# cd microservices/report-management
# set PYTHONUTF8=1
# python main.py

'''
[REPORT] main.py

Cerca un paziente in MongoDB tramite codice fiscale e genera
un PDF formattato usando direttamente le funzioni di pdf_generator.py.
I dati anagrafici vengono presi da st.session_state.
'''

import streamlit as st
from mongodb import reports
from pdf_generator import genera_scheda_pdf_da_json
from datetime import datetime


def cerca_paziente_per_codice_fiscale(cf: str):
    """
    Cerca il paziente più recente in MongoDB tramite codice fiscale.
    """
    return reports.find_one(
        {"social_sec_number": cf},
        sort=[("created_at", -1)]
    )


def genera_pdf_paziente(cf: str):
    """
    Recupera i dati del paziente e genera il PDF formattato
    utilizzando direttamente pdf_generator.genera_scheda_pdf_da_json.
    I dati anagrafici (firstname, lastname, birth_date, sex) vengono
    presi da st.session_state invece che da MongoDB.
    """
    print(f"🔍 Ricerca paziente con codice fiscale: {cf}")
    paziente = cerca_paziente_per_codice_fiscale(cf)

    if not paziente:
        print(f"❌ Nessun paziente trovato con codice fiscale {cf}")
        return None

    # Sovrascrivi i dati anagrafici con quelli di session_state
    paziente['firstname'] = st.session_state.firstname
    paziente['lastname'] = st.session_state.lastname
    paziente['birth_date'] = st.session_state.birth_date
    paziente['sex'] = st.session_state.sex

    print(f"✅ Paziente trovato: {paziente.get('firstname', '')} {paziente.get('lastname', '')}")

    # Genera PDF usando il sistema interno di pdf_generator.py
    try:
        risultato = genera_scheda_pdf_da_json(dati_json=paziente, mantieni_html=False)

        if risultato["success"]:
            print(f"🎉 PDF generato con successo: {risultato['pdf']}")
            return risultato["pdf"]
        else:
            print(f"❌ Errore nella generazione PDF: {risultato['error']}")
            return None

    except Exception as e:
        print(f"❌ Errore critico durante la generazione PDF: {e}")
        return None


# ================== ESEMPIO D'USO ==================
if __name__ == "__main__":
    # Prende il codice fiscale direttamente dal session_state di Streamlit
    # codice_fiscale = st.session_state.social_sec_number.strip().upper()
    
    # Per il test, simula i dati di session_state
    if 'firstname' not in st.session_state:
        st.session_state.firstname = "Ale"
        st.session_state.lastname = "Campanella"
        st.session_state.birth_date = "2001-08-09"
        st.session_state.sex = "F"
    
    codice_fiscale = "CMPLAE01M49F839Z"
    if not codice_fiscale:
        print("❌ Codice fiscale non presente in st.session_state.social_sec_number")
    else:
        genera_pdf_paziente(codice_fiscale)