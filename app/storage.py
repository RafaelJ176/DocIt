import os
from fastapi import UploadFile
from datetime import datetime
import aiofiles
from typing import Optional
import uuid

UPLOAD_DIR = "uploads"
ALLOWED_EXTENSIONS = {
    "pdf", "jpg", "jpeg", "png", "dicom", "doc", "docx"
}

def get_file_extension(filename: str) -> str:
    return filename.rsplit(".", 1)[1].lower()

def is_allowed_file(filename: str) -> bool:
    return get_file_extension(filename) in ALLOWED_EXTENSIONS

async def save_upload_file(file: UploadFile, test_id: str) -> Optional[str]:
    if not is_allowed_file(file.filename):
        return None
    
    # Create upload directory if it doesn't exist
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    
    # Generate unique filename
    file_extension = get_file_extension(file.filename)
    unique_filename = f"{uuid.uuid4()}.{file_extension}"
    file_path = os.path.join(UPLOAD_DIR, test_id, unique_filename)
    
    # Create test directory if it doesn't exist
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    # Save file
    async with aiofiles.open(file_path, 'wb') as out_file:
        content = await file.read()
        await out_file.write(content)
    
    return file_path

async def delete_file(file_path: str) -> bool:
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
        return False
    except Exception:
        return False 