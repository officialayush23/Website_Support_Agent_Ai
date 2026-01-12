# app/api/routers/payments.py
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.auth import get_current_user
from app.schema.schemas import PaymentCreate, PaymentOut
from app.services.payment_service import process_dummy_payment

router = APIRouter(prefix="/payments", tags=["Payments"])


@router.post("/dummy", response_model=PaymentOut)
async def pay_dummy(
    payload: PaymentCreate,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    return await process_dummy_payment(
        db=db,
        user_id=user["user_id"],   # ✅ ownership enforced
        order_id=payload.order_id,
        provider=payload.provider,
    )
