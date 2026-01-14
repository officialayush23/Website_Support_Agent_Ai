# app/api/routers/events.py
# app/api/routers/events.py
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.core.database import get_db
from app.core.auth import get_current_user
from app.services.user_event_service import record_event
from app.schema.enums import UserEventType
from pydantic import BaseModel
from typing import Optional, Dict, Any
from app.services.user_event_service import get_user_context
router = APIRouter(prefix="/events", tags=["Events"])


class UserEventCreate(BaseModel):
    event_type: UserEventType
    product_id: Optional[UUID] = None
    order_id: Optional[UUID] = None
    metadata: Optional[Dict[str, Any]] = None


@router.post("/")
async def track_event(
    payload: UserEventCreate,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    await record_event(
        db=db,
        user_id=user["user_id"],
        event_type=payload.event_type.value,
        product_id=payload.product_id,
        order_id=payload.order_id,
        metadata=payload.metadata,
    )
    return {"status": "tracked"}


# app/api/routers/events.py
@router.get("/context")
async def get_context(
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    return await get_user_context(db, user["user_id"])
