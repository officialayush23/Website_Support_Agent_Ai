# app/api/routers/carts.py
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from app.schema.schemas import CheckoutCreate, OrderOut
from app.core.database import get_db
from app.services.cart_service import checkout
from app.core.auth import get_current_user
from app.services.cart_service import (
    get_cart_items,
    add_item,
    update_item,
    clear_cart,
)
from app.schema.schemas import CartItemCreate, CartItemUpdate

router = APIRouter(prefix="/cart", tags=["Cart"])


@router.get("/")
async def view_cart(
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    return await get_cart_items(db, user["user_id"])


@router.post("/items")
async def add(
    payload: CartItemCreate,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    await add_item(
        db=db,
        user_id=user["user_id"],
        product_id=payload.product_id,
        qty=payload.quantity,
    )
    return {"status": "added"}


@router.patch("/items/{product_id}")
async def update(
    product_id: UUID,
    payload: CartItemUpdate,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    await update_item(
        db=db,
        user_id=user["user_id"],
        product_id=product_id,
        qty=payload.quantity,
    )
    return {"status": "updated"}


@router.delete("/")
async def clear(
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    await clear_cart(db, user["user_id"])
    return {"status": "cleared"}


@router.post("/checkout", response_model=OrderOut)
async def checkout_api(
    payload: CheckoutCreate,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    return await checkout(
        db=db,
        user_id=user["user_id"],
        payload=payload,
    )
