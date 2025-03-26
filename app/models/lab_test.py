from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from enum import Enum

class TestStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class TestType(str, Enum):
    BLOOD_TEST = "blood_test"
    URINE_TEST = "urine_test"
    X_RAY = "x_ray"
    MRI = "mri"
    CT_SCAN = "ct_scan"
    OTHER = "other"

class LabTestBase(BaseModel):
    test_type: TestType
    description: str
    patient_id: str
    doctor_id: str
    status: TestStatus = TestStatus.PENDING

class LabTestCreate(LabTestBase):
    pass

class LabTestResult(BaseModel):
    test_id: str
    result_data: dict
    interpretation: Optional[str] = None
    reference_ranges: Optional[dict] = None
    notes: Optional[str] = None

class LabTest(LabTestBase):
    id: str
    created_at: datetime
    updated_at: datetime
    results: Optional[LabTestResult] = None
    attachments: List[str] = []

    class Config:
        from_attributes = True 