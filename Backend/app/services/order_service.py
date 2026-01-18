# app/services/order_service.py
from uuid import UUID, uuid4
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models.models import (
    Order,
    OrderItem,
    OrderStatusHistory,
    AgentAction,
    Complaint,
    Delivery,
    Payment,
    Pickup,
    Refund,
)
from app.schema.enums import OrderStatus
from app.services.inventory_service import release_inventory_for_order
from app.utils.api_error import bad_request, not_found


CANCELLABLE = {OrderStatus.pending.value}


async def list_orders(db: AsyncSession, user_id: UUID):
    res = await db.execute(
        select(Order)
        .where(Order.user_id == user_id)
        .options(selectinload(Order.items))
        .order_by(Order.created_at.desc())
    )
    return res.scalars().all()


async def get_order(db: AsyncSession, user_id: UUID, order_id: UUID):
    order = await db.get(
        Order,
        order_id,
        options=[selectinload(Order.items)],
    )
    if not order or order.user_id != user_id:
        not_found("Order")
    return order


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
    await release_inventory_for_order(db, order_id)
    await db.commit()

    return {"status": "cancelled"}


async def get_order_detail(
    db: AsyncSession,
    *,
    order_id: UUID,
    user_id: UUID,
):
    res = await db.execute(
        select(Order)
        .where(Order.id == order_id, Order.user_id == user_id)
        .options(
            selectinload(Order.items).selectinload(OrderItem.product),
            selectinload(Order.store),
        )
    )

    order = res.scalar_one_or_none()
    if not order:
        not_found("Order")

    return {
        "id": order.id,
        "status": order.status,
        "fulfillment_type": order.fulfillment_type,
        "store": (
            {
                "id": order.store.id,
                "name": order.store.name,
                "city": order.store.city,
            }
            if order.store
            else None
        ),
        "subtotal": float(order.subtotal),
        "discount_total": float(order.discount_total),
        "total": float(order.total),
        "items": [
            {
                "product_id": i.product_id,
                "name": i.product.name,
                "quantity": i.quantity,
                "price": float(i.price),
            }
            for i in order.items
        ],
        "created_at": order.created_at,
    }


async def get_order_timeline(
    db: AsyncSession,
    *,
    order_id: UUID,
    user_id: UUID,
):
    order = await db.get(Order, order_id)
    if not order or order.user_id != user_id:
        not_found("Order")

    history = await db.execute(
        select(OrderStatusHistory)
        .where(OrderStatusHistory.order_id == order_id)
        .order_by(OrderStatusHistory.created_at)
    )

    return {
        "order": order,
        "history": history.scalars().all(),
        "payments": (await db.execute(select(Payment).where(Payment.order_id == order_id))).scalars().all(),
        "delivery": (await db.execute(select(Delivery).where(Delivery.order_id == order_id))).scalar_one_or_none(),
        "pickup": (await db.execute(select(Pickup).where(Pickup.order_id == order_id))).scalar_one_or_none(),
        "refunds": (await db.execute(select(Refund).where(Refund.order_id == order_id))).scalars().all(),
        "complaints": (await db.execute(select(Complaint).where(Complaint.order_id == order_id))).scalars().all(),
        "agent_actions": (
            await db.execute(
                select(AgentAction)
                .where(AgentAction.payload["order_id"].astext == str(order_id))
                .order_by(AgentAction.created_at)
            )
        ).scalars().all(),
    }


async def log_order_status(db, order_id, status):
    db.add(
        OrderStatusHistory(
            id=uuid4(),
            order_id=order_id,
            status=status,
        )
    )
