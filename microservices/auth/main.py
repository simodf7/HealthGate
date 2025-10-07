# python -m uvicorn auth_service:app --reload --host 0.0.0.0 --port 8001

import requests
import json
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from typing import Optional, Dict, Any
import jwt
from datetime import datetime, timedelta
import psycopg2
from config import DATABASE_URL  # Assicurati di avere la configurazione PostgreSQL

# Configurazione
REPORT_MANAGEMENT_URL = "http://localhost:8005"
JWT_SECRET = "your-secret-key"  # Usa una variabile d'ambiente in produzione
JWT_ALGORITHM = "HS256"

class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    success: bool
    token: Optional[str] = None
    user_data: Optional[Dict] = None
    error: Optional[str] = None

app = FastAPI(title="Authentication Service")

def get_db_connection():
    """Crea una connessione al database PostgreSQL"""
    return psycopg2.connect(DATABASE_URL)

def verify_credentials_in_postgres(username: str, password: str) -> Optional[Dict[str, Any]]:
    """
    Verifica le credenziali in PostgreSQL e restituisce i dati utente completi
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Query per verificare credenziali e ottenere dati completi
        query = """
        SELECT 
            p.id as patient_id,
            p.social_sec_number,
            p.firstname,
            p.lastname, 
            p.birth_date,
            p.sex,
            u.username,
            u.role,
            u.email
        FROM patients p
        JOIN users u ON p.id = u.patient_id
        WHERE u.username = %s AND u.password_hash = %s
        """
        
        cursor.execute(query, (username, password))  # In produzione, usa hash delle password!
        result = cursor.fetchone()
        
        if result:
            # Costruisci il dizionario con i dati utente
            user_data = {
                "patient_id": result[0],
                "social_sec_number": result[1],
                "firstname": result[2],
                "lastname": result[3],
                "birth_date": result[4].isoformat() if result[4] else None,
                "sex": result[5],
                "username": result[6],
                "role": result[7],
                "email": result[8]
            }
            return user_data
        
        return None
        
    except Exception as e:
        print(f"❌ Errore durante la verifica credenziali: {str(e)}")
        return None
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

def send_patient_data_to_report_service(patient_data: Dict) -> bool:
    """
    Invia i dati del paziente al Report Management Service dopo il login
    """
    try:
        # Prepara i dati per il report service
        sync_data = {
            "social_sec_number": patient_data.get("social_sec_number"),
            "firstname": patient_data.get("firstname"),
            "lastname": patient_data.get("lastname"),
            "birth_date": patient_data.get("birth_date"),
            "sex": patient_data.get("sex"),
            "patient_id": patient_data.get("patient_id")
        }
        
        print(f"🔄 Invio dati a Report Service: {sync_data}")
        
        # Invia i dati al Report Management Service
        response = requests.post(
            f"{REPORT_MANAGEMENT_URL}/patient/sync",
            json=sync_data,
            headers={"Content-Type": "application/json"},
            timeout=10  # Timeout di 10 secondi
        )
        
        if response.status_code == 200:
            response_data = response.json()
            if response_data.get("success"):
                print(f"✅ Dati paziente sincronizzati con Report Service per CF: {patient_data.get('social_sec_number')}")
                return True
            else:
                print(f"⚠️ Sincronizzazione fallita: {response_data.get('error')}")
                return False
        else:
            print(f"⚠️ Errore HTTP nella sincronizzazione: {response.status_code} - {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Errore di connessione al Report Service: {str(e)}")
        return False
    except Exception as e:
        print(f"❌ Errore nell'invio dati a Report Service: {str(e)}")
        return False

def generate_jwt_token(user_data: Dict) -> str:
    """
    Genera un token JWT per l'utente
    """
    try:
        # Dati da includere nel token
        payload = {
            "user_id": user_data.get("patient_id"),
            "username": user_data.get("username"),
            "role": user_data.get("role"),
            "social_sec_number": user_data.get("social_sec_number"),
            "exp": datetime.utcnow() + timedelta(hours=24)  # Scadenza 24 ore
        }
        
        token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
        return token
        
    except Exception as e:
        print(f"❌ Errore nella generazione del token JWT: {str(e)}")
        raise

@app.post("/login", response_model=LoginResponse)
async def login(credentials: LoginRequest):
    """
    Endpoint di login che dopo l'autenticazione sincronizza i dati con Report Management
    """
    try:
        print(f"🔐 Tentativo di login per: {credentials.username}")
        
        # 1. Verifica credenziali nel database PostgreSQL
        user_data = verify_credentials_in_postgres(credentials.username, credentials.password)
        
        if not user_data:
            print(f"❌ Login fallito per: {credentials.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenziali non valide"
            )
        
        print(f"✅ Credenziali verificate per: {user_data.get('firstname')} {user_data.get('lastname')}")
        
        # 2. Se è un paziente, sincronizza i dati con Report Management
        if user_data.get("role") == "patient":
            print("🔄 Sincronizzazione con Report Management Service...")
            sync_success = send_patient_data_to_report_service(user_data)
            
            if sync_success:
                user_data["report_service_sync"] = True
                print("✅ Sincronizzazione Report Service completata")
            else:
                user_data["report_service_sync"] = False
                print("⚠️ Attenzione: sincronizzazione Report Service fallita, ma login procede")
        
        # 3. Genera token JWT
        token = generate_jwt_token(user_data)
        
        # 4. Prepara risposta (rimuovi dati sensibili se necessario)
        response_data = {
            "patient_id": user_data.get("patient_id"),
            "social_sec_number": user_data.get("social_sec_number"),
            "firstname": user_data.get("firstname"),
            "lastname": user_data.get("lastname"),
            "birth_date": user_data.get("birth_date"),
            "sex": user_data.get("sex"),
            "username": user_data.get("username"),
            "role": user_data.get("role"),
            "email": user_data.get("email"),
            "report_service_sync": user_data.get("report_service_sync", False)
        }
        
        print(f"🎉 Login completato con successo per: {user_data.get('firstname')} {user_data.get('lastname')}")
        
        return LoginResponse(
            success=True,
            token=token,
            user_data=response_data
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Errore durante il login: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Errore interno: {str(e)}"
        )

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Authentication Service",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/user/profile/{user_id}")
async def get_user_profile(user_id: int):
    """
    Endpoint per ottenere il profilo utente (esempio aggiuntivo)
    """
    try:
        # Implementa la logica per recuperare il profilo utente
        # ...
        return {"message": "Profilo utente"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Errore: {str(e)}")