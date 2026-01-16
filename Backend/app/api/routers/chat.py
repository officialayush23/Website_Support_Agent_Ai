# app/routers/chat.py
from app.services.chat_service import create_chat_session
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from app.core.database import get_db
from app.core.auth import get_current_user
from app.llm.agent import run_agent
from app.models.models import ChatSession, Message
from app.schema.schemas import MessageCreate
from app.utils.api_error import not_found

router = APIRouter(prefix="/chat", tags=["AI Chat"])



@router.post("/chat-sessions")
async def new_session(
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    s = await create_chat_session(db, user["user_id"])
    return {"chat_session_id": s.id}
@router.post("/sessions")
async def create_chat_session(
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    session = ChatSession(
        user_id=user["user_id"],
        is_active=True,
    )
    db.add(session)
    await db.commit()
    await db.refresh(session)

    return {
        "chat_session_id": session.id,
        "created_at": session.created_at,
    }


@router.post("/sessions/{chat_session_id}/messages")
async def send_message_to_agent(
    chat_session_id: UUID,
    payload: MessageCreate,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    session = await db.get(ChatSession, chat_session_id)
    if not session or session.user_id != user["user_id"]:
        not_found("Chat session")

    # 🔹 Run agent
    agent_response = await run_agent(
        user_id=user["user_id"],
        user_message=payload.content,
        chat_session_id=chat_session_id,
    )

    return {
        "chat_session_id": chat_session_id,
        "message": agent_response["content"],
        "actions": agent_response.get("actions", []),
        "confidence": agent_response.get("confidence"),
        "handoff": agent_response.get("handoff", False),
        "tool_used": agent_response.get("tool_used"),
    }

from app.llm.memory import AgentMemory

@router.get("/sessions/{chat_session_id}/messages")
async def get_chat_history(
    chat_session_id: UUID,
    user=Depends(get_current_user),
):
    memory = AgentMemory(user["user_id"])
    history = await memory.read()

    return {
        "chat_session_id": chat_session_id,
        "messages": history,
    }
@router.post("/sessions/{chat_session_id}/end")
async def end_chat_session(
    chat_session_id: UUID,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    session = await db.get(ChatSession, chat_session_id)
    if not session or session.user_id != user["user_id"]:
        not_found("Chat session")

    session.is_active = False
    await db.commit()

    return {"status": "ended"}
