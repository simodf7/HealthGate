from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import Column, Integer, String, Date, Enum
import enum
from config import DATABASE_URL

engine = create_async_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

Base = declarative_base()

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


class Sex(enum.Enum):
    male = "m"
    female = "f" 
    

class Patient(Base):
    __tablename__ = "patients"
    id = Column(Integer, primary_key=True, autoincrement=True)
    social_sec_number = Column(String(16), nullable=False, unique=True, index=True)
    name = Column(String(30), nullable=False) 
    surname = Column(String(30), nullable=False)
    birth_date = Column(Date, nullable=False)
    sex = Column(Enum(Sex), nullable=False)
    birth_place = Column(String(100), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    

class Operator(Base):
    __tablename__ = "operators"
    id = Column(Integer, primary_key=True, autoincrement=True)
    med_register_code = Column(String(20), unique=True)
    name = Column(String(30), nullable=False) 
    surname = Column(String(30), nullable=False)
    email = Column(String(255), nullable=False, unique=True)
    phone_number = Column(String(20), nullable=False, unique=True)
    hashed_password = Column(String(255), nullable=False)