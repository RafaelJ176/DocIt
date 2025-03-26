from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File, WebSocket
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import timedelta, datetime
from . import crud, models, schemas
from .database import engine, get_db, create_document, get_document, update_document, delete_document
from .auth.utils import (
    verify_password, get_password_hash, create_access_token,
    get_current_user, check_permissions, ACCESS_TOKEN_EXPIRE_MINUTES
)
from .models.user import UserRole, UserCreate, User
from .models.lab_test import LabTestCreate, LabTest, TestStatus
from .models.patient import PatientCreate, Patient
from .models.doctor import DoctorCreate, Doctor
from .models.appointment import AppointmentCreate, Appointment, AppointmentStatus
from .websocket import handle_websocket
from .storage import save_upload_file, delete_file
import json

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Healthcare API",
    description="A modern healthcare API for managing lab tests, patients, and healthcare providers",
    version="1.0.0"
)

@app.get("/")
async def root():
    return {"message": "Welcome to FastAPI Backend"}

@app.get("/items", response_model=List[schemas.Item])
def read_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    items = crud.get_items(db, skip=skip, limit=limit)
    return items

@app.get("/items/{item_id}", response_model=schemas.Item)
def read_item(item_id: int, db: Session = Depends(get_db)):
    db_item = crud.get_item(db, item_id=item_id)
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return db_item

@app.post("/items", response_model=schemas.Item)
def create_item(item: schemas.ItemCreate, db: Session = Depends(get_db)):
    return crud.create_item(db=db, item=item)

@app.put("/items/{item_id}", response_model=schemas.Item)
def update_item(item_id: int, item: schemas.ItemCreate, db: Session = Depends(get_db)):
    db_item = crud.update_item(db=db, item_id=item_id, item=item)
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return db_item

@app.delete("/items/{item_id}")
def delete_item(item_id: int, db: Session = Depends(get_db)):
    success = crud.delete_item(db=db, item_id=item_id)
    if not success:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"message": "Item deleted successfully"}

# Authentication endpoints
@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await get_document("users", form_data.username)
    if not user or not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user["_id"]), "role": user["role"]},
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# User management endpoints
@app.post("/users", response_model=User)
async def create_user(user: UserCreate, current_user: dict = Depends(get_current_user)):
    if not check_permissions(current_user["role"], UserRole.ADMIN):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    db_user = await get_document("users", user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    user_dict = user.dict()
    user_dict["hashed_password"] = get_password_hash(user_dict.pop("password"))
    user_id = await create_document("users", user_dict)
    return await get_document("users", user_id)

# Patient management endpoints
@app.post("/patients", response_model=Patient)
async def create_patient(
    patient: PatientCreate,
    current_user: dict = Depends(get_current_user)
):
    if not check_permissions(current_user["role"], UserRole.DOCTOR):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    patient_dict = patient.dict()
    patient_id = await create_document("patients", patient_dict)
    return await get_document("patients", patient_id)

@app.get("/patients/{patient_id}", response_model=Patient)
async def get_patient(
    patient_id: str,
    current_user: dict = Depends(get_current_user)
):
    patient = await get_document("patients", patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    if current_user["role"] == UserRole.PATIENT and str(current_user["_id"]) != patient["user_id"]:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    return patient

# Lab test management endpoints
@app.post("/lab-tests", response_model=LabTest)
async def create_lab_test(
    test: LabTestCreate,
    current_user: dict = Depends(get_current_user)
):
    if not check_permissions(current_user["role"], UserRole.DOCTOR):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    test_dict = test.dict()
    test_id = await create_document("lab_tests", test_dict)
    return await get_document("lab_tests", test_id)

@app.get("/lab-tests/{test_id}", response_model=LabTest)
async def get_lab_test(
    test_id: str,
    current_user: dict = Depends(get_current_user)
):
    test = await get_document("lab_tests", test_id)
    if not test:
        raise HTTPException(status_code=404, detail="Test not found")
    
    if current_user["role"] == UserRole.PATIENT and str(current_user["_id"]) != test["patient_id"]:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    return test

@app.put("/lab-tests/{test_id}/results")
async def update_test_results(
    test_id: str,
    results: dict,
    current_user: dict = Depends(get_current_user)
):
    if not check_permissions(current_user["role"], UserRole.DOCTOR):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    test = await get_document("lab_tests", test_id)
    if not test:
        raise HTTPException(status_code=404, detail="Test not found")
    
    update_data = {
        "results": results,
        "status": TestStatus.COMPLETED
    }
    success = await update_document("lab_tests", test_id, update_data)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to update test results")
    
    return await get_document("lab_tests", test_id)

@app.post("/lab-tests/{test_id}/attachments")
async def upload_test_attachment(
    test_id: str,
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    if not check_permissions(current_user["role"], UserRole.DOCTOR):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    # Here you would implement file storage logic
    # For now, we'll just return a success message
    return {"message": "File uploaded successfully"} 