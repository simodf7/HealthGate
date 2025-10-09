import psycopg2
import os
from typing import Optional, Dict
from dotenv import load_dotenv

load_dotenv()

## secondo me sostituire con richiamare la route di auth service, ora te la modifico


PG_HOST = os.getenv("PG_HOST", "localhost")
PG_USER = os.getenv("PG_USER")
PG_PASSWORD = os.getenv("PG_PASSWORD")
PG_DBNAME = os.getenv("PG_DBNAME", "auth_db")
DATABASE_URL = os.getenv("DATABASE_URL")

def get_db_connection():
    """Crea una connessione al database PostgreSQL"""
    return psycopg2.connect(DATABASE_URL)

def get_patient_anagrafica(patient_id: int):
    """Recupera dati anagrafici da PostgreSQL"""
    conn = psycopg2.connect(
        host=PG_HOST,
        user=PG_USER,
        password=PG_PASSWORD,
        dbname=PG_DBNAME
    )
    cur = conn.cursor()
    cur.execute("""
        SELECT id, social_sec_number, firstname, lastname, birth_date, sex
        FROM patients WHERE id = %s
    """, (patient_id,))
    row = cur.fetchone()
    cur.close()
    conn.close()

    if row:
        keys = ["id", "social_sec_number", "firstname", "lastname", "birth_date", "sex"]
        return dict(zip(keys, row))
    else:
        return None

def get_patient_id_by_cf(social_sec_number: str) -> Optional[int]:
    """
    Cerca il patient_id dal codice fiscale in PostgreSQL
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = "SELECT id FROM patients WHERE social_sec_number = %s"
        cursor.execute(query, (social_sec_number,))
        result = cursor.fetchone()
        
        if result:
            patient_id = result[0]
            return patient_id
        else:
            print(f"❌ Nessun paziente trovato con CF: {social_sec_number}")
            return None
            
    except Exception as e:
        print(f"❌ Errore nella ricerca patient_id per CF {social_sec_number}: {str(e)}")
        return None
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()