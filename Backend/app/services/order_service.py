# app/services/order_service.py

from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from sqlalchemy.orm import selectinload

from app.models.models import Order, OrderItem, Cart, CartItem
from app.schema.enums import OrderStatus
from app.services.inventory_service import release_inventory_for_order
from app.utils.api_error import bad_request, not_found


# =========================
# LIST USER ORDERS
# =========================

async def list_orders(db: AsyncSession, user_id: UUID):
    res = await db.execute(
        select(Order)
        .where(Order.user_id == user_id)
        .options(selectinload(Order.items))
        .order_by(Order.created_at.desc())
    )
    return res.scalars().all()


# =========================
# GET SINGLE ORDER
# =========================

async def get_order(db: AsyncSession, user_id: UUID, order_id: UUID):
    order = await db.get(
        Order,
        order_id,
        options=[selectinload(Order.items)],
    )
    if not order or order.user_id != user_id:
        not_found("Order")
    return order


# =========================
# CANCEL ORDER (SAFE)
# =========================

CANCELLABLE = {OrderStatus.pending.value}

async def cancel_order(
    db: AsyncSession,
    *,
    user_id: UUID,
    order_id: UUID,
):
    order = await db.get(Order, order_id)
    if not order or order.user_id != user_id:
        not_found("Order")

    if order.status not in CANCELLABLE:
        bad_request("Order cannot be cancelled")

    order.status = OrderStatus.cancelled.value

    # 🔥 release inventory (global + store)
    await release_inventory_for_order(db, order_id)

    await db.commit()
    return {"status": "cancelled"}
