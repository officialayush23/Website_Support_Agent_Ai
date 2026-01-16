# app/core/ws_manager.py

from typing import Dict, List
from fastapi import WebSocket

class WSManager:
    def __init__(self):
        self.connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, channel: str, ws: WebSocket):
        await ws.accept()
        self.connections.setdefault(channel, []).append(ws)

    def disconnect(self, channel: str, ws: WebSocket):
        self.connections[channel].remove(ws)

    async def broadcast(self, channel: str, payload: dict):
        for ws in self.connections.get(channel, []):
            await ws.send_json(payload)


ws_manager = WSManager()
