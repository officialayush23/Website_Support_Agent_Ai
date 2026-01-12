# app/api/routers/complaints.py
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.core.database import get_db
from app.core.auth import get_current_user
from app.schema.schemas import ComplaintUpdate
from app.services.complaint_service import update_complaint_status
from app.utils.api_error import forbidden

router = APIRouter(prefix="/admin/complaints", tags=["Complaints"])


@router.patch("/{complaint_id}")
async def update_status(
    complaint_id: UUID,
    payload: ComplaintUpdate,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    if user["role"] not in ("admin", "support"):
        forbidden()

    await update_complaint_status(
        db=db,
        complaint_id=complaint_id,
        new_status=payload.status,   # ✅ ENUM PASSED
        actor=user["role"],
        confidence=0.9,              # can be dynamic later
    )

    return {"status": payload.status.value}
