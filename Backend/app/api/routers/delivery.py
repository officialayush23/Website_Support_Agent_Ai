# app/api/routers/delivery.py
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.core.database import get_db
from app.core.auth import get_current_user
from app.schema.schemas import DeliveryCreate, DeliveryUpdate, DeliveryOut
from app.services.delivery_service import (
    create_delivery,
    update_delivery,
    get_delivery_for_order,
)
from app.utils.api_error import forbidden

router = APIRouter(prefix="/delivery", tags=["Delivery"])


@router.post("/admin", response_model=DeliveryOut)
async def create(
    payload: DeliveryCreate,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    if user["role"] not in ("admin", "support"):
        forbidden()

    return await create_delivery(db, payload.order_id)


@router.patch("/admin/{delivery_id}", response_model=DeliveryOut)
async def update(
    delivery_id: UUID,
    payload: DeliveryUpdate,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    if user["role"] not in ("admin", "support"):
        forbidden()

    return await update_delivery(
        db=db,
        delivery_id=delivery_id,
        new_status=payload.status,
        courier=payload.courier,
        tracking_id=payload.tracking_id,
        eta=payload.eta,
    )


@router.get("/order/{order_id}", response_model=DeliveryOut)
async def get_for_order(
    order_id: UUID,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    return await get_delivery_for_order(
        db=db,
        order_id=order_id,
        user_id=user["user_id"],
    )
