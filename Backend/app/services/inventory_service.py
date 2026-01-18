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
    InventoryMovement,
)
from app.utils.api_error import not_found


async def release_inventory_for_order(
    db: AsyncSession,
    order_id: UUID,
):
    order = await db.get(
        Order,
        order_id,
        options=[selectinload(Order.items)],
    )
    if not order:
        not_found("Order")

    for item in order.items:
        gi = await db.get(GlobalInventory, item.product_id, with_for_update=True)
        gi.reserved_stock = max(0, gi.reserved_stock - item.quantity)

        db.add(
            InventoryMovement(
                product_id=item.product_id,
                source="global",
                destination=None,
                quantity=item.quantity,
                reason="order_cancelled",
                reference_type="order",
                reference_id=order.id,
            )
        )

    await db.commit()
