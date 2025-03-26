from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, List
import json
from datetime import datetime

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {
            "doctors": [],
            "patients": []
        }

    async def connect(self, websocket: WebSocket, user_type: str):
        await websocket.accept()
        self.active_connections[user_type].append(websocket)

    def disconnect(self, websocket: WebSocket, user_type: str):
        self.active_connections[user_type].remove(websocket)

    async def broadcast_to_doctors(self, message: dict):
        for connection in self.active_connections["doctors"]:
            await connection.send_json(message)

    async def broadcast_to_patients(self, message: dict):
        for connection in self.active_connections["patients"]:
            await connection.send_json(message)

    async def send_personal_message(self, message: dict, user_id: str, user_type: str):
        for connection in self.active_connections[user_type]:
            if connection.user_id == user_id:
                await connection.send_json(message)

manager = ConnectionManager()

async def handle_websocket(websocket: WebSocket, user_type: str, user_id: str):
    await manager.connect(websocket, user_type)
    websocket.user_id = user_id
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            # Handle different types of messages
            if message["type"] == "test_update":
                await manager.broadcast_to_doctors({
                    "type": "test_update",
                    "test_id": message["test_id"],
                    "status": message["status"],
                    "timestamp": datetime.utcnow().isoformat()
                })
            elif message["type"] == "patient_update":
                await manager.send_personal_message({
                    "type": "patient_update",
                    "patient_id": message["patient_id"],
                    "update": message["update"],
                    "timestamp": datetime.utcnow().isoformat()
                }, message["patient_id"], "patients")
    except WebSocketDisconnect:
        manager.disconnect(websocket, user_type) 