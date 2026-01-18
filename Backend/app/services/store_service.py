# app/services/store_service.py
# app/services/store_service.py

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text, select, delete, func
from uuid import uuid4, UUID
from datetime import datetime

from app.models.models import (
    Store,
    StoreInventory,
    StoreWorkingHour,
    GlobalInventory,
    Product,
    InventoryMovement,
)

from app.schema.schemas import StoreHourCreate
from app.utils.api_error import not_found, bad_request
from app.models.enums import fulfillment_target_enum


# =====================================================
# STORES
# =====================================================

async def list_stores(db: AsyncSession):
    stmt = text("""
        SELECT 
            id,
            name,
            city,
            state,
            ST_Y(location::geometry) AS latitude,
            ST_X(location::geometry) AS longitude,
            is_active
        FROM stores
        WHERE is_active = true
    """)
    res = await db.execute(stmt)
    return res.mappings().all()


async def create_store(db: AsyncSession, data: dict):
    store_id = uuid4()
    lat = data.pop("latitude")
    lng = data.pop("longitude")

    stmt = text("""
        INSERT INTO stores (
            id, name, city, state, location, is_active
        )
        VALUES (
            :id, :name, :city, :state,
            ST_SetSRID(ST_MakePoint(:lng, :lat), 4326),
            true
        )
        RETURNING
            id,
            name,
            city,
            state,
            ST_Y(location::geometry) AS latitude,
            ST_X(location::geometry) AS longitude,
            is_active
    """)

    res = await db.execute(stmt, {
        "id": store_id,
        "name": data["name"],
        "city": data["city"],
        "state": data["state"],
        "lat": lat,
        "lng": lng,
    })

    await db.commit()
    return res.mappings().first()


# =====================================================
# STORE HOURS
# =====================================================

async def set_store_hours(
    db: AsyncSession,
    store_id: UUID,
    hours: list[StoreHourCreate],
):
    await db.execute(
        delete(StoreWorkingHour)
        .where(StoreWorkingHour.store_id == store_id)
    )

    for h in hours:
        db.add(
            StoreWorkingHour(
                id=uuid4(),
                store_id=store_id,
                **h.model_dump(),
            )
        )

    await db.commit()


async def get_store_hours(
    db: AsyncSession,
    store_id: UUID,
):
    store = await db.get(Store, store_id)
    if not store:
        not_found("Store")

    res = await db.execute(
        select(StoreWorkingHour)
        .where(StoreWorkingHour.store_id == store_id)
        .order_by(StoreWorkingHour.day_of_week)
    )

    return res.scalars().all()


async def is_store_open_now(db: AsyncSession, store_id: UUID) -> bool:
    now = datetime.utcnow()
    day = now.weekday()

    res = await db.execute(
        select(StoreWorkingHour)
        .where(
            StoreWorkingHour.store_id == store_id,
            StoreWorkingHour.day_of_week == day,
            StoreWorkingHour.is_closed.is_(False),
            StoreWorkingHour.opens_at <= now.time(),
            StoreWorkingHour.closes_at >= now.time(),
        )
    )
    return res.scalar_one_or_none() is not None


# =====================================================
# INVENTORY (PRODUCT-BASED)
# =====================================================

async def allocate_inventory_to_store(
    db: AsyncSession,
    *,
    store_id: UUID,
    product_id: UUID,
    quantity: int,
):
    gi = await db.get(GlobalInventory, product_id, with_for_update=True)
    if not gi:
        not_found("Global inventory")

    available = gi.total_stock - gi.allocated_stock - gi.reserved_stock
    if quantity > 0 and available < quantity:
        bad_request("Insufficient global stock")

    inv = await db.get(
        StoreInventory,
        {"store_id": store_id, "product_id": product_id},
        with_for_update=True,
    )

    if not inv:
        inv = StoreInventory(
            store_id=store_id,
            product_id=product_id,
            allocated_stock=0,
            in_hand_stock=0,
        )
        db.add(inv)

    gi.allocated_stock += quantity
    inv.allocated_stock += quantity
    inv.in_hand_stock += quantity

    db.add(
        InventoryMovement(
            product_id=product_id,
            source=fulfillment_target_enum.global_inventory,
            destination=fulfillment_target_enum.store_inventory,
            quantity=quantity,
            reason="admin_allocation",
            reference_type="store",
            reference_id=store_id,
        )
    )

    await db.commit()
    await db.refresh(inv)
    return inv


async def update_store_inventory(
    db: AsyncSession,
    *,
    store_id: UUID,
    product_id: UUID,
    allocated_stock: int,
):
    gi = await db.get(GlobalInventory, product_id)
    if not gi:
        not_found("Global inventory")

    if allocated_stock < 0:
        bad_request("Invalid stock")

    res = await db.execute(
        select(func.coalesce(func.sum(StoreInventory.allocated_stock), 0))
        .where(
            StoreInventory.product_id == product_id,
            StoreInventory.store_id != store_id,
        )
    )
    allocated_elsewhere = res.scalar()

    if allocated_elsewhere + allocated_stock > gi.total_stock:
        bad_request("Exceeds global stock")

    inv = await db.get(
        StoreInventory,
        {"store_id": store_id, "product_id": product_id},
    )

    if inv:
        inv.allocated_stock = allocated_stock
        inv.in_hand_stock = allocated_stock
    else:
        inv = StoreInventory(
            store_id=store_id,
            product_id=product_id,
            allocated_stock=allocated_stock,
            in_hand_stock=allocated_stock,
        )
        db.add(inv)

    gi.allocated_stock = allocated_elsewhere + allocated_stock

    await db.commit()
    await db.refresh(inv)
    return inv


async def get_store_inventory(db: AsyncSession, store_id: UUID):
    store = await db.get(Store, store_id)
    if not store:
        not_found("Store")

    res = await db.execute(
        select(StoreInventory, Product)
        .join(Product, Product.id == StoreInventory.product_id)
        .where(StoreInventory.store_id == store_id)
    )

    return {
        "store_id": store.id,
        "store_name": store.name,
        "items": [
            {
                "product_id": p.id,
                "name": p.name,
                "price": float(p.price),
                "allocated_stock": inv.allocated_stock,
                "in_hand_stock": inv.in_hand_stock,
            }
            for inv, p in res.all()
        ],
    }


# =====================================================
# ADMIN
# =====================================================

async def admin_catalog(db: AsyncSession):
    res = await db.execute(
        select(
            Product.id,
            Product.name,
            Product.price,
            GlobalInventory.total_stock,
            GlobalInventory.allocated_stock,
            GlobalInventory.reserved_stock,
        )
        .join(GlobalInventory, GlobalInventory.product_id == Product.id)
    )

    return [
        {
            "product_id": r.id,
            "name": r.name,
            "price": float(r.price),
            "total_stock": r.total_stock,
            "allocated_stock": r.allocated_stock,
            "reserved_stock": r.reserved_stock,
            "available_stock": r.total_stock - r.allocated_stock - r.reserved_stock,
        }
        for r in res
    ]


async def update_global_stock(
    db: AsyncSession,
    *,
    product_id: UUID,
    total_stock: int,
):
    gi = await db.get(GlobalInventory, product_id)
    if not gi:
        not_found("Global inventory")

    if total_stock < gi.allocated_stock + gi.reserved_stock:
        bad_request("Below allocated/reserved")

    gi.total_stock = total_stock
    await db.commit()
    return gi
