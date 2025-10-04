# python -m uvicorn main:app  --reload --host 0.0.0.0 --port 8001
 
from fastapi import FastAPI, Depends, HTTPException, status
from db_ops import *
from validation import *
from contextlib import asynccontextmanager
from security import verify_password, create_access_token


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db() # All'avvio inizializzo il database
    yield  # to be executed at shutdown


app = FastAPI(title="Authentication Service", lifespan=lifespan)

"""
Mettendo come parametro della funzione della route un modello pydantic
fastapi in automatico a partire da una rihciesta post in cui c'è 
un json nel body, automaticamente dal file json crea un oggetto 
pydantic passando i dati del json. Se i dati non sono validi richiama un'eccezione (DA GESTIRE!!!)

quindi possiamo fare direttamente data.campo 
"""

@app.get("/", response_model=dict)
async def health():
    return {"Status": "T'appost! Auth Service running"}

@app.post("/signup/patient", response_model=dict)
async def signup(data: PatientSignupRequest, db: AsyncSession = Depends(get_db)):
    patient = await create_patient(data,db)
    return {"id": patient.id}

@app.post("/signup/operator", response_model=dict)
async def signup(data: OperatorSignupRequest, db: AsyncSession = Depends(get_db)):
    operator = await create_operator(data,db)
    return {"id": operator.id}


@app.post("/login/patient", response_model=dict)
async def login(data: PatientLoginRequest, db: AsyncSession = Depends(get_db)): 
    patient = await find_patient_by_social_number(data, db)
    # In FastAPI non serve necessariamente un try/except se sollevi direttamente un’eccezione come HTTPException
    # Se il paziente non esiste, viene sollevata un’HTTPException. 
    # FastAPI intercetta automaticamente questa eccezione e invia al client una risposta HTTP:

    if not verify_password(data.password, patient.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Password o codice fiscale errati"
        )


    token = create_access_token(patient.id, "patient")
    
    return {"access_token": token, "token_type": "bearer"}


@app.post("/login/operator", response_model=dict)
async def login(data: OperatorLoginRequest, db: AsyncSession = Depends(get_db)):
    operator = await find_operator_by_med_code(data, db)
 
    if not verify_password(data.password, operator.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Password o codice operatore errati"
        )

    token = create_access_token(operator.id, "operator")
    
    return {"access_token": token, "token_type": "bearer"}



'''
@app.post("/login")
def login(username: str, password: str):
    # validazione utente (qui finto)
    user_id = "user-123"
    access_token = create_access_token(user_id, scopes=["read:items"])
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/protected")
def protected_route(token: str):
    payload = verify_token(token)
    return {"msg": f"Benvenuto utente {payload['sub']}"}

# --- route ---
@app.get("/profilo")
def get_profilo(token_payload = Depends(require_paziente)):
    return {"msg": f"Accesso consentito a {token_payload['sub']} come paziente"}

@app.get("/cartella_clinica")
def get_cartella(token_payload = Depends(require_operatore)):
    return {"msg": f"Accesso consentito a {token_payload['sub']} come operatore sanitario"}
'''