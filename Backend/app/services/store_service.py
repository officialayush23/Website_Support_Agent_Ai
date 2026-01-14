# app/services/store_service.py

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text, select, delete, func
from uuid import uuid4, UUID
from datetime import datetime

from app.models.models import (
    Store,
    Inventory,
    Product,
    StoreWorkingHour,
    GlobalInventory,
)
from app.schema.schemas import StoreHourCreate
from app.utils.api_error import not_found, bad_request


# ---------------------------------------------------
# STORES (RAW SQL – PostGIS SAFE)
# ---------------------------------------------------

async def list_stores(db: AsyncSession):
    """
    List active stores.
    Uses RAW SQL to safely cast geography → geometry.
    """
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
    """
    Create store with geography point safely.
    Expects latitude & longitude in payload.
    """
    store_id = uuid4()
    lat = data.pop("latitude")
    lng = data.pop("longitude")

    stmt = text("""
        INSERT INTO stores (
            id,
            name,
            city,
            state,
            location,
            is_active
        )
        VALUES (
            :id,
            :name,
            :city,
            :state,
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

    res = await db.execute(
        stmt,
        {
            "id": store_id,
            "name": data["name"],
            "city": data["city"],
            "state": data["state"],
            "lat": lat,
            "lng": lng,
        },
    )

    await db.commit()
    return res.mappings().first()


# ---------------------------------------------------
# STORE HOURS
# ---------------------------------------------------

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


async def is_store_open_now(db: AsyncSession, store_id: UUID) -> bool:
    now = datetime.utcnow()
    day = now.weekday()  # Monday = 0

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


# ---------------------------------------------------
# INVENTORY (GLOBAL + STORE-LEVEL – SAFE LOGIC)
# ---------------------------------------------------

async def update_stock(
    db: AsyncSession,
    store_id: UUID,
    product_id: UUID,
    stock: int,
):
    """
    Update store inventory while respecting global stock.
    """
    gi = await db.get(GlobalInventory, product_id)
    if not gi:
        not_found("Global inventory")

    existing = await db.get(
        Inventory,
        {"store_id": store_id, "product_id": product_id},
    )

    # Sum stock elsewhere
    res = await db.execute(
        select(func.coalesce(func.sum(Inventory.stock), 0))
        .where(
            Inventory.product_id == product_id,
            Inventory.store_id != store_id,
        )
    )
    allocated_elsewhere = res.scalar()

    new_reserved = allocated_elsewhere + stock
    if new_reserved > gi.total_stock:
        bad_request("Not enough global stock")

    if existing:
        existing.stock = stock
    else:
        existing = Inventory(
            store_id=store_id,
            product_id=product_id,
            stock=stock,
        )
        db.add(existing)

    gi.reserved_stock = new_reserved

    await db.commit()
    await db.refresh(existing)
    return existing


async def get_store_inventory(db: AsyncSession, store_id: UUID):
    store = await db.get(Store, store_id)
    if not store:
        not_found("Store")

    res = await db.execute(
        select(Inventory, Product)
        .join(Product, Product.id == Inventory.product_id)
        .where(Inventory.store_id == store_id)
    )

    items = [
        {
            "product_id": p.id,
            "product_name": p.name,
            "stock": inv.stock,
        }
        for inv, p in res.all()
    ]

    return {
        "store_id": store.id,
        "store_name": store.name,
        "items": items,
    }


# ---------------------------------------------------
# ADMIN CATALOG
# ---------------------------------------------------

async def admin_catalog(db: AsyncSession):
    res = await db.execute(
        select(
            Product.id,
            Product.name,
            Product.price,
            GlobalInventory.total_stock,
            GlobalInventory.reserved_stock,
        )
        .join(GlobalInventory, GlobalInventory.product_id == Product.id)
        .where(Product.is_active.is_(True))
    )

    return [
        {
            "product_id": r.id,
            "name": r.name,
            "price": float(r.price),
            "total_stock": r.total_stock,
            "reserved_stock": r.reserved_stock,
        }
        for r in res
    ]


# ---------------------------------------------------
# GLOBAL STOCK
# ---------------------------------------------------

async def update_global_stock(
    db: AsyncSession,
    product_id: UUID,
    total_stock: int,
):
    gi = await db.get(GlobalInventory, product_id)
    if not gi:
        not_found("Global inventory")

    if total_stock < gi.reserved_stock:
        bad_request("Cannot reduce below reserved stock")

    gi.total_stock = total_stock
    await db.commit()
    return gi
