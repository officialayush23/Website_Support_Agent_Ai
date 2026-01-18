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
from app.models.enums import fulfillment_target_enum
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
        if order.fulfillment_type == "delivery":
            gi = await db.get(GlobalInventory, item.variant_id, with_for_update=True)
            gi.reserved_stock = max(0, gi.reserved_stock - item.quantity)

            db.add(
                InventoryMovement(
                    variant_id=item.variant_id,
                    source=fulfillment_target_enum.global_inventory,
                    destination=None,
                    quantity=item.quantity,
                    reason="order_cancelled",
                    reference_type="order",
                    reference_id=order.id,
                )
            )

        else:  # pickup
            inv = await db.get(
                StoreInventory,
                {
                    "store_id": order.store_id,
                    "variant_id": item.variant_id,
                },
                with_for_update=True,
            )
            inv.in_hand_stock += item.quantity

            db.add(
                InventoryMovement(
                    variant_id=item.variant_id,
                    source=fulfillment_target_enum.store_inventory,
                    destination=None,
                    quantity=item.quantity,
                    reason="pickup_cancelled",
                    reference_type="order",
                    reference_id=order.id,
                )
            )

    await db.commit()
