# python -m uvicorn auth_service:app --reload --host 0.0.0.0 --port 8001

from fastapi import Depends, FastAPI, HTTPException, status
from datetime import datetime
from validation import *
from db_ops import *
from security import *
from contextlib import asynccontextmanager


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

    #return {"access_token": token, "token_type": "bearer"}


    return {
        "access_token": token,
        "token_type": "bearer",
        "patient_id": patient.id,
        "social_sec_number": patient.social_sec_number,
        "firstname": patient.firstname,
        "lastname": patient.lastname,
        "birth_date": patient.birth_date.isoformat(),  # converto la data in stringa ISO
        "sex": patient.sex,
        "birth_place": patient.birth_place
    }


@app.post("/login/operator", response_model=dict)
async def login(data: OperatorLoginRequest, db: AsyncSession = Depends(get_db)): 
    operator = await find_operator_by_med_code(data, db)

    if not verify_password(data.password, operator.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Password o codice fiscale errati"
        ) 
    
    token = create_access_token(operator.id, "operator")


    return {
        "access_token": token,
        "token_type": "bearer",
        "operator_id": operator.id,
    }



@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Authentication Service",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/user/profile/{patient_id}")
async def get_user_profile(patient_id:int, db: AsyncSession = Depends(get_db)):
    """
    Endpoint per ottenere un profilo utente da un operatore (esempio aggiuntivo)
    """
    patient = await find_patient_by_id(patient_id, db)

    return {
        "patient_id": patient.id,
        "social_sec_number": patient.social_sec_number,
        "firstname": patient.firstname,
        "lastname": patient.lastname,
        "birth_date": patient.birth_date.isoformat(),  # converto la data in stringa ISO
        "sex": patient.sex,
        "birth_place": patient.birth_place
    }




