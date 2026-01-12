# app/api/ws/chat.py
from fastapi import WebSocket
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from fastapi import APIRouter

from app.llm.agent import run_agent
from app.core.auth import get_user_from_ws
from app.core.database import AsyncSessionLocal
from app.services.support_service import start_conversation

router = APIRouter()
@router.websocket("/ws/chat")
async def chat_ws(ws: WebSocket):
    await ws.accept()

    user = await get_user_from_ws(ws)
    user_id = user["user_id"]

    async with AsyncSessionLocal() as db:
        convo = await start_conversation(db, user_id)
        conversation_id = convo.id

    while True:
        msg = await ws.receive_text()
        response = await run_agent(
            user_id=user_id,
            user_message=msg,
            conversation_id=conversation_id,
        )
        await ws.send_json(response)
