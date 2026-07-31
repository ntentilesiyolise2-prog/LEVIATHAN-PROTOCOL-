# leviathan/api/websocket.py
import asyncio
import json
from typing import List, Dict, Any
from fastapi import WebSocket, WebSocketDisconnect
from loguru import logger

from ..core import Engine, NotificationCenter

class WebSocketManager:
    def __init__(self, engine: Engine = None):
        self.engine = engine
        self.active_connections: List[WebSocket] = []
        self._ping_task = None

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket connected: {len(self.active_connections)} total")
        # Send unread notifications immediately
        if self.engine:
            unread = self.engine.notification_center.get_unread()
            if unread:
                await websocket.send_json({"type": "notifications", "data": unread})
        # Start ping task if not running
        if self._ping_task is None or self._ping_task.done():
            self._ping_task = asyncio.create_task(self._ping_loop())

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        logger.info(f"WebSocket disconnected: {len(self.active_connections)} remaining")

    async def broadcast(self, message: Dict[str, Any]):
        """Broadcast a message to all connected clients."""
        for conn in self.active_connections:
            try:
                await conn.send_json(message)
            except Exception as e:
                logger.error(f"Broadcast error: {e}")

    async def broadcast_signal(self, signal: Dict[str, Any]):
        await self.broadcast({"type": "signal", "data": signal})

    async def broadcast_notification(self, notif: Dict[str, Any]):
        await self.broadcast({"type": "notification", "data": notif})

    async def _ping_loop(self):
        """Send periodic ping to keep connections alive."""
        while self.active_connections:
            await asyncio.sleep(30)
            for conn in self.active_connections:
                try:
                    await conn.send_json({"type": "ping"})
                except:
                    pass

# Global manager (will be set in main)
manager = WebSocketManager()

async def websocket_endpoint(websocket: WebSocket):
    global manager
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            try:
                payload = json.loads(data)
                if payload.get("action") == "mark_read":
                    notif_id = payload.get("id")
                    if manager.engine:
                        manager.engine.notification_center.mark_read(notif_id)
                        # Acknowledge
                        await websocket.send_json({"type": "ack", "status": "marked_read"})
                elif payload.get("action") == "execute":
                    # Placeholder for execution
                    await websocket.send_json({"type": "execution", "status": "not_implemented"})
                elif payload.get("action") == "ping":
                    await websocket.send_json({"type": "pong"})
            except json.JSONDecodeError:
                logger.warning(f"Invalid JSON: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
