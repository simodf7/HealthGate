"""
[BACKEND/DATABASE] store_data.py

Modulo per la connessione e l'inserimento dei dati clinici strutturati in MongoDB.
Assume che ogni documento JSON rappresenti una singola visita o registrazione del paziente.
"""

from pymongo import MongoClient
from datetime import datetime
import certifi
from bson.objectid import ObjectId
import os

# Configurazione MongoDB (modificare se necessario)
MONGO_URI = "mongodb+srv://irispanaro07:bd_prog@cluster0.z6zdoju.mongodb.net/"
DB_NAME = "voice2care"
COLLECTION_NAME = "patient_records"

def connect_to_mongo():
    """
    Stabilisce la connessione a MongoDB.
    """
    try:
        client = MongoClient(MONGO_URI, tls=True, tlsCAFile=certifi.where())
        db = client[DB_NAME]
        collection = db[COLLECTION_NAME]
        print("✅ Connessione a MongoDB riuscita.")
        return collection
    except Exception as e:
        print(f"❌ Errore di connessione a MongoDB: {e}")
        return None

def load_plot_data(campo_x: str, campo_y: str, filtro: dict = None, sort_by: str = "timestamp", ascending: bool = True):
    """
    Carica coppie (X, Y) da MongoDB per plotting generico.

    :param campo_x: chiave da usare per l’asse X (può essere "timestamp" o un campo annidato es. "data.ora_accesso")
    :param campo_y: chiave da usare per l’asse Y
    :param filtro: dizionario con la query MongoDB (facoltativo)
    :param sort_by: campo di ordinamento (default: "timestamp")
    :param ascending: True = crescente, False = decrescente
    :return: tuple (x_values, y_values)
    """
    collection = connect_to_mongo()
    if collection is None:
        return [], []

    query = filtro or {}
    sort_direction = 1 if ascending else -1

    try:
        cursor = collection.find(query).sort(sort_by, sort_direction)
        x_values = []
        y_values = []

        for doc in cursor:
            # Accesso ricorsivo a campo annidato con dot notation
            def get_nested(doc, path):
                for p in path.split('.'):
                    doc = doc.get(p, None)
                    if doc is None:
                        return None
                return doc

            x = get_nested(doc, campo_x)
            y = get_nested(doc, campo_y)

            if x is not None and y is not None:
                x_values.append(x)
                y_values.append(y)

        return x_values, y_values

    except Exception as e:
        print(f"❌ Errore durante il caricamento dei dati per il plot: {e}")
        return [], []


def insert_patient_data(json_data):
    """
    Inserisce i dati strutturati del paziente nella collezione.
    Aggiunge automaticamente timestamp e ID paziente.
    """
    collection = connect_to_mongo()
    if collection is None:
        return False

    try:
        # Crea una copia per non modificare il dizionario originale in session_state
        document_to_insert = json_data.copy()
        
        # Estrai il codice fiscale dal JSON e aggiungilo come campo di primo livello
        codice_fiscale = document_to_insert.get("codice_fiscale", "unknown")
        document_to_insert["codice_fiscale"] = codice_fiscale
        
        # Aggiungi il timestamp di salvataggio come campo di primo livello
        document_to_insert["timestamp"] = datetime.now().strftime('%Y-%m-%dT%H-%M-%S')

        collection.insert_one(document_to_insert)
        #print("📥 Dati del paziente inseriti correttamente (struttura piatta).")
        return True
    except Exception as e:
        print(f"❌ Errore durante l'inserimento dei dati: {e}")
        return False

def get_patient_history(codice_fiscale):
    """
    Recupera la storia clinica di un dato paziente.
    """
    collection = connect_to_mongo()
    if collection is None:
        return []

    try:
        records = list(collection.find({"codice_fiscale": codice_fiscale}).sort("timestamp", -1))
        return records
    except Exception as e:
        print(f"❌ Errore durante il recupero della storia clinica: {e}")
        return []

def update_patient_data(codice_fiscale: str, timestamp: str, updated_fields: dict) -> bool:
    """
    Aggiorna i campi di un record clinico specifico di un paziente, identificato da patient_id e timestamp.
    :param patient_id: ID del paziente
    :param timestamp: timestamp del record da aggiornare
    :param updated_fields: dizionario con i campi da aggiornare e i nuovi valori
    :return: True se update ok, False altrimenti
    """
    collection = connect_to_mongo()
    if collection is None:
        return False

    query = {
        "codice_fiscale": codice_fiscale,
        "timestamp": timestamp
    }

    update_doc = {"$set": {}}
    # aggiorna solo i campi dentro "data"
    for key, value in updated_fields.items():
        update_doc["$set"][f"data.{key}"] = value

    try:
        result = collection.update_one(query, update_doc)
        if result.matched_count == 0:
            print("❌ Nessun documento trovato con i criteri specificati.")
            return False
        print("✅ Documento aggiornato correttamente.")
        return True
    except Exception as e:
        print(f"❌ Errore durante l'aggiornamento: {e}")
        return False
    
def reset_database():
    collection = connect_to_mongo()
    if collection is not None:
        collection.delete_many({})
        print("🧹 Database pulito.")

def delete_patient_data(record_id):
    """
    Elimina un documento dalla collezione pazienti usando il suo _id.
    """
    try:
        collection = connect_to_mongo()
        if collection is None:
            print("Errore: Impossibile connettersi a MongoDB.")
            return False
            
        # L'ID deve essere convertito in un oggetto ObjectId
        result = collection.delete_one({"_id": ObjectId(record_id)})
        
        if result.deleted_count == 1:
            print(f"Record con ID {record_id} eliminato con successo.")
            return True
        else:
            print(f"Nessun record trovato con ID {record_id}.")
            return False
            
    except Exception as e:
        print(f"Errore durante l'eliminazione del record: {e}")
        return False