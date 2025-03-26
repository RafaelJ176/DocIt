from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class PatientProfile(BaseModel):
    user_id: str
    medical_history: Optional[List[dict]] = []
    allergies: Optional[List[str]] = []
    medications: Optional[List[dict]] = []
    emergency_contact: Optional[dict] = None
    insurance_info: Optional[dict] = None
    blood_type: Optional[str] = None
    height: Optional[float] = None
    weight: Optional[float] = None
    last_checkup: Optional[datetime] = None

class PatientCreate(PatientProfile):
    pass

class Patient(PatientProfile):
    id: str
    created_at: datetime
    updated_at: datetime
    assigned_doctors: List[str] = []
    test_history: List[str] = []

    class Config:
        from_attributes = True 