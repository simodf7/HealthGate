from typing import Optional
from pydantic import BaseModel



class Report(BaseModel):
    id: str  
    social_sec_number: str
    patient_id: int
    date: str
    motivazione: Optional[str] = None 
    diagnosi: Optional[str] = None  
    sintomi: str 
    trattamento: str 
    created_at: str 


class CreateReportRequest(BaseModel):
    patient_id: int
    social_sec_number: str
    date: str  # data del report
    motivazione: str
    diagnosi: Optional[str] = None
    sintomi: str 
    trattamento: Optional[str] = None


class CreateReportResponse(BaseModel):
    success: bool
    report_id: Optional[str] = None
    error: Optional[str] = None


class UpdateRequest(BaseModel):
    report_id: str 
    diagnosi: str
    trattamento: str

