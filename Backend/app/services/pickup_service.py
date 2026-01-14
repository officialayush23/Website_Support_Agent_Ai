# app/services/pickup_service.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from uuid import UUID
from datetime import datetime

from app.models.models import Pickup, Order, OrderItem, Product, User
from app.utils.api_error import not_found, bad_request


# =========================================
# LIST PICKUPS FOR A STORE
# =========================================
async def list_store_pickups(
    db: AsyncSession,
    store_id: UUID,
):
    """
    Returns all pickups for a store with:
    - order
    - user
    - order items
    - product details
    """

    res = await db.execute(
        select(Pickup)
        .where(Pickup.store_id == store_id)
        .options(
            # Pickup → Order
            selectinload(Pickup.order)
            # Order → Items → Product
            .selectinload(Order.items)
            .selectinload(OrderItem.product),

            # Order → User
            selectinload(Pickup.order)
            .selectinload(Order.user),
        )
        .order_by(Pickup.id.desc())
    )

    pickups = []
    for p in res.scalars().all():
        order = p.order
        user = order.user if order else None

        pickups.append(
            {
                "pickup_id": p.id,
                "order_id": p.order_id,
                "store_id": p.store_id,
                "status": p.status,
                "amount": float(p.amount),
                "created_at": order.created_at if order else None,
                "picked_up_at": p.picked_up_at,
                "user": {
                    "user_id": user.id,
                    "name": user.name,
                } if user else None,
                "items": [
                    {
                        "product_id": item.product.id,
                        "name": item.product.name,
                        "quantity": item.quantity,
                    }
                    for item in order.items
                ] if order else [],
            }
        )

    return pickups


# =========================================
# UPDATE PICKUP STATUS
# =========================================
async def update_pickup_status(
    db: AsyncSession,
    pickup_id: UUID,
    status: str,
):
    """
    Update pickup status.
    Allowed: ready | picked_up | cancelled
    """

    pickup = await db.get(Pickup, pickup_id)
    if not pickup:
        not_found("Pickup")

    if status not in {"ready", "picked_up", "cancelled"}:
        bad_request("Invalid pickup status")

    pickup.status = status

    if status == "picked_up":
        pickup.picked_up_at = datetime.utcnow()

    await db.commit()
    await db.refresh(pickup)
    return pickup
