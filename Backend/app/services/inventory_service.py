# app/services/inventory_service.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID

from app.models.models import (
    Order,
    OrderItem,
    GlobalInventory,
    Inventory,
)
from app.utils.api_error import not_found


async def release_inventory_for_order(
    db: AsyncSession,
    order_id: UUID,
):
    order = await db.execute(
        select(Order)
        .where(Order.id == order_id)
        .options(
            selectinload(Order.items)
        )
    )
    order = order.scalar_one_or_none()
    if not order:
        not_found("Order")

    # DELIVERY → global inventory
    if order.fulfillment_type == "delivery":
        for item in order.items:
            gi = await db.get(GlobalInventory, item.product_id)
            if gi:
                gi.reserved_stock = max(
                    0,
                    gi.reserved_stock - item.quantity
                )

    # PICKUP → store inventory + global
    if order.fulfillment_type == "pickup" and order.store_id:
        for item in order.items:
            inv = await db.get(
                Inventory,
                {
                    "store_id": order.store_id,
                    "product_id": item.product_id,
                }
            )
            if inv:
                inv.stock += item.quantity

            gi = await db.get(GlobalInventory, item.product_id)
            if gi:
                gi.reserved_stock = max(
                    0,
                    gi.reserved_stock - item.quantity
                )

    await db.commit()
