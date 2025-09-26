import os
import time
import uuid
import jwt  # pyjwt
import bcrypt
from fastapi import FastAPI, HTTPException

SECRET_KEY = os.getenv("SECRET_KEY", "fallback-supersegreto")
ALGORITHM = "HS256"
ACCESS_EXP = 60 * 15  # 15 minuti

def create_access_token(user_id: str, role: str):
    # Otteniamo il timestamp attuale
    now = int(time.time())

    # Definiamo il contenuto (payload) del JWT:
    payload = {
        "sub": user_id,              # "subject": identifica l'utente (es. user id)
        "iat": now,                  # "issued at": quando è stato generato il token
        "exp": now + ACCESS_EXP,     # "expiration": quando il token scadrà (ora + durata in sec.)
        "jti": str(uuid.uuid4()),    # "JWT ID": identificativo unico del token (utile per blacklist)
        "scope": role                # "scope": ruolo dell’utente (Paziente o Operatore Sanitario)
    }

    # Firmiamo il token con la SECRET_KEY e algoritmo scelto (HS256 in questo caso)
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    # Ritorniamo il token JWT pronto da mandare al client
    return token

# Hashing delle password

# Funzione per hashare la password
def hash_password(password: str) -> str:
    # Converte la password in bytes
    password_bytes = password.encode('utf-8')

    # Genera un salt sicuro
    salt = bcrypt.gensalt()

    # Crea l'hash della password
    hashed = bcrypt.hashpw(password_bytes, salt)
    
    # Ritorna l'hash come stringa
    return hashed.decode('utf-8')

# Funzione per verificare la password
def verify_password(password: str, hashed: str) -> bool:
    # Confronta la password in chiaro con l'hash
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

# Esempio d'uso hashing
password = "SuperSegreta123!"
hashed_pw = hash_password(password)
print("Password hashata:", hashed_pw)

# Verifica
is_valid = verify_password("SuperSegreta123!", hashed_pw)
print("Password corretta?", is_valid)

# ALTERNATIVA: verificare qui il jwt e non all'API Gateway

'''
# --- verifica token base ---
def verify_token(token: str):
    try:
        # Decodifica il token e verifica:
        # - la firma (usando SECRET_KEY)
        # - l’algoritmo (HS256)
        # - la scadenza ("exp")
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        # Se tutto è valido ritorna il payload (cioè i dati del token)
        return payload

    except jwt.ExpiredSignatureError:
        # Se il token è scaduto, restituiamo errore HTTP 401
        raise HTTPException(status_code=401, detail="Token scaduto")

    except jwt.InvalidTokenError:
        # Se la firma è sbagliata, il token è manomesso o non valido, 401
        raise HTTPException(status_code=401, detail="Token non valido")

# --- verifica token e controllo ruolo generico ---
def verify_token_with_role(token: str, required_role: str):
    """
    Verifica firma e scadenza del token e controlla che l'utente
    abbia il ruolo richiesto.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token scaduto")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Token non valido")

    # Controllo ruolo
    if payload.get("scope") != required_role:
        raise HTTPException(status_code=403, detail="Permesso negato")

    return payload
'''