# app/services/refund_service.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from uuid import uuid4, UUID
from decimal import Decimal
from app.services.inventory_service import release_inventory_for_order
from app.schema.enums import RefundStatus
from app.models.models import Refund, Order, AgentAction
from app.models.enums import agent_action_status_enum
from app.utils.api_error import not_found, bad_request


# ---------- Order states that allow refund ----------
REFUND_ALLOWED_ORDER_STATUS = {"paid", "delivered"}


# ---------- Refund state machine ----------
REFUND_TRANSITIONS = {
    "initiated": {"approved", "rejected"},
    "approved": {"completed"},
    "rejected": set(),
    "completed": set(),
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

    if order.status not in REFUND_ALLOWED_ORDER_STATUS:
        bad_request("Refund not allowed for this order status")

    refund = Refund(
        id=uuid4(),
        order_id=order_id,
        reason=reason,
        status="initiated",
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

    if new_status not in REFUND_TRANSITIONS[current]:
        bad_request(
            f"Invalid transition {current.value} → {new_status.value}"
        )

    refund.status = new_status.value

    # 🔥 inventory is restored ONLY on completed
    if new_status == RefundStatus.completed:
        await release_inventory_for_order(db, refund.order_id)

    db.add(
        AgentAction(
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
    )

    await db.commit()
    await db.refresh(refund)
    return refund

# ---------- Admin: list refunds ----------
async def list_refunds(
    db: AsyncSession,
    status: str | None = None,
):
    q = (
        select(Refund)
        .options(selectinload(Refund.order))
        .order_by(Refund.created_at.desc())
    )

    if status:
        q = q.where(Refund.status == status)

    res = await db.execute(q)
    refunds = res.scalars().all()

    return [
        {
            "id": r.id,
            "order_id": r.order_id,
            "reason": r.reason,
            "status": r.status,
            "created_at": r.created_at,
            "amount": float(r.order.total),
        }
        for r in refunds
    ]


# ---------- User refunds ----------
async def list_refunds_for_user(
    db: AsyncSession,
    user_id: UUID,
):
    res = await db.execute(
        select(Refund)
        .join(Refund.order)
        .options(selectinload(Refund.order))
        .where(Order.user_id == user_id)
        .order_by(Refund.created_at.desc())
    )
    return res.scalars().all()
