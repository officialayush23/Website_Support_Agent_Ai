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
from app.models.models import Order, GlobalInventory, Product
from app.services.store_service import update_global_stock
from app.schema.schemas import ProductCreate, ProductUpdate, GlobalStockUpdate
from app.utils.api_error import forbidden

router = APIRouter(prefix="/admin", tags=["Admin"])


def admin_only(user):
    if user["role"] != "admin":
        forbidden()


# =====================================================
# INVENTORY KPIs
# =====================================================

@router.get("/inventory/stats")
async def inventory_stats(
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    admin_only(user)

    stmt_value = select(
        func.sum(GlobalInventory.total_stock * Product.price)
    ).join(Product, Product.id == GlobalInventory.product_id)

    stmt_low = select(
        func.count(GlobalInventory.product_id)
    ).where(GlobalInventory.total_stock < 10)

    stmt_count = select(func.sum(GlobalInventory.total_stock))

    value = (await db.execute(stmt_value)).scalar() or 0
    low_stock = (await db.execute(stmt_low)).scalar() or 0
    total_items = (await db.execute(stmt_count)).scalar() or 0

    return {
        "total_value": float(value),
        "low_stock_products": low_stock,
        "total_items": total_items,
    }


# =====================================================
# PRODUCTS
# =====================================================

@router.post("/products")
async def create(
    payload: ProductCreate,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    admin_only(user)

    product = await create_product(
        db=db,
        name=payload.name,
        description=payload.description,
        category=payload.category,
        price=payload.price,
        images=payload.images,
    )
    return {"id": product.id}


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


# =====================================================
# GLOBAL INVENTORY
# =====================================================

@router.patch("/inventory/global")
async def set_global_stock(
    payload: GlobalStockUpdate,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    admin_only(user)

    await update_global_stock(
        db=db,
        product_id=payload.product_id,
        total_stock=payload.total_stock,
    )
    return {"status": "updated"}


@router.get("/products/stock")
async def product_stock_overview(
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    """
    Admin stock overview per product.
    """
    admin_only(user)

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


# =====================================================
# SALES KPIs
# =====================================================

@router.get("/summary")
async def kpi_summary(
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    admin_only(user)

    res = await db.execute(
        select(func.count(Order.id), func.sum(Order.total))
    )
    orders, revenue = res.first()

    return {
        "total_orders": orders or 0,
        "total_revenue": float(revenue or 0),
    }
