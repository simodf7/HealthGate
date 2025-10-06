import os
import certifi
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv
from datetime import datetime
from pg_db import get_patient_anagrafica


load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "healthgate_db")

try:
    client = MongoClient(
        MONGO_URI,
        server_api=ServerApi('1'),
        tls=True,
        tlsAllowInvalidCertificates=False,
        tlsCAFile=certifi.where()
    )
    client.admin.command('ping')
    print("Connessione a MongoDB Atlas riuscita!")
except Exception as e:
    print("Errore connessione MongoDB:", e)

# Seleziona il database
db = client[MONGO_DB_NAME]

# Definisci le collection
reports = db["reports"]

# ----------------------------------------------------------
# FUNZIONI
# ----------------------------------------------------------

def get_reports_by_patient(patient_id: str):
    """Restituisce tutti i report clinici di un paziente ordinati per data."""
    return list(reports.find({"patient_id": patient_id}).sort("data", 1))


def save_report(patient_id: str, report_data: dict):
    """Salva un nuovo report clinico nel DB."""

    # converti date in stringhe
    for k, v in report_data.items():
        if hasattr(v, "isoformat"):  # funziona sia per date che datetime
            report_data[k] = v.isoformat()

    report_data["created_at"] = datetime.now().isoformat()
    reports.insert_one(report_data)
    return True


def save_report_with_anagrafica(patient_id: int, report_data: dict):
    """
    Salva un report clinico su MongoDB includendo l’anagrafica recuperata da PostgreSQL.
    """
    anagrafica = get_patient_anagrafica(patient_id)
    if anagrafica:
        # unisci i dati dell'anagrafica al report
        report_data.update(anagrafica)

    # chiama la save_report "normale"
    return save_report(patient_id, report_data)
