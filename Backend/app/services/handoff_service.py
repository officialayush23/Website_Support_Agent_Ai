# app/services/handoff_service.py
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.models import Conversation

async def escalate_to_human(
    db: AsyncSession,
    conversation_id,
    reason: str,
):
    convo = await db.get(Conversation, conversation_id)
    if not convo:
        return

    convo.handled_by = "human"
    

    await db.commit()
