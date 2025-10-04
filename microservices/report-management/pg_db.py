import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

PG_HOST = os.getenv("PG_HOST", "localhost")
PG_USER = os.getenv("PG_USER")
PG_PASSWORD = os.getenv("PG_PASSWORD")
PG_DBNAME = os.getenv("PG_DBNAME", "auth_db")

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
