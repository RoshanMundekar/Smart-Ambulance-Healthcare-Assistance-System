"""
WebSocket notification manager and notification utilities.
"""
import json
from typing import Dict, List, Optional
from fastapi import WebSocket
from loguru import logger
from sqlalchemy.orm import Session

from app.models.booking import Notification


class ConnectionManager:
    """Manages active WebSocket connections per user."""

    def __init__(self):
        self.active_connections: Dict[int, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, user_id: int):
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = []
        self.active_connections[user_id].append(websocket)
        logger.info(f"WebSocket connected: user_id={user_id}")

    def disconnect(self, websocket: WebSocket, user_id: int):
        if user_id in self.active_connections:
            try:
                self.active_connections[user_id].remove(websocket)
            except ValueError:
                pass
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
        logger.info(f"WebSocket disconnected: user_id={user_id}")

    async def send_to_user(self, user_id: int, message: dict):
        connections = self.active_connections.get(user_id, [])
        dead = []
        for ws in connections:
            try:
                await ws.send_text(json.dumps(message))
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.disconnect(ws, user_id)

    async def broadcast(self, message: dict, user_ids: Optional[List[int]] = None):
        targets = user_ids if user_ids else list(self.active_connections.keys())
        for uid in targets:
            await self.send_to_user(uid, message)

    def is_connected(self, user_id: int) -> bool:
        return user_id in self.active_connections and bool(self.active_connections[user_id])


# Global WebSocket manager
ws_manager = ConnectionManager()


async def notify_user(
    db: Session,
    user_id: int,
    title: str,
    message: str,
    notification_type: str = "system",
    related_id: Optional[int] = None,
    related_type: Optional[str] = None,
):
    """Save a notification to DB and push via WebSocket if connected."""
    notif = Notification(
        user_id=user_id,
        title=title,
        message=message,
        notification_type=notification_type,
        related_id=related_id,
        related_type=related_type,
    )
    db.add(notif)
    db.commit()
    db.refresh(notif)

    payload = {
        "type": "notification",
        "data": {
            "id": notif.id,
            "title": title,
            "message": message,
            "notification_type": notification_type,
            "related_id": related_id,
            "created_at": notif.created_at.isoformat() if notif.created_at else None,
        },
    }
    await ws_manager.send_to_user(user_id, payload)
    return notif


async def push_emergency_update(
    user_id: int,
    driver_id: Optional[int],
    hospital_admin_id: Optional[int],
    emergency_data: dict,
):
    """Push emergency status to all relevant parties."""
    payload = {"type": "emergency_update", "data": emergency_data}
    await ws_manager.send_to_user(user_id, payload)
    if driver_id:
        await ws_manager.send_to_user(driver_id, payload)
    if hospital_admin_id:
        await ws_manager.send_to_user(hospital_admin_id, payload)


async def push_location_update(ambulance_id: int, lat: float, lng: float, eta: Optional[int] = None):
    """Broadcast ambulance location to all connected users."""
    payload = {
        "type": "location_update",
        "data": {
            "ambulance_id": ambulance_id,
            "latitude": lat,
            "longitude": lng,
            "eta_minutes": eta,
        },
    }
    await ws_manager.broadcast(payload)
