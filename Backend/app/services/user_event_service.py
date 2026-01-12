# app/services/user_event_service.py
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import uuid4
from app.models.models import UserEvent


async def record_event(
    db: AsyncSession,
    *,
    user_id,
    event_type,
    product_id=None,
    order_id=None,
    metadata=None,
):
    event = UserEvent(
        id=uuid4(),
        user_id=user_id,
        event_type=event_type,
        product_id=product_id,
        order_id=order_id,
        metadata=metadata or {},
    )
    db.add(event)
    await db.commit()
