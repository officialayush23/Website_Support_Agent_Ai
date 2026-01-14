# app/api/ws/events.py
# app/api/ws/events.py
from fastapi import WebSocket
from app.core.auth import get_user_from_ws
from app.core.database import AsyncSessionLocal
from app.services.user_event_service import record_event

async def events_ws(ws: WebSocket):
    await ws.accept()
    user = await get_user_from_ws(ws)

    async with AsyncSessionLocal() as db:
        while True:
            payload = await ws.receive_json()
            await record_event(
                db=db,
                user_id=user["user_id"],
                **payload
            )
