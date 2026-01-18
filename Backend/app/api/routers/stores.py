# app/api/routers/stores.py
# app/api/routers/stores.py

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.core.database import get_db
from app.core.auth import get_current_user
from app.utils.api_error import forbidden

from app.services.store_service import (
    list_stores,
    create_store,
    admin_catalog,
    update_global_stock,
    update_store_inventory,
    get_store_inventory,
    set_store_hours,
    allocate_inventory_to_store,
    get_store_hours,
)

from app.schema.schemas import (
    StoreCreate,
    StoreOut,
    StoreHourCreate,
    StoreHourOut,
    GlobalStockUpdate,
    StoreInventoryOut,
    InventoryUpdate,
    StockAllocation,
)

router = APIRouter(prefix="/stores", tags=["Stores"])


# =====================================================
# STORES
# =====================================================

@router.get("/", response_model=list[StoreOut])
async def list_(
    db: AsyncSession = Depends(get_db),
):
    return await list_stores(db)


@router.post("/admin", response_model=StoreOut)
async def create(
    payload: StoreCreate,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    if user["role"] != "admin":
        forbidden()

    return await create_store(db, payload.model_dump())


# =====================================================
# INVENTORY (PRODUCT-BASED)
# =====================================================

@router.patch("/admin/inventory", response_model=StoreInventoryOut)
async def update_inventory(
    payload: InventoryUpdate,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    if user["role"] != "admin":
        forbidden()

    return await update_store_inventory(
        db=db,
        store_id=payload.store_id,
        product_id=payload.product_id,
        allocated_stock=payload.allocated_stock,
    )


@router.get("/{store_id}/inventory", response_model=StoreInventoryOut)
async def store_inventory(
    store_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    return await get_store_inventory(db, store_id)


# =====================================================
# STORE HOURS
# =====================================================

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
    return await get_store_hours(db, store_id)


# =====================================================
# ALLOCATION (GLOBAL → STORE)
# =====================================================

@router.post("/{store_id}/allocate", response_model=StoreInventoryOut)
async def allocate_stock_endpoint(
    store_id: UUID,
    payload: StockAllocation,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    if user["role"] != "admin":
        forbidden()

    return await allocate_inventory_to_store(
        db=db,
        store_id=store_id,
        product_id=payload.product_id,
        quantity=payload.quantity,
    )


# =====================================================
# ADMIN
# =====================================================

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
        db=db,
        product_id=payload.product_id,
        total_stock=payload.total_stock,
    )
    return {"status": "updated"}
