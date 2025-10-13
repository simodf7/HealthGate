import certifi
from fastapi import HTTPException
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from config import MONGO_DB_NAME, MONGO_URI
from datetime import datetime
from bson import ObjectId

async def connect_db(): 
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


        db = client[MONGO_DB_NAME]

        return db 
    except Exception as e:
        print("Errore connessione MongoDB:", e)



    

# ----------------------------------------------------------
# FUNZIONI
# ----------------------------------------------------------

async def get_reports(collection):
    return list(collection.find())


async def get_report_by_id(collection, report_id: str):
    oid = ObjectId(report_id)
    return collection.find_one({"_id": oid})

async def get_reports_by_patient_id(collection, patient_id: int):
    """Restituisce tutti i report clinici di un paziente ordinati per data."""
    l = list(collection.find({"patient_id": patient_id}).sort("data", 1))
    for r in l:
        if "_id" in r and isinstance(r["_id"], ObjectId):
            r["id"] = str(r["_id"])
    print(l)
    return l

async def get_reports_by_patient_ssn(collection, social_sec_number : str):
    """Restituisce tutti i report clinici di un paziente ordinati per data."""
    l = list(collection.find({"social_sec_number": social_sec_number}).sort("data", 1))
    for r in l:
        if "_id" in r and isinstance(r["_id"], ObjectId):
            r["id"] = str(r["_id"])
    print(l)
    return l

async def modify_report(collection, report_id:str, diagnosi:str, trattamento:str):
    oid = ObjectId(report_id)
    result = collection.update_one({"_id": oid}, {"$set": {"diagnosi": diagnosi, "trattamento": trattamento}})
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Report non trovato")

    return collection.find_one({"_id": oid})
    

async def save_report(collection, report_data: dict):
    """Salva un nuovo report clinico nel DB e restituisce l'ID del report."""
    
    # converti date in stringhe
    for k, v in report_data.items():
        if hasattr(v, "isoformat"):  # funziona sia per date che datetime
            report_data[k] = v.isoformat()

    report_data["created_at"] = datetime.now().isoformat()
    
    # Inserisci il documento e ottieni il risultato
    result = collection.insert_one(report_data)
    
    # Restituisci l'ID del documento inserito come stringa
    return str(result.inserted_id)
