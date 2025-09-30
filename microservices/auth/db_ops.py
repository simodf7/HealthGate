from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from schemas import Base, Patient, Operator
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
async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        await db.close()

# Logica di interazione con il database
# CRUD 
async def create_patient(data: PatientSignupRequest, db: AsyncSession):
    patient = Patient(
        social_sec_number = codicefiscale.encode(
            lastname= data.lastname, 
            firstname= data.firstname,
            gender = data.sex,
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
    try:
        await db.commit()
        await db.refresh(patient)
        return patient
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=400,
            detail="Un paziente con gli stessi dati anagrafici esiste già."
        )

async def create_operator(data: OperatorSignupRequest, db: AsyncSession):
    operator = Operator(
        med_register_code = data.med_register_code, 
        firstname = data.firstname, 
        lastname = data.lastname, 
        email = data.email, 
        phone_number = data.phone_number, 
        hashed_password = hash_password(data.password)
    )
    db.add(operator)
    await db.commit()
    await db.refresh(operator)
    return operator

async def find_patient_by_social_number(data: PatientLoginRequest, db: AsyncSession): # non si puo piu usare db.query ma db.execute
    result = await db.execute(
        select(Patient).where(Patient.social_sec_number == data.social_sec_number)
    )

    # prende il primo valore della prima colonna del risultato, oppure None se non trova niente.
    # equivalente del first 
    patient = result.scalar_one_or_none()  
    if patient is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Paziente non trovato"
        )

    return patient
    

async def find_operator_by_med_code(data: OperatorLoginRequest, db: AsyncSession):
    result = await db.execute(
        select(Operator).where(Operator.med_register_code == data.med_register_code)
    )
    operator = result.scalar_one_or_none() 
    if operator is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Operatore non trovato"
        )

    return operator