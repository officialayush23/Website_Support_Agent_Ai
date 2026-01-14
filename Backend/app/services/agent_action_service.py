# app/services/agent_action_service.py
from uuid import uuid4, UUID
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.models import AgentAction
from app.models.enums import agent_action_status_enum


async def log_agent_action(
    db: AsyncSession,
    conversation_id: UUID | None,
    action_type: str,
    payload: dict,
    confidence: float | None = None,
    status: str = "executed",
):
    action = AgentAction(
        id=uuid4(),
        conversation_id=conversation_id,
        action_type=action_type,
        payload=payload,
        status=status,  # ✅ string enum value
        confidence=confidence,
    )
    db.add(action)
    await db.commit()
    return action
