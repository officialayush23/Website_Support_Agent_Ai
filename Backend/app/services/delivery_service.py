# app/services/delivery_service.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from uuid import UUID, uuid4
from datetime import datetime

from app.models.models import Delivery, Order, OrderItem
from app.models.enums import delivery_status_enum, order_status_enum
from app.schema.enums import DeliveryStatus, OrderStatus
from app.utils.api_error import not_found, bad_request
from app.services.agent_action_service import log_agent_action
from app.services.handoff_service import escalate_to_human


# ---------------- DELIVERY FSM ---------------- #

DELIVERY_TRANSITIONS = {
    DeliveryStatus.pending: {
        DeliveryStatus.assigned,
        DeliveryStatus.cancelled,
    },
    DeliveryStatus.assigned: {
        DeliveryStatus.out_for_delivery,
        DeliveryStatus.failed,
    },
    DeliveryStatus.out_for_delivery: {
        DeliveryStatus.delivered,
        DeliveryStatus.failed,
    },
    DeliveryStatus.delivered: set(),
    DeliveryStatus.failed: set(),
    DeliveryStatus.cancelled: set(),
}

ORDER_SYNC = {
    DeliveryStatus.delivered: OrderStatus.delivered,
    DeliveryStatus.cancelled: OrderStatus.cancelled,
}


# ---------------- ADMIN LIST ---------------- #

async def list_deliveries_admin(db: AsyncSession):
    res = await db.execute(
        select(Delivery)
        .options(
            selectinload(Delivery.order)
            .selectinload(Order.items)
            .selectinload(OrderItem.product)
        )
        .order_by(Delivery.created_at.desc())
    )

    deliveries = []
    for d in res.scalars():
        deliveries.append({
            "delivery_id": d.id,
            "status": d.status,
            "courier": d.courier,
            "tracking_id": d.tracking_id,
            "order_id": d.order_id,
            "user_id": d.user_id,
            "total": float(d.order.total),
            "products": [
                {
                    "product_id": i.product.id,
                    "name": i.product.name,
                    "quantity": i.quantity,
                    "price": float(i.price),
                }
                for i in d.order.items
            ],
        })

    return deliveries


# ---------------- CREATE ---------------- #

async def create_delivery(
    db: AsyncSession,
    order_id: UUID,
    conversation_id: UUID | None = None,
):
    order = await db.get(Order, order_id)
    if not order:
        not_found("Order")

    delivery = Delivery(
        id=uuid4(),
        order_id=order.id,
        user_id=order.user_id,
        address_id=order.address_id,
        status=delivery_status_enum.pending,
    )

    db.add(delivery)
    await db.commit()
    await db.refresh(delivery)

    await log_agent_action(
        db=db,
        conversation_id=conversation_id,
        action_type="create_delivery",
        payload={
            "order_id": str(order_id),
            "delivery_id": str(delivery.id),
        },
        confidence=0.95,
    )

    return delivery


# ---------------- UPDATE ---------------- #

async def update_delivery(
    db: AsyncSession,
    delivery_id: UUID,
    new_status: DeliveryStatus,
    courier: str | None = None,
    tracking_id: str | None = None,
    eta: datetime | None = None,
    conversation_id: UUID | None = None,
):
    delivery = await db.get(Delivery, delivery_id)
    if not delivery:
        not_found("Delivery")

    current = DeliveryStatus(delivery.status)

    if new_status not in DELIVERY_TRANSITIONS[current]:
        await escalate_to_human(
            db,
            conversation_id,
            reason=f"Illegal delivery transition {current.value} → {new_status.value}",
        )
        bad_request(
            f"Invalid delivery transition {current.value} → {new_status.value}"
        )

    delivery.status = new_status.value

    if courier is not None:
        delivery.courier = courier
    if tracking_id is not None:
        delivery.tracking_id = tracking_id
    if eta is not None:
        delivery.eta = eta

    if new_status in ORDER_SYNC:
        order = await db.get(Order, delivery.order_id)
        order.status = ORDER_SYNC[new_status].value

    await db.commit()
    await db.refresh(delivery)

    await log_agent_action(
        db=db,
        conversation_id=conversation_id,
        action_type="update_delivery",
        payload={
            "delivery_id": str(delivery_id),
            "from": current.value,
            "to": new_status.value,
        },
        confidence=0.85,
    )

    return delivery


# ---------------- USER FETCH ---------------- #

async def get_delivery_for_order(
    db: AsyncSession,
    order_id: UUID,
    user_id: UUID,
):
    res = await db.execute(
        select(Delivery)
        .where(
            Delivery.order_id == order_id,
            Delivery.user_id == user_id,
        )
    )

    delivery = res.scalar_one_or_none()
    if not delivery:
        not_found("Delivery")

    return delivery
