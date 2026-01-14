# app/api/routers/stores.py

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text, func
from uuid import UUID

from app.core.database import get_db
from app.core.auth import get_current_user
from app.utils.api_error import forbidden, not_found

from app.services.store_service import (
    admin_catalog,
    list_stores,
    create_store,
    update_global_stock,
    update_stock,
    get_store_inventory,
    set_store_hours,
)

from app.schema.schemas import (
    GlobalStockUpdate,
    StoreCreate,
    StoreHourOut,
    StoreOut,
    InventoryUpdate,
    InventoryOut,
    StoreInventoryOut,
    StoreHourCreate,
)

from app.models.models import (
    Inventory,
    Order,
    Product,
    StoreWorkingHour,
    Pickup,
)

router = APIRouter(prefix="/stores", tags=["Stores"])


# ---------------------------
# STORES
# ---------------------------

@router.get("/", response_model=list[StoreOut])
async def list_(
    db: AsyncSession = Depends(get_db),
):
    """
    List all active stores.
    Uses RAW SQL internally to safely cast geography → geometry.
    """
    return await list_stores(db)


@router.post("/admin", response_model=StoreOut)
async def create(
    payload: StoreCreate,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    """
    Create a new store (ADMIN ONLY).
    Location is inserted using ST_SetSRID(ST_MakePoint).
    """
    if user["role"] != "admin":
        forbidden()

    return await create_store(db, payload.model_dump())


# ---------------------------
# INVENTORY
# ---------------------------

@router.patch("/admin/inventory", response_model=InventoryOut)
async def update_inventory(
    payload: InventoryUpdate,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    """
    Update per-store inventory allocation (ADMIN ONLY).
    Global stock consistency handled in service.
    """
    if user["role"] != "admin":
        forbidden()

    return await update_stock(
        db=db,
        store_id=payload.store_id,
        product_id=payload.product_id,
        stock=payload.stock,
    )


@router.get("/{store_id}/inventory", response_model=StoreInventoryOut)
async def store_inventory(
    store_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """
    Get inventory for a specific store with product details.
    """
    return await get_store_inventory(db, store_id)


# ---------------------------
# NEAREST STORES (GEO)
# ---------------------------

@router.get("/products/{product_id}/nearest-stores")
async def nearest_stores(
    product_id: UUID,
    radius_km: float = 10,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    """
    Find nearest open stores with stock for a product.
    Uses geography distance safely.
    """
    res = await db.execute(
        text("""
        SELECT 
            s.id,
            s.name,
            i.stock,
            ST_Distance(s.location, u.location) AS distance
        FROM stores s
        JOIN inventory i ON i.store_id = s.id
        JOIN users u ON u.id = :uid
        JOIN store_working_hours h ON h.store_id = s.id
        WHERE i.product_id = :pid
          AND i.stock > 0
          AND h.day_of_week = EXTRACT(DOW FROM now())
          AND h.is_closed = false
          AND now()::time BETWEEN h.opens_at AND h.closes_at
          AND ST_DWithin(s.location, u.location, :radius)
        ORDER BY distance
        LIMIT 5
        """),
        {
            "pid": product_id,
            "uid": user["user_id"],
            "radius": radius_km * 1000,
        },
    )

    return [
        {
            "store_id": r.id,
            "name": r.name,
            "stock": r.stock,
            "distance_m": r.distance,
        }
        for r in res
    ]


# ---------------------------
# STORE ORDERS & PICKUPS
# ---------------------------

@router.get("/{store_id}/orders")
async def store_orders(
    store_id: UUID,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    if user["role"] not in ("admin", "support"):
        forbidden()

    res = await db.execute(
        select(Order)
        .where(Order.store_id == store_id)
        .order_by(Order.created_at.desc())
    )
    return res.scalars().all()


@router.patch("/pickups/{pickup_id}")
async def update_pickup(
    pickup_id: UUID,
    status: str,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    if user["role"] not in ("admin", "support"):
        forbidden()

    pickup = await db.get(Pickup, pickup_id)
    if not pickup:
        not_found("Pickup")

    pickup.status = status
    if status == "picked_up":
        pickup.picked_up_at = func.now()

    await db.commit()
    return {"status": "updated"}


# ---------------------------
# STORE HOURS
# ---------------------------

@router.post("/admin/{store_id}/hours")
async def set_hours(
    store_id: UUID,
    payload: list[StoreHourCreate],
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    if user["role"] != "admin":
        forbidden()

    await set_store_hours(db, store_id, payload)
    return {"status": "updated"}


@router.get("/{store_id}/hours", response_model=list[StoreHourOut])
async def get_hours(
    store_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    res = await db.execute(
        select(StoreWorkingHour)
        .where(StoreWorkingHour.store_id == store_id)
        .order_by(StoreWorkingHour.day_of_week)
    )
    return res.scalars().all()


# ---------------------------
# ADMIN CATALOG & GLOBAL STOCK
# ---------------------------

@router.get("/admin/catalog")
async def admin_catalog_view(
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    if user["role"] != "admin":
        forbidden()

    return await admin_catalog(db)


@router.patch("/admin/global-stock")
async def update_global_stock_api(
    payload: GlobalStockUpdate,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    if user["role"] != "admin":
        forbidden()

    await update_global_stock(
        db,
        payload.product_id,
        payload.total_stock,
    )
    return {"status": "updated"}


from app.services.store_dashboard_service import get_store_dashboard

@router.get("/{store_id}/dashboard")
async def store_dashboard(
    store_id: UUID,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    if user["role"] not in ("admin", "store_manager"):
        forbidden()

    return await get_store_dashboard(db, store_id)