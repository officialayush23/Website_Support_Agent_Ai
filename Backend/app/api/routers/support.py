
# app/api/routers/support.py
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.core.database import get_db
from app.core.auth import get_current_user
from app.llm.agent import run_agent

from app.models.enums import message_role_enum
from app.schema.schemas import MessageCreate, ConversationOut
from app.schema.enums import ConversationStatus

from app.services.support_service import (
    get_or_create_active_conversation,
    get_conversation_history,
    add_message,
    get_ai_handoffs,
)

from app.utils.api_error import forbidden

router = APIRouter(prefix="/support", tags=["Support"])


# ==========================================================
# USER: START / RESUME CONVERSATION
# ==========================================================
@router.post("/conversations")
async def start_conversation(
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    convo = await get_or_create_active_conversation(db, user["user_id"])
    return {"conversation_id": convo.id}


# ==========================================================
# USER: GET CONVERSATION HISTORY
# ==========================================================
@router.get("/conversations/{conversation_id}/messages")
async def get_messages(
    conversation_id: UUID,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    return await get_conversation_history(db, conversation_id)


# ==========================================================
# USER: SEND MESSAGE (SYNC AI RESPONSE)
# ==========================================================
@router.post("/conversations/{conversation_id}/messages")
async def send_message(
    conversation_id: UUID,
    
    payload: MessageCreate,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    user_id = user["user_id"]

    # 1️⃣ Save USER message
    await add_message(
        db=db,
        conversation_id=conversation_id,
        user_id=user_id,
        role=message_role_enum.user,
        content=payload.content,
    )

    # 2️⃣ Run AI agent (WAIT here)
    ai_response = await run_agent(
        user_id=user_id,
        user_message=payload.content,
        conversation_id=conversation_id,
    )

    ai_text = ai_response["content"]

    # 3️⃣ Save ASSISTANT message
    await add_message(
        db=db,
        conversation_id=conversation_id,
        user_id=user_id,
        role=message_role_enum.assistant,
        content=ai_text,
    )

    # 4️⃣ Return AI response (REST-style)
    return {
        "role": "assistant",
        "content": ai_text,
        "products": ai_response.get("products", []),
        "confidence": ai_response.get("confidence"),
        "handoff": ai_response.get("handoff", False),
    }


# ==========================================================
# ADMIN: AI HANDOFF QUEUE
# ==========================================================
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
        status=status.value if status else None,
        assigned_to=assigned_to,
        unassigned=unassigned,
    )
