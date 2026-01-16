# app/services/pickup_service.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text, func
from sqlalchemy.orm import selectinload
from uuid import UUID
from datetime import datetime

from app.models.models import (
    Pickup,
    Order,
    OrderItem,
    Store,
    StoreInventory,
    StoreWorkingHour,
    Cart,
    CartItem,
    User,
)
from app.models.enums import order_status_enum
from app.utils.api_error import not_found, bad_request
from app.schema.enums import PickupStatus


# =====================================================
# LIST PICKUPS FOR A STORE (ADMIN / STORE MANAGER)
# =====================================================

async def list_store_pickups(
    db: AsyncSession,
    store_id: UUID,
):
    res = await db.execute(
        select(Pickup)
        .where(Pickup.store_id == store_id)
        .options(
            selectinload(Pickup.order)
            .selectinload(Order.items)
            .selectinload(OrderItem.variant)
        )
        .order_by(Pickup.created_at.desc())
    )

    pickups = []
    for p in res.scalars():
        order = p.order
        pickups.append(
            {
                "pickup_id": p.id,
                "order_id": p.order_id,
                "status": p.status,
                "amount": float(p.amount),
                "created_at": order.created_at if order else None,
                "picked_up_at": p.picked_up_at,
                "items": [
                    {
                        "variant_id": i.variant_id,
                        "sku": i.variant.sku if i.variant else None,
                        "quantity": i.quantity,
                    }
                    for i in (order.items if order else [])
                ],
            }
        )

    return pickups


# =====================================================
# UPDATE PICKUP STATUS (FSM SAFE)
# =====================================================

VALID_TRANSITIONS: dict[PickupStatus, set[PickupStatus]] = {
    PickupStatus.ready: {PickupStatus.picked_up, PickupStatus.cancelled},
    PickupStatus.picked_up: set(),
    PickupStatus.cancelled: set(),
}

async def update_pickup_status(
    db: AsyncSession,
    *,
    pickup_id: UUID,
    status: PickupStatus,
):
    pickup = await db.get(Pickup, pickup_id)
    if not pickup:
        not_found("Pickup")

    current = PickupStatus(pickup.status)

    if status not in VALID_TRANSITIONS[current]:
        bad_request(f"Invalid transition {current.value} → {status.value}")

    pickup.status = status.value

    if status == PickupStatus.picked_up:
        pickup.picked_up_at = datetime.utcnow()

        # 🔥 FINAL BUSINESS RULE
        if pickup.order:
            pickup.order.status = order_status_enum.completed

    await db.commit()
    await db.refresh(pickup)
    return pickup



# =====================================================
# AUTO PICKUP STORE (BEST STORE)
# =====================================================

async def find_best_store_for_pickup(
    db: AsyncSession,
    *,
    user_id: UUID,
    cart_items: list[dict],  # [{variant_id, quantity}]
    radius_km: float = 25,
):
    if not cart_items:
        return None

    variant_ids = [i["variant_id"] for i in cart_items]
    qty_map = {i["variant_id"]: i["quantity"] for i in cart_items}

    # 🔥 SQL: candidate stores (open + nearby + have all variants)
    res = await db.execute(
        text("""
        SELECT
            s.id AS store_id,
            s.name,
            ST_Distance(s.location, u.location) AS distance
        FROM stores s
        JOIN users u ON u.id = :user_id
        JOIN store_working_hours h ON h.store_id = s.id
        JOIN store_inventory si ON si.store_id = s.id
        WHERE h.day_of_week = EXTRACT(DOW FROM now())
          AND h.is_closed = false
          AND now()::time BETWEEN h.opens_at AND h.closes_at
          AND ST_DWithin(s.location, u.location, :radius)
          AND si.variant_id = ANY(:variant_ids)
        GROUP BY s.id, u.location
        HAVING COUNT(DISTINCT si.variant_id) = :variant_count
        ORDER BY distance
        """),
        {
            "user_id": user_id,
            "radius": radius_km * 1000,
            "variant_ids": variant_ids,
            "variant_count": len(variant_ids),
        },
    )

    candidates = res.fetchall()
    if not candidates:
        return None

    # 🔍 Python stock validation (final gate)
    for row in candidates:
        inv_res = await db.execute(
            select(StoreInventory)
            .where(
                StoreInventory.store_id == row.store_id,
                StoreInventory.variant_id.in_(variant_ids),
            )
        )
        inventories = inv_res.scalars().all()

        if all(
            inv.in_hand_stock >= qty_map[inv.variant_id]
            for inv in inventories
        ):
            return {
                "store_id": row.store_id,
                "name": row.name,
                "distance_m": row.distance,
            }

    return None


# =====================================================
# FALLBACK: ALL STORES THAT CAN FULFILL CART
# =====================================================

async def list_stores_that_can_fulfill_cart(
    db: AsyncSession,
    *,
    user_id: UUID,
):
    res = await db.execute(
        select(CartItem)
        .join(Cart)
        .where(Cart.user_id == user_id)
    )
    items = res.scalars().all()

    if not items:
        bad_request("Cart is empty")

    variant_ids = [i.variant_id for i in items]
    qty_map = {i.variant_id: i.quantity for i in items}

    res = await db.execute(
        select(
            Store.id,
            Store.name,
            func.count(StoreInventory.variant_id).label("count"),
        )
        .join(StoreInventory, StoreInventory.store_id == Store.id)
        .where(
            StoreInventory.variant_id.in_(variant_ids),
            Store.is_active.is_(True),
        )
        .group_by(Store.id)
        .having(func.count(StoreInventory.variant_id) == len(variant_ids))
    )

    stores = []
    for s in res.all():
        inv_res = await db.execute(
            select(StoreInventory)
            .where(
                StoreInventory.store_id == s.id,
                StoreInventory.variant_id.in_(variant_ids),
            )
        )
        inventories = inv_res.scalars().all()

        if all(
            inv.in_hand_stock >= qty_map[inv.variant_id]
            for inv in inventories
        ):
            stores.append(
                {
                    "store_id": s.id,
                    "name": s.name,
                }
            )

    return stores




async def list_pickups_for_store_dashboard(
    db: AsyncSession,
    *,
    store_id: UUID,
):
    res = await db.execute(
        select(Pickup)
        .where(Pickup.store_id == store_id)
        .options(
            selectinload(Pickup.order)
            .selectinload(Order.items)
            .selectinload(OrderItem.variant)
        )
        .order_by(Pickup.created_at.desc())
    )

    return [
        {
            "pickup_id": p.id,
            "order_id": p.order_id,
            "status": p.status,
            "amount": float(p.amount),
            "created_at": p.created_at,
            "picked_up_at": p.picked_up_at,
            "items": [
                {
                    "variant_id": i.variant_id,
                    "sku": i.variant.sku,
                    "quantity": i.quantity,
                }
                for i in p.order.items
            ],
        }
        for p in res.scalars()
    ]
