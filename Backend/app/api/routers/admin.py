
# app/api/routers/admin.py

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from sqlalchemy import select, func
from app.core.database import get_db
from app.core.auth import get_current_user
from app.services.product_service import (
    create_product,
    update_product,
    delete_product,
)
from app.models.models import Order
from app.services.store_service import update_global_stock
from app.schema.schemas import ProductCreate, ProductUpdate, GlobalStockUpdate
from app.utils.api_error import forbidden
from app.services.catalog_service import product_variant_breakdown,product_quantity_overview
router = APIRouter(prefix="/admin", tags=["Admin"])


def admin_only(user):
    if user["role"] != "admin":
        forbidden()
from app.models.models import GlobalInventory, ProductVariant

@router.get("/inventory/stats")
async def inventory_stats(
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    """
    Returns high-level inventory KPIs for the Admin Dashboard.
    """
    if user["role"] != "admin":
        forbidden()

    # Total Value (Price * Total Stock)
    stmt_value = select(
        func.sum(GlobalInventory.total_stock * ProductVariant.price)
    ).join(ProductVariant, ProductVariant.id == GlobalInventory.variant_id)
    
    # Low Stock Count (< 10 items)
    stmt_low = select(func.count(GlobalInventory.variant_id)).where(GlobalInventory.total_stock < 10)

    # Total Items
    stmt_count = select(func.sum(GlobalInventory.total_stock))

    value = (await db.execute(stmt_value)).scalar() or 0
    low_stock = (await db.execute(stmt_low)).scalar() or 0
    total_items = (await db.execute(stmt_count)).scalar() or 0

    return {
        "total_value": float(value),
        "low_stock_variants": low_stock,
        "total_items": total_items
    }

@router.post("/products")
async def create(
    payload: ProductCreate,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    admin_only(user)
    p = await create_product(db, **payload.model_dump())
    return {"id": p.id}


@router.patch("/products/{product_id}")
async def update(
    product_id: UUID,
    payload: ProductUpdate,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    admin_only(user)
    await update_product(
        db=db,
        product_id=product_id,
        data=payload.model_dump(exclude_unset=True),
    )
    return {"status": "updated"}


@router.delete("/products/{product_id}")
async def delete(
    product_id: UUID,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    admin_only(user)
    await delete_product(db=db, product_id=product_id)
    return {"status": "deleted"}


@router.patch("/inventory/global")
async def set_global_stock(
    payload: GlobalStockUpdate,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    admin_only(user)
    await update_global_stock(
        db=db,
        variant_id=payload.variant_id,
        total_stock=payload.total_stock,
    )
    return {"status": "updated"}


@router.get("/summary")
async def kpi_summary(
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    if user["role"] != "admin":
        forbidden()

    res = await db.execute(
        select(
            func.count(Order.id),
            func.sum(Order.total),
        )
    )

    orders, revenue = res.first()

    return {
        "total_orders": orders or 0,
        "total_revenue": float(revenue or 0),
    }

@router.get("/products/stock")
async def product_stock_overview(
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    admin_only(user)
    return await product_quantity_overview(db)


@router.get("/products/{product_id}/stock")
async def product_stock_detail(
    product_id: UUID,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    admin_only(user)
    return await product_variant_breakdown(db, product_id)
