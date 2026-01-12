# app/services/refund_service.py
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import uuid4, UUID
from decimal import Decimal

from app.models.models import Refund, Order, AgentAction
from app.models.py_enums import RefundStatus, OrderStatus
from app.models.enums import agent_action_status_enum
from app.utils.api_error import not_found, bad_request


# ---------- Order states that allow refund ----------
REFUND_ALLOWED_ORDER_STATUS = {
    OrderStatus.paid,
    OrderStatus.delivered,
}


# ---------- Refund state machine ----------
REFUND_TRANSITIONS = {
    RefundStatus.initiated: {
        RefundStatus.approved,
        RefundStatus.rejected,
    },
    RefundStatus.approved: {RefundStatus.completed},
    RefundStatus.rejected: set(),
    RefundStatus.completed: set(),
}


# ---------- User requests refund ----------
async def create(
    db: AsyncSession,
    user_id: UUID,
    order_id: UUID,
    reason: str,
):
    order = await db.get(Order, order_id)
    if not order or order.user_id != user_id:
        not_found("Order")

    current_order_status = OrderStatus(order.status)

    if current_order_status not in REFUND_ALLOWED_ORDER_STATUS:
        bad_request("Refund not allowed for this order status")

    refund = Refund(
        id=uuid4(),
        order_id=order_id,
        reason=reason,
        status=RefundStatus.initiated,   # ✅ enum
    )

    db.add(refund)
    await db.commit()
    await db.refresh(refund)

    return refund


# ---------- Admin / Support updates refund ----------
async def update_status(
    db: AsyncSession,
    refund_id: UUID,
    new_status: RefundStatus,
    *,
    actor: str,
    conversation_id: UUID | None = None,
    confidence: float = 1.0,
):
    refund = await db.get(Refund, refund_id)
    if not refund:
        not_found("Refund")

    current = RefundStatus(refund.status)

    # 🔒 Lock illegal transitions
    if new_status not in REFUND_TRANSITIONS[current]:
        bad_request(
            f"Invalid transition {current.value} → {new_status.value}"
        )

    refund.status = new_status
    db.add(refund)

    # 🧾 Agent action log
    action = AgentAction(
        id=uuid4(),
        conversation_id=conversation_id,
        action_type="update_refund_status",
        payload={
            "refund_id": str(refund_id),
            "from": current.value,
            "to": new_status.value,
            "actor": actor,
        },
        status=agent_action_status_enum.executed,
        confidence=Decimal(str(confidence)),
    )
    db.add(action)

    await db.commit()
    await db.refresh(refund)

    return refund


# ---------- User checks refund status ----------
async def get_status(
    db: AsyncSession,
    user_id: UUID,
    refund_id: UUID,
):
    refund = await db.get(Refund, refund_id)
    if not refund:
        not_found("Refund")

    order = await db.get(Order, refund.order_id)
    if not order or order.user_id != user_id:
        not_found("Refund")

    return {"status": refund.status.value}
