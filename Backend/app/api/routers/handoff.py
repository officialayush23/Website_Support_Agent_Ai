# app/api/routers/handoff.py
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.core.database import get_db
from app.core.auth import get_current_user
from app.services.handoff_service import escalate_to_human
from app.utils.api_error import forbidden

router = APIRouter(prefix="/handoff", tags=["Handoff"])


@router.post("/{conversation_id}")
async def handoff(
    conversation_id: UUID,
    reason: str,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    # LLM / system / support only
    if user["role"] not in ("admin", "support", "system"):
        forbidden()

    await escalate_to_human(
        db=db,
        conversation_id=conversation_id,
        reason=reason,
    )

    return {"status": "handed_off"}
