# app/services/user_event_service.py
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import uuid4
from app.models.models import UserEvent
from uuid import UUID
from app.services.user_preference_service import recompute_user_preferences

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

    # 🔥 update preferences
    await recompute_user_preferences(db, user_id)


# app/services/user_event_service.py
from sqlalchemy import select, desc


async def get_user_context(db: AsyncSession, user_id: UUID, limit=50):
    res = await db.execute(
        select(UserEvent)
        .where(UserEvent.user_id == user_id)
        .order_by(desc(UserEvent.created_at))
        .limit(limit)
    )
    events = res.scalars().all()

    return {
        "recent_events": [
            {
                "type": e.event_type,
                "product_id": e.product_id,
                "order_id": e.order_id,
                "metadata": e.meta,
                "created_at": e.created_at,
            }
            for e in events
        ]
    }
