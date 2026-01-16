# app/services/payment_service.py
from app.schema.enums import PaymentStatus
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import uuid4, UUID
from sqlalchemy import select

from app.models.models import Payment, Order
from app.models.enums import payment_status_enum, order_status_enum
from app.utils.api_error import not_found, bad_request


# Order must be pending to pay
ALLOWED_PAYMENT_ORDER_STATUS = {"pending"}


async def process_dummy_payment(
    db: AsyncSession,
    user_id: UUID,
    order_id: UUID,
    provider: str = "dummy",
):
    order = await db.get(Order, order_id)
    if not order or order.user_id != user_id:
        not_found("Order")

    if order.status not in ALLOWED_PAYMENT_ORDER_STATUS:
        bad_request("Order is not payable")

    # prevent double payment
    existing = await db.execute(
        select(Payment).where(
            Payment.order_id == order_id,
            Payment.status == "success",
        )
    )
    if existing.scalar_one_or_none():
        bad_request("Order already paid")

    payment = Payment(
        id=uuid4(),
        order_id=order_id,
        provider=provider,
        status=PaymentStatus.success.value,
        amount=order.total,
    )

    order.status = "paid"

    db.add(payment)
    await db.commit()
    await db.refresh(payment)

    return payment
