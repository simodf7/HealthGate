from typing import Optional
from pydantic import BaseModel



class Report(BaseModel):
    _id: str  
    social_sec_number: str
    patient_id: int
    date: str
    motivazione: str
    diagnosi: str 
    sintomi: str 
    trattamento: str 
    created_at: str 


class CreateReportRequest(BaseModel):
    patient_id: int
    social_sec_number: str
    date: str  # data del report
    diagnosi: Optional[str] = None
    sintomi: Optional[str] = None
    trattamento: Optional[str] = None


class CreateReportResponse(BaseModel):
    success: bool
    report_id: Optional[str] = None
    error: Optional[str] = None


class UpdateRequest(BaseModel):
    report_id: str 
    diagnosi: str
    trattamento: str

