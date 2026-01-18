# app/services/support_service.py

from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID, uuid4
from sqlalchemy import select, desc,update
from datetime import datetime

from app.models.enums import (
    message_role_enum,
    conversation_status_enum,
)
from app.models.models import Conversation, Message, ChatSession, User, AgentAction,Embedding
from app.utils.api_error import not_found, forbidden
from app.services.chat_context_service import summarize_chat_session
from app.models.enums import conversation_status_enum
from app.services.chat_context_service import summarize_chat_session
from app.llm.memory import AgentMemory
from app.services.user_embedding_service import rebuild_user_embedding
# =========================
# CONVERSATION MANAGEMENT
# =========================

async def get_or_create_active_conversation(
    db: AsyncSession,
    user_id: UUID,
) -> Conversation:
    # 1. FIND ACTIVE SESSION (AI Memory)
    res_session = await db.execute(
        select(ChatSession)
        .where(ChatSession.user_id == user_id, ChatSession.is_active.is_(True))
        .order_by(desc(ChatSession.created_at))
    )
    session = res_session.scalar_one_or_none()

    # If no session, start one
    if not session:
        session = ChatSession(
            id=uuid4(),
            user_id=user_id,
            is_active=True,
            title="New Chat"
        )
        db.add(session)
        await db.flush() # Flush to generate ID

    # 2. FIND ACTIVE CONVERSATION (Support Ticket) linked to Session
    res_convo = await db.execute(
        select(Conversation)
        .where(
            Conversation.chat_session_id == session.id, 
            Conversation.status == conversation_status_enum.active,
        )
        .order_by(desc(Conversation.last_message_at))
    )
    convo = res_convo.scalar_one_or_none()
    
    if convo:
        return convo

    # 3. Create Ticket if missing
    convo = Conversation(
        id=uuid4(),
        chat_session_id=session.id,
        user_id=user_id,
        status="active",
        handled_by="llm",
    )
    db.add(convo)
    await db.commit()
    await db.refresh(convo)
    return convo


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

    # Security check
    if role == message_role_enum.user and convo.user_id != user_id:
        forbidden()

    # Ensure session linkage
    msg = Message(
        id=uuid4(),
        conversation_id=conversation_id,
        chat_session_id=convo.chat_session_id, # LINK MESSAGES TO SESSION
        role=role,
        content=content,
    )
    db.add(msg)
    convo.last_message_at = datetime.utcnow()
    
    await db.commit()
    await db.refresh(msg)
    return msg

# =========================
# END SESSION & SUMMARIZE
# =========================


async def end_session_for_user(
    db: AsyncSession,
    user_id: UUID,
):
    """
    Ends the active ChatSession:
    - summarizes conversation
    - stores ChatContext + Embedding
    - updates user preferences
    - closes conversations
    - clears Redis memory
    """

    # 1. Get active session
    res = await db.execute(
        select(ChatSession)
        .where(
            ChatSession.user_id == user_id,
            ChatSession.is_active.is_(True),
        )
        .order_by(desc(ChatSession.created_at))
    )
    session = res.scalar_one_or_none()
    if not session:
        not_found("No active session")

    # 2. Fetch messages
    res_msgs = await db.execute(
        select(Message)
        .where(Message.chat_session_id == session.id)
        .order_by(Message.created_at.asc())
    )
    messages = res_msgs.scalars().all()

    # 3. If empty session → close cleanly
    if not messages:
        session.is_active = False
        session.last_activity_at = datetime.utcnow()
        await db.commit()
        return {"status": "ended_empty"}

    # 4. Generate summary (MVP logic)
    summary_text = "\n".join(
        f"{m.role}: {m.content}" for m in messages[-10:]
    )

    # 5. Persist ChatContext + Embedding
    ctx = await summarize_chat_session(
        db=db,
        chat_session_id=session.id,
        summary=summary_text,
        token_count=len(summary_text.split()),
        confidence=1.0,
    )

    await rebuild_user_embedding(db, user_id)

    # 🔥 Link embedding_id explicitly (IMPORTANT)
    embedding = await db.execute(
        select(Embedding)
        .where(
            Embedding.source_type == "chat_summary",
            Embedding.source_id == session.id,
        )
        .order_by(Embedding.created_at.desc())
    )
    embedding = embedding.scalar_one_or_none()

    if embedding:
        ctx.embedding_id = embedding.id

    # 6. Update user preferences
    user = await db.get(User, user_id)
    prefs = dict(user.preferences or {})
    prefs.update(
        {
            "last_session_summary": summary_text,
            "last_session_date": datetime.utcnow().isoformat(),
        }
    )
    user.preferences = prefs

    # 7. Close ALL conversations for this session
    await db.execute(
        update(Conversation)
        .where(Conversation.chat_session_id == session.id)
        .values(
            status=conversation_status_enum.closed,
            last_message_at=datetime.utcnow(),
        )
    )

    # 8. Close session
    session.is_active = False
    session.last_activity_at = datetime.utcnow()

    # 9. Clear Redis memory
    memory = AgentMemory(chat_session_id=str(session.id))
    await memory.clear()

    await db.commit()

    return {
        "status": "ended",
        "summary": summary_text,
        "chat_session_id": session.id,
    }

# =========================
# UTILS (HISTORY, HANDOFF, ACTIONS)
# =========================

async def get_conversation_history(db: AsyncSession, conversation_id: UUID, limit: int = 50):
    res = await db.execute(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.asc())
        .limit(limit)
    )
    return [{"role": m.role, "content": m.content, "created_at": m.created_at} for m in res.scalars()]

async def get_ai_handoffs(db: AsyncSession, status=None, assigned_to=None, unassigned=False):
    stmt = select(Conversation).where(Conversation.handled_by == "human").order_by(Conversation.handed_off_at.desc())
    if status: stmt = stmt.where(Conversation.status == conversation_status_enum(status))
    if assigned_to: stmt = stmt.where(Conversation.assigned_to == assigned_to)
    if unassigned: stmt = stmt.where(Conversation.assigned_to.is_(None))
    res = await db.execute(stmt)
    return res.scalars().all()

async def get_pending_actions(db: AsyncSession, conversation_id: UUID):
    res = await db.execute(
        select(AgentAction)
        .where(
            AgentAction.conversation_id == conversation_id,
            AgentAction.status == "pending"
        )
    )
    return res.scalars().all()