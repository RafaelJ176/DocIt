from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from enum import Enum

class AppointmentStatus(str, Enum):
    SCHEDULED = "scheduled"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"
    NO_SHOW = "no_show"

class AppointmentType(str, Enum):
    CONSULTATION = "consultation"
    FOLLOW_UP = "follow_up"
    EMERGENCY = "emergency"
    ROUTINE_CHECKUP = "routine_checkup"
    SPECIALIST_VISIT = "specialist_visit"

class AppointmentBase(BaseModel):
    patient_id: str
    doctor_id: str
    appointment_type: AppointmentType
    scheduled_time: datetime
    duration_minutes: int = 30
    notes: Optional[str] = None
    status: AppointmentStatus = AppointmentStatus.SCHEDULED

class AppointmentCreate(AppointmentBase):
    pass

class Appointment(AppointmentBase):
    id: str
    created_at: datetime
    updated_at: datetime
    diagnosis: Optional[str] = None
    prescription: Optional[dict] = None
    follow_up_date: Optional[datetime] = None

    class Config:
        from_attributes = True 