# app/api/routers/support.py
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.core.database import get_db
from app.core.auth import get_current_user
from app.schema.schemas import MessageCreate
from app.services.support_service import start_conversation, add_message
from app.models.py_enums import MessageRole

router = APIRouter(prefix="/support", tags=["Support"])


@router.post("/conversations")
async def start(
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    convo = await start_conversation(db, user["user_id"])
    return {"conversation_id": convo.id}


@router.post("/conversations/{conversation_id}/messages")
async def message(
    conversation_id: UUID,
    payload: MessageCreate,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    await add_message(
        db=db,
        conversation_id=conversation_id,
        user_id=user["user_id"],
        role=MessageRole.user,
        content=payload.content,
    )
    return {"status": "sent"}
