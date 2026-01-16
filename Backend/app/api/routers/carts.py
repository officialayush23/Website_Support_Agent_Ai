# app/api/routers/carts.py
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.core.database import get_db
from app.core.auth import get_current_user

from app.schema.schemas import (
    CartItemCreate,
    CartItemUpdate,
    CheckoutCreate,
)

from app.services.cart_service import (
    get_cart_items,
    add_item,
    update_item,
    clear_cart,
    checkout,
    preview_cart_offers,
    list_stores_that_can_fulfill_cart,
)

router = APIRouter(prefix="/cart", tags=["Cart"])


# =====================================================
# VIEW CART
# =====================================================

@router.get("/")
async def view_cart(
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    """
    UI-safe cart view.
    Includes variant, product, attributes, totals.
    """
    return await get_cart_items(
        db=db,
        user_id=user["user_id"],
    )


# =====================================================
# ADD ITEM (VARIANT BASED)
# =====================================================

@router.post("/items")
async def add_to_cart(
    payload: CartItemCreate,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    """
    Adds a variant to cart.
    """
    await add_item(
        db=db,
        user_id=user["user_id"],
        variant_id=payload.variant_id,
        quantity=payload.quantity,
    )
    return {"status": "added"}


# =====================================================
# UPDATE ITEM
# =====================================================

@router.patch("/items/{variant_id}")
async def update_cart_item(
    variant_id: UUID,
    payload: CartItemUpdate,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    """
    Update quantity.
    quantity = 0 → remove.
    """
    await update_item(
        db=db,
        user_id=user["user_id"],
        variant_id=variant_id,
        quantity=payload.quantity,
    )
    return {"status": "updated"}


# =====================================================
# REMOVE ITEM (EXPLICIT)
# =====================================================

@router.delete("/items/{variant_id}")
async def remove_cart_item(
    variant_id: UUID,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    await update_item(
        db=db,
        user_id=user["user_id"],
        variant_id=variant_id,
        quantity=0,
    )
    return {"status": "removed"}


# =====================================================
# CLEAR CART
# =====================================================

@router.delete("/")
async def clear(
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    await clear_cart(
        db=db,
        user_id=user["user_id"],
    )
    return {"status": "cleared"}


# =====================================================
# OFFER PREVIEW (IMPORTANT FOR UI)
# =====================================================

@router.get("/offers")
async def preview_offers(
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    """
    Returns:
    - subtotal
    - eligible offers
    - best discount
    - payable amount
    """
    return await preview_cart_offers(
        db=db,
        user_id=user["user_id"],
    )


# =====================================================
# PICKUP FALLBACK (MANUAL STORE SELECTION)
# =====================================================

@router.get("/pickup/stores")
async def eligible_pickup_stores(
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    """
    Fallback when auto-pickup fails.
    Returns ALL stores that can fulfill ENTIRE cart.
    """
    return await list_stores_that_can_fulfill_cart(
        db=db,
        user_id=user["user_id"],
    )


# =====================================================
# CHECKOUT
# =====================================================

@router.post("/checkout")
async def checkout_cart(
    payload: CheckoutCreate,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    """
    Canonical checkout.
    - delivery OR pickup
    - auto-store OR manual store_id
    """
    return await checkout(
        db=db,
        user_id=user["user_id"],
        payload=payload,
    )
