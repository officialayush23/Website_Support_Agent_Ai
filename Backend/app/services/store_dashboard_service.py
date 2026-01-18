# app/services/store_dashboard_service.py

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from uuid import UUID
from datetime import date

from app.models.models import Pickup, Order


async def get_store_dashboard(
    db: AsyncSession,
    store_id: UUID,
):
    today = date.today()

    res = await db.execute(
        select(
            func.count(Pickup.id).label("total_pickups"),
            func.count().filter(Pickup.status == "picked_up").label("completed"),
            func.count().filter(Pickup.status == "ready").label("pending"),
            func.count().filter(Pickup.status == "cancelled").label("cancelled"),
            func.coalesce(
                func.sum(Pickup.amount).filter(Pickup.status == "picked_up"),
                0
            ).label("revenue"),
        )
        .join(Order, Order.id == Pickup.order_id)
        .where(
            Pickup.store_id == store_id,
            func.date(Order.created_at) == today,
        )
    )

    r = res.one()

    return {
        "date": today.isoformat(),
        "total_pickups": r.total_pickups,
        "completed": r.completed,
        "pending": r.pending,
        "cancelled": r.cancelled,
        "revenue": float(r.revenue),
    }
