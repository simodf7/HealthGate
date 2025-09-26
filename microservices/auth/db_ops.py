from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from schemas import Base, Patient, Operator, Sex
from validation import *
from config import DATABASE_URL
from codicefiscale import codicefiscale
from security import hash_password
from fastapi import HTTPException, status


engine = create_async_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(bind=engine, class_= AsyncSession, expire_on_commit=False)

# Logica di inizializzazione con il database

# Definisce una funzione asincrona per inizializzare il database
async def init_db():
    # Apre una connessione asincrona al database in modalità transazionale
    async with engine.begin() as conn:
        # Esegue la funzione sincrona 'create_all' di SQLAlchemy
        # che crea tutte le tabelle definite nei modelli ereditati da Base
        # 'run_sync' permette di eseguire funzioni sincrone in contesto asincrono
        await conn.run_sync(Base.metadata.create_all)


# dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Logica di interazione con il database
# CRUD 

def create_patient(data: PatientSignupRequest, db: AsyncSession):
    patient = Patient(
        social_sec_number = codicefiscale.encode(
            lastname= data.lastname, 
            firstname= data.firstname,
            gender = "M" if data.sex == Sex.MALE else "F",
            birthdate =  data.birth_date.strftime("%d/%m/%Y"), 
            birthplace= data.birth_place
        ), 
        firstname = data.firstname, 
        lastname = data.lastname, 
        birth_date = data.birth_date, 
        sex = data.sex, 
        birth_place = data.birth_place, 
        hashed_password = hash_password(data.password)
    )
    db.add(patient)
    db.commit()
    db.refresh(patient)  # ottieni l'oggetto con id aggiornato
    return patient

def create_operator(data: OperatorSignupRequest, db: AsyncSession):
    operator = Operator(
        med_register_code = data.med_register_codes, 
        firstname = data.firstname, 
        lastname = data.lastname, 
        email = data.email, 
        phone_number = data.phone_number, 
        hashed_password = hash_password(data.password)
    )
    db.add(operator)
    db.commit()
    db.refresh(operator)  # ottieni l'oggetto con id aggiornato
    return operator

def find_patient_by_social_number(data: PatientLoginRequest, db: AsyncSession):
    patient = db.query(Patient).filter(Patient.social_sec_number == data.social_sec_number).first() 
    if patient is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Paziente non trovato"
        )

    return patient
    

def find_operator_by_med_code(data: OperatorLoginRequest, db: AsyncSession):
    operator = db.query(Operator).filter(Operator.med_register_code == data.med_register_code).first() 
    if operator is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Operatore non trovato"
        )

    return operator
    


