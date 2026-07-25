import json
import logging
from typing import List, Dict, Any
from fastapi import WebSocket, WebSocketDisconnect

logger = logging.getLogger("nexusops.websockets")

class ConnectionManager:
    """Manages active WebSocket client connections for real-time control plane event streaming."""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket client connected. Total connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            logger.info(f"WebSocket client disconnected. Total connections: {len(self.active_connections)}")

    async def broadcast(self, event_type: str, data: Dict[str, Any]):
        """Broadcast a JSON payload event to all connected dashboard UI clients."""
        payload = {
            "type": event_type,
            "data": data
        }
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_json(payload)
            except Exception as e:
                logger.warning(f"Error broadcasting to WebSocket client: {e}")
                disconnected.append(connection)
                
        for conn in disconnected:
            self.disconnect(conn)

manager = ConnectionManager()
