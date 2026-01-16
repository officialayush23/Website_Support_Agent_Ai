# app/api/routers/pickups.py
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from sqlalchemy import select
from app.core.database import get_db
from app.core.auth import get_current_user
from app.core.ws_manager import ws_manager
from app.models.enums import pickup_status_enum
from app.models.models import Cart, CartItem
from app.services.pickup_service import (
    list_store_pickups,
    update_pickup_status,
    find_best_store_for_pickup,
    list_stores_that_can_fulfill_cart,
    list_pickups_for_store_dashboard,
)

from app.utils.api_error import forbidden, not_found

router = APIRouter(prefix="/pickups", tags=["Pickup"])


# =====================================================
# STORE DASHBOARD – LIST PICKUPS
# =====================================================

@router.get("/store/{store_id}")
async def store_pickups(
    store_id: UUID,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    if user["role"] not in ("admin", "store_manager"):
        forbidden()

    return await list_store_pickups(db, store_id)


# =====================================================
# UPDATE PICKUP STATUS
# =====================================================

@router.patch("/{pickup_id}")
async def update_status(
    pickup_id: UUID,
    status: str,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    if user["role"] not in ("admin", "store_manager"):
        forbidden()

    pickup = await update_pickup_status(
        db=db,
        pickup_id=pickup_id,
        status=status,
    )

    # 🔥 REAL-TIME STORE UI UPDATE
    await ws_manager.broadcast(
        channel=f"store:{pickup.store_id}:pickups",
        payload={
            "pickup_id": str(pickup.id),
            "order_id": str(pickup.order_id),
            "status": pickup.status,
            "picked_up_at": pickup.picked_up_at.isoformat()
            if pickup.picked_up_at
            else None,
        },
    )

    return {"status": "updated"}


# =====================================================
# AUTO PICKUP STORE (BEST)
# =====================================================

@router.get("/auto-store")
async def auto_pickup_store(
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    res = await db.execute(
        select(CartItem)
        .join(Cart)
        .where(Cart.user_id == user["user_id"])
    )
    items = res.scalars().all()

    if not items:
        not_found("Cart is empty")

    store = await find_best_store_for_pickup(
        db=db,
        user_id=user["user_id"],
        cart_items=[
            {"variant_id": i.variant_id, "quantity": i.quantity}
            for i in items
        ],
    )

    if not store:
        not_found("No store can fulfill full cart")

    return store


# =====================================================
# FALLBACK – USER SELECTABLE STORES
# =====================================================

@router.get("/eligible-stores")
async def eligible_stores(
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    """
    UI fallback when auto-pickup fails.
    """
    return await list_stores_that_can_fulfill_cart(
        db=db,
        user_id=user["user_id"],
    )


@router.get("/store/{store_id}/dashboard")
async def store_dashboard_pickups(
    store_id: UUID,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    if user["role"] not in ("admin", "store_manager"):
        forbidden()

    return await list_pickups_for_store_dashboard(
        db=db,
        store_id=store_id,
    )