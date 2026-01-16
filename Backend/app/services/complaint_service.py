# app/services/complaint_service.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from uuid import UUID, uuid4
from decimal import Decimal

from app.models.models import Complaint, AgentAction
from app.models.enums import (
    agent_action_status_enum,
    complaint_created_by_enum,
)
from app.schema.enums import ComplaintStatus
from app.utils.api_error import not_found, bad_request


# ---------- FSM ----------
ALLOWED_TRANSITIONS = {
    ComplaintStatus.open: {ComplaintStatus.in_progress},
    ComplaintStatus.in_progress: {ComplaintStatus.resolved},
    ComplaintStatus.resolved: set(),
}


# ---------- User creates complaint ----------
async def create(
    db: AsyncSession,
    user_id: UUID,
    order_id: UUID,
    desc: str,
):
    complaint = Complaint(
        id=uuid4(),
        user_id=user_id,
        order_id=order_id,
        description=desc,
        status=ComplaintStatus.open.value,
        created_by=complaint_created_by_enum.user,
    )

    db.add(complaint)
    await db.commit()
    await db.refresh(complaint)
    return complaint


# ---------- User checks status ----------
async def get_status(
    db: AsyncSession,
    user_id: UUID,
    complaint_id: UUID,
):
    c = await db.get(Complaint, complaint_id)
    if not c or c.user_id != user_id:
        not_found("Complaint")

    return {"status": c.status}


# ---------- Admin / Support updates ----------
async def update_complaint_status(
    db: AsyncSession,
    complaint_id: UUID,
    new_status: ComplaintStatus,
    *,
    actor: str,
    conversation_id: UUID | None = None,
    confidence: float = 1.0,
):
    c = await db.get(Complaint, complaint_id)
    if not c:
        not_found("Complaint")

    current = ComplaintStatus(c.status)

    if new_status not in ALLOWED_TRANSITIONS[current]:
        bad_request(
            f"Invalid transition {current.value} → {new_status.value}"
        )

    c.status = new_status.value

    db.add(
        AgentAction(
            id=uuid4(),
            conversation_id=conversation_id,
            action_type="update_complaint_status",
            payload={
                "complaint_id": str(complaint_id),
                "from": current.value,
                "to": new_status.value,
                "actor": actor,
            },
            status=agent_action_status_enum.executed,
            confidence=Decimal(str(confidence)),
        )
    )

    await db.commit()
    await db.refresh(c)
    return c


# ---------- Admin list ----------
async def list_complaints(db: AsyncSession):
    res = await db.execute(
        select(Complaint)
        .order_by(Complaint.created_at.desc())
    )
    return res.scalars().all()


async def list_complaints_with_order(db: AsyncSession):
    res = await db.execute(
        select(Complaint)
        .options(selectinload(Complaint.order))
        .order_by(Complaint.created_at.desc())
    )
    return res.scalars().all()