# app/services/support_service.py
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID, uuid4

from app.models.models import Conversation, Message
from app.models.py_enums import MessageRole, ConversationStatus
from app.utils.api_error import not_found, forbidden


async def start_conversation(
    db: AsyncSession,
    user_id: UUID,
):
    convo = Conversation(
        id=uuid4(),
        user_id=user_id,
        status=ConversationStatus.active.value,
    )
    db.add(convo)
    await db.commit()
    await db.refresh(convo)
    return convo


async def add_message(
    db: AsyncSession,
    conversation_id: UUID,
    user_id: UUID,
    role: MessageRole,
    content: str,
):
    convo = await db.get(Conversation, conversation_id)
    if not convo:
        not_found("Conversation")

    if convo.user_id != user_id:
        forbidden()

    msg = Message(
        id=uuid4(),
        conversation_id=conversation_id,
        role=role.value,
        content=content,
    )
    db.add(msg)

    convo.last_message_at = msg.created_at

    await db.commit()
    await db.refresh(msg)
    return msg

