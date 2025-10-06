# endpoint: id paziente, così fa query su  ongodb e stampa i dati del paziente, + stato 
# ingestion chiama report management che fa query mongodb
# i dati ottenuti dal report vengono uniti con l'info del sesso e dell'età e viene creata la storia


# decisione finale: decision passa tutto a report, tanto comunque decision si prende i sintomi


"""
generate_patient_pdf.py

Cerca un paziente in MongoDB tramite codice fiscale e genera
un PDF formattato usando direttamente le funzioni di pdf_generator.py.
"""

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
    """
    print(f"🔍 Ricerca paziente con codice fiscale: {cf}")
    paziente = cerca_paziente_per_codice_fiscale(cf)

    if not paziente:
        print(f"❌ Nessun paziente trovato con codice fiscale {cf}")
        return None

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
    codice_fiscale = input("Inserisci il codice fiscale del paziente: ").strip().upper()
    genera_pdf_paziente(codice_fiscale)
