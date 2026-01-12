# app/api/routers/orders.py
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from app.core.database import get_db
from app.core.auth import get_current_user
from app.services.order_service import (
    create_order,
    list_orders,
    cancel_order,
)
from app.schema.schemas import OrderCreate, OrderOut

router = APIRouter(prefix="/orders", tags=["Orders"])


@router.post("/", response_model=OrderOut)
async def create(
    payload: OrderCreate,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    return await create_order(db, user["user_id"], payload.address_id)


@router.get("/", response_model=list[OrderOut])
async def list_(
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    return await list_orders(db, user["user_id"])


@router.patch("/{order_id}/cancel")
async def cancel(
    order_id: UUID,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    await cancel_order(db, user["user_id"], order_id)
    return {"status": "cancelled"}
