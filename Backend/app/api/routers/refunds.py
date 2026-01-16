# app/api/routers/refunds.py
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.core.database import get_db
from app.core.auth import get_current_user
from app.schema.schemas import (
    RefundAdminOut,
    RefundCreate,
    RefundOut,
    RefundStatusUpdate,
)
from app.schema.enums import RefundStatus
from app.services.refund_service import (
    create,
    update_status,
    list_refunds,
    list_refunds_for_user,
)
from app.utils.api_error import forbidden

router = APIRouter(prefix="/refunds", tags=["Refunds"])


@router.post("/", response_model=RefundOut)
async def request_refund(
    payload: RefundCreate,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    return await create(
        db=db,
        user_id=user["user_id"],
        order_id=payload.order_id,
        reason=payload.reason,
    )


@router.patch("/{refund_id}")
async def admin_update_refund(
    refund_id: UUID,
    payload: RefundStatusUpdate,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    if user["role"] not in ("admin", "support"):
        forbidden()

    refund = await update_status(
        db=db,
        refund_id=refund_id,
        new_status=payload.status,  # 🔥 IMPORTANT
        actor=user["role"],
        confidence=0.95,
    )

    return {"status": refund.status}


@router.get("/admin", response_model=list[RefundAdminOut])
async def list_all(
    status: RefundStatus | None = None,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    if user["role"] not in ("admin", "support"):
        forbidden()

    return await list_refunds(
        db,
        status=status.value if status else None,
    )


@router.get("/me", response_model=list[RefundOut])
async def my_refunds(
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    return await list_refunds_for_user(db, user["user_id"])
