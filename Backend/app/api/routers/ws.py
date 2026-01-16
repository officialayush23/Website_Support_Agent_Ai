# app/api/routers/ws.py

from fastapi import APIRouter, WebSocket
from uuid import UUID
from app.core.ws_manager import ws_manager

router = APIRouter()

@router.websocket("/ws/stores/{store_id}/pickups")
async def pickup_ws(ws: WebSocket, store_id: UUID):
    channel = f"store:{store_id}:pickups"
    await ws_manager.connect(channel, ws)

    try:
        while True:
            await ws.receive_text()  # keep alive
    except:
        ws_manager.disconnect(channel, ws)
