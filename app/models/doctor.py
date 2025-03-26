from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class DoctorProfile(BaseModel):
    user_id: str
    specialization: str
    license_number: str
    years_of_experience: Optional[int] = None
    education: Optional[List[dict]] = []
    certifications: Optional[List[str]] = []
    availability: Optional[dict] = None
    department: Optional[str] = None

class DoctorCreate(DoctorProfile):
    pass

class Doctor(DoctorProfile):
    id: str
    created_at: datetime
    updated_at: datetime
    patients: List[str] = []
    active_appointments: List[str] = []

    class Config:
        from_attributes = True 