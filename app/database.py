from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
from typing import Optional
import os
from dotenv import load_dotenv

load_dotenv()

MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "healthcare_db")

client = AsyncIOMotorClient(MONGODB_URL)
database = client[DATABASE_NAME]

# Collections
users_collection = database.users
patients_collection = database.patients
lab_tests_collection = database.lab_tests

async def get_database():
    return database

async def get_collection(collection_name: str):
    return database[collection_name]

# Helper functions for common database operations
async def create_document(collection_name: str, document: dict) -> str:
    collection = await get_collection(collection_name)
    document["created_at"] = datetime.utcnow()
    document["updated_at"] = datetime.utcnow()
    result = await collection.insert_one(document)
    return str(result.inserted_id)

async def update_document(collection_name: str, document_id: str, update_data: dict) -> bool:
    collection = await get_collection(collection_name)
    update_data["updated_at"] = datetime.utcnow()
    result = await collection.update_one(
        {"_id": document_id},
        {"$set": update_data}
    )
    return result.modified_count > 0

async def get_document(collection_name: str, document_id: str) -> Optional[dict]:
    collection = await get_collection(collection_name)
    return await collection.find_one({"_id": document_id})

async def delete_document(collection_name: str, document_id: str) -> bool:
    collection = await get_collection(collection_name)
    result = await collection.delete_one({"_id": document_id})
    return result.deleted_count > 0 