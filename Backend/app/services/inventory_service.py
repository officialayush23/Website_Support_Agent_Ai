# app/services/inventory_service.py

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID
from sqlalchemy.orm import selectinload
from app.models.models import (
    Order,
    OrderItem,
    GlobalInventory,
    StoreInventory,
)
from app.utils.api_error import not_found


async def release_inventory_for_order(
    db: AsyncSession,
    order_id: UUID,
):
    res = await db.execute(
        select(Order)
        .where(Order.id == order_id)
        .options(selectinload(Order.items))
    )
    order = res.scalar_one_or_none()
    if not order:
        not_found("Order")

    for item in order.items:
        # 🔥 GLOBAL INVENTORY ALWAYS
        gi = await db.get(GlobalInventory, item.variant_id)
        if gi:
            gi.reserved_stock = max(
                0,
                gi.reserved_stock - item.quantity,
            )

        # 🔥 PICKUP → RESTORE STORE INVENTORY
        if order.fulfillment_type == "pickup" and order.store_id:
            inv = await db.get(
                StoreInventory,
                {
                    "store_id": order.store_id,
                    "variant_id": item.variant_id,
                }
            )
            if inv:
                inv.in_hand_stock += item.quantity

    await db.commit()
