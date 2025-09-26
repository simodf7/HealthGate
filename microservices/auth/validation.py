from pydantic import BaseModel, EmailStr, Field, field_validator
from datetime import date
from enum import Enum
from typing import Optional
from typing_extensions import Annotated
import re


class SexEnum(str, Enum):
    male = "M"
    female = "F"


class PatientSignupRequest(BaseModel):
    firstname: Annotated[str, Field(min_length=2, max_length=30)]
    lastname: Annotated[str, Field(min_length=2, max_length=30)]
    birth_date: date
    sex: SexEnum
    birth_place: Annotated[str, Field(min_length=2, max_length=100)]
    password: Annotated[str, Field(min_length=8, max_length=128)]

    # Validazione password
    @field_validator("password")
    def password_complexity(cls, v: str) -> str:
        if not re.search(r"[A-Z]", v):
            raise ValueError("La password deve contenere almeno una lettera maiuscola")
        if not re.search(r"\d", v):
            raise ValueError("La password deve contenere almeno un numero")
        return v

    # Validazione data di nascita
    @field_validator("birth_date")
    def birth_date_not_future(cls, v: date) -> date:
        if v > date.today():
            raise ValueError("La data di nascita non può essere futura")
        return v


class OperatorSignupRequest(BaseModel):
    med_register_code: Optional[Annotated[str, Field(min_length=1, max_length=20)]]
    firstname: Annotated[str, Field(min_length=2, max_length=30)]
    lastname: Annotated[str, Field(min_length=2, max_length=30)]
    email: EmailStr
    phone_number: Annotated[str, Field(min_length=7, max_length=20)]
    password: Annotated[str, Field(min_length=8, max_length=128)]

    @field_validator("password")
    def password_complexity(cls, v: str) -> str:
        if not re.search(r"[A-Z]", v):
            raise ValueError("La password deve contenere almeno una lettera maiuscola")
        if not re.search(r"\d", v):
            raise ValueError("La password deve contenere almeno un numero")
        return v
    


class PatientLoginRequest(BaseModel):
    social_sec_number: str 
    password: str


class OperatorLoginRequest(BaseModel):
    med_register_code: str 
    password: str

