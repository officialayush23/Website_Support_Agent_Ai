# app/api/routers/support.py

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.core.database import get_db
from app.core.auth import get_current_user
from app.llm.agent import run_agent
from app.models.models import Conversation
from app.models.enums import message_role_enum
from app.schema.schemas import MessageCreate, ConversationOut, AgentActionOut # Ensure AgentActionOut exists
from app.schema.enums import ConversationStatus

from app.services.support_service import (
    get_or_create_active_conversation,
    get_conversation_history,
    add_message,
    get_ai_handoffs,
    end_session_for_user,
    get_pending_actions,
)
from app.utils.api_error import forbidden, not_found

router = APIRouter(prefix="/support", tags=["Support"])


# ==========================================================
# 1. START CHAT (Gets Session + Ticket)
# ==========================================================
@router.post("/conversations")
async def start_conversation(
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    convo = await get_or_create_active_conversation(db, user["user_id"])
    return {"conversation_id": convo.id, "chat_session_id": convo.chat_session_id}


# ==========================================================
# 2. CHAT HISTORY
# ==========================================================
@router.get("/conversations/{conversation_id}/messages")
async def get_messages(
    conversation_id: UUID,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    return await get_conversation_history(db, conversation_id)


# ==========================================================
# 3. PENDING ACTIONS (UI Recovery)
# ==========================================================
@router.get("/conversations/{conversation_id}/actions", response_model=list[AgentActionOut])
async def get_actions(
    conversation_id: UUID,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    """
    Call this when page reloads to see if there are any unclicked buttons
    (e.g., Confirm Payment, Select Store)
    """
    return await get_pending_actions(db, conversation_id)

# ==========================================================
# 4. SEND MESSAGE
# ==========================================================
@router.post("/conversations/{conversation_id}/messages")
async def send_message(
    conversation_id: UUID,
    payload: MessageCreate,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    user_id = user["user_id"]

    # A. Save USER message
    await add_message(
        db=db,
        conversation_id=conversation_id,
        user_id=user_id,
        role=message_role_enum.user,
        content=payload.content,
    )

    # B. Run AI Agent
    ai_response = await run_agent(
        user_id=user_id,
        user_message=payload.content,
        conversation_id=conversation_id, # Agent uses this to find the Session
    )

    # C. Save AI Response
    await add_message(
        db=db,
        conversation_id=conversation_id,
        user_id=user_id,
        role=message_role_enum.assistant,
        content=ai_response["content"],
    )

    return {
        "role": "assistant",
        "content": ai_response["content"],
        "actions": ai_response.get("actions", []), # Immediate actions for UI
        "handoff": ai_response.get("handoff", False),
    }

@router.post("/conversations/{conversation_id}/join")
async def join_conversation(
    conversation_id: UUID,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    # Only Admin or Support can join
    if user["role"] not in ("admin", "support"):
        forbidden()

    convo = await db.get(Conversation, conversation_id)
    if not convo:
        not_found("Conversation")
    
    # Assign ticket to the current user
    convo.assigned_to = user["user_id"]
    await db.commit()
    
    return {"status": "joined", "assigned_to": user["user_id"]}

# ==========================================================
# 5. END SESSION (TRIGGER SUMMARY)
# ==========================================================
@router.post("/sessions/end")
async def end_current_session(
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    """
    User clicks "New Chat". 
    We close the old session, summarize it, and update User Preferences.
    """
    return await end_session_for_user(db, user["user_id"])


# ==========================================================
# ADMIN: HANDOFFS
# ==========================================================
@router.get("/admin/conversations/ai-handoffs", response_model=list[ConversationOut])
async def list_ai_handoffs(
    status: ConversationStatus | None = None,
    assigned_to: UUID | None = None,
    unassigned: bool = False,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    if user["role"] not in ("admin", "support"):
        forbidden()
    return await get_ai_handoffs(db, status=status.value if status else None, assigned_to=assigned_to, unassigned=unassigned)