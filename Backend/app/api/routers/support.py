
# app/api/routers/support.py

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.schema.schemas import ConversationOut, MessageCreate
from app.schema.enums import ConversationStatus
from app.models.enums import message_role_enum
from app.services.support_service import (
    get_ai_handoffs,
    start_conversation,
    add_message,
)
from app.utils.api_error import forbidden
from app.core.database import get_db
from app.core.auth import get_current_user

router = APIRouter(prefix="/support", tags=["Support"])


# =========================
# ADMIN: AI HANDOFFS
# =========================
@router.get(
    "/admin/conversations/ai-handoffs",
    response_model=list[ConversationOut],
)
async def list_ai_handoffs(
    status: ConversationStatus | None = None,
    assigned_to: UUID | None = None,
    unassigned: bool = False,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    if user["role"] not in ("admin", "support"):
        forbidden()

    return await get_ai_handoffs(
        db=db,
        status=status.value if status else None,  # ✅ convert API enum → DB value
        assigned_to=assigned_to,
        unassigned=unassigned,
    )


# =========================
# USER: START CONVERSATION
# =========================
@router.post("/conversations")
async def start(
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    convo = await start_conversation(db, user["user_id"])
    return {"conversation_id": convo.id}


# =========================
# USER: SEND MESSAGE
# =========================
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
        role=message_role_enum.user,  # ✅ DB enum only
        content=payload.content,
    )
    return {"status": "sent"}
