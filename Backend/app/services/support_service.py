# app/services/support_service.py

from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID, uuid4
from sqlalchemy import select
from datetime import datetime
from sqlalchemy import desc
from app.models.enums import message_role_enum
from app.models.models import Conversation, Message
from app.models.enums import (
    conversation_status_enum,
    message_role_enum,
)
from app.utils.api_error import not_found, forbidden


# =========================
# START CONVERSATION
# =========================
async def start_conversation(
    db: AsyncSession,
    user_id: UUID,
):
    convo = Conversation(
        id=uuid4(),
        user_id=user_id,
        status="active",


        handled_by="llm",
    )
    db.add(convo)
    await db.commit()
    await db.refresh(convo)
    return convo


# =========================
# ADD MESSAGE
# =========================


async def add_message(
    db: AsyncSession,
    conversation_id: UUID,
    user_id: UUID,
    role: message_role_enum,
    content: str,
):
    convo = await db.get(Conversation, conversation_id)
    if not convo:
        not_found("Conversation")

    # User can only write to own conversation
    if role == message_role_enum.user and convo.user_id != user_id:
        forbidden()

    msg = Message(
        id=uuid4(),
        conversation_id=conversation_id,
        role=role,
        content=content,
    )
    db.add(msg)

    convo.last_message_at = datetime.utcnow()

    await db.commit()
    await db.refresh(msg)
    return msg


# =========================
# AI → HUMAN HANDOFF
# =========================
async def mark_handoff_to_human(
    db: AsyncSession,
    conversation_id: UUID,
    *,
    reason: str,
    ai_confidence: float,
):
    convo = await db.get(Conversation, conversation_id)
    if not convo:
        not_found("Conversation")

    # Prevent duplicate handoff
    if convo.handled_by == "human":
        return convo

    convo.handled_by = "human"
    convo.handed_off_at = datetime.utcnow()
    convo.handoff_reason = reason
    convo.ai_confidence = ai_confidence

    await db.commit()
    await db.refresh(convo)
    return convo


# =========================
# ADMIN: LIST AI HANDOFFS
# =========================
async def get_ai_handoffs(
    db: AsyncSession,
    *,
    status: str | None = None,
    assigned_to: UUID | None = None,
    unassigned: bool = False,
):
    stmt = (
        select(Conversation)
        .where(Conversation.handled_by == "human")
        .order_by(Conversation.handed_off_at.desc())
    )

    if status:
        stmt = stmt.where(
            Conversation.status == conversation_status_enum(status)
        )

    if assigned_to:
        stmt = stmt.where(Conversation.assigned_to == assigned_to)

    if unassigned:
        stmt = stmt.where(Conversation.assigned_to.is_(None))

    res = await db.execute(stmt)
    return res.scalars().all()

# =========================
async def get_or_create_active_conversation(
    db: AsyncSession,
    user_id: UUID,
) -> Conversation:
    res = await db.execute(
        select(Conversation)
        .where(
            Conversation.user_id == user_id,
            Conversation.status == conversation_status_enum.active,
        )
        .order_by(desc(Conversation.last_message_at))
        .limit(1)
    )

    convo = res.scalar_one_or_none()
    if convo:
        return convo

    convo = Conversation(
        id=uuid4(),
        user_id=user_id,
        status="active",
        handled_by="llm",
    )
    db.add(convo)
    await db.commit()
    await db.refresh(convo)
    return convo


# =========================
# LOAD CONVERSATION HISTORY
# =========================
async def get_conversation_history(
    db: AsyncSession,
    conversation_id: UUID,
    limit: int = 50,
):
    res = await db.execute(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.asc())
        .limit(limit)
    )

    return [
        {
            "role": m.role,
            "content": m.content,
            "created_at": m.created_at,
        }
        for m in res.scalars()
    ]
