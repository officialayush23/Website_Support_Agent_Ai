# app/api/routers/complaints.py
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.core.database import get_db
from app.core.auth import get_current_user
from app.schema.schemas import ComplaintOut, ComplaintUpdate
from app.services.complaint_service import (
    list_complaints,
    update_complaint_status,
)
from app.utils.api_error import forbidden

router = APIRouter(prefix="/admin/complaints", tags=["Complaints"])


@router.get("/", response_model=list[ComplaintOut])
async def list_all(
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    if user["role"] not in ("admin", "support"):
        forbidden()

    return await list_complaints(db)


@router.patch("/{complaint_id}")
async def update_status(
    complaint_id: UUID,
    payload: ComplaintUpdate,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    if user["role"] not in ("admin", "support"):
        forbidden()

    c = await update_complaint_status(
        db=db,
        complaint_id=complaint_id,
        new_status=payload.status,
        actor=user["role"],
        confidence=0.9,
    )

    return {"status": c.status}
