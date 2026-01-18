# app/services/catalog_service.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.models.models import (
    Product,
    ProductVariant,
    GlobalInventory,
    StoreInventory,
)


async def product_quantity_overview(db: AsyncSession):
    res = await db.execute(
        select(
            Product.id,
            Product.name,
            func.sum(GlobalInventory.total_stock).label("total_stock"),
        )
        .join(ProductVariant, ProductVariant.product_id == Product.id)
        .join(GlobalInventory, GlobalInventory.variant_id == ProductVariant.id)
        .group_by(Product.id)
    )

    return [
        {
            "product_id": r.id,
            "name": r.name,
            "total_stock": r.total_stock or 0,
        }
        for r in res
    ]

async def product_variant_breakdown(db: AsyncSession, product_id):
    res = await db.execute(
        select(
            ProductVariant.id,
            ProductVariant.sku,
            ProductVariant.price,
            GlobalInventory.total_stock,
            GlobalInventory.allocated_stock,
            GlobalInventory.reserved_stock,
        )
        .join(GlobalInventory, GlobalInventory.variant_id == ProductVariant.id)
        .where(ProductVariant.product_id == product_id)
    )

    return [
        {
            "variant_id": r.id,
            "sku": r.sku,
            "price": float(r.price),
            "total_stock": r.total_stock,
            "available_stock": r.total_stock - r.allocated_stock - r.reserved_stock,
        }
        for r in res
    ]
