from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String, Date, Enum
import enum

Base = declarative_base()

class Sex(enum.Enum):
    male = "M"
    female = "F" 
    

class Patient(Base):
    __tablename__ = "patients"
    id = Column(Integer, primary_key=True, autoincrement=True)
    social_sec_number = Column(String(16), nullable=False, unique=True, index=True)
    firstname = Column(String(30), nullable=False) 
    lastname = Column(String(30), nullable=False)
    birth_date = Column(Date, nullable=False)
    sex = Column(Enum(Sex), nullable=False)
    birth_place = Column(String(100), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    

class Operator(Base):
    __tablename__ = "operators"
    id = Column(Integer, primary_key=True, autoincrement=True)
    med_register_code = Column(String(20), unique=True)
    firstname = Column(String(30), nullable=False) 
    lastname = Column(String(30), nullable=False)
    email = Column(String(255), nullable=False, unique=True)
    phone_number = Column(String(20), nullable=False, unique=True)
    hashed_password = Column(String(255), nullable=False)