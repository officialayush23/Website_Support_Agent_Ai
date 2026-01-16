# app/services/product_service.py

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from uuid import UUID, uuid4

from app.models.models import (
    Product,
    ProductVariant,
    GlobalInventory,
)
from app.models.enums import user_event_type_enum
from app.services.user_event_service import record_event
from app.services.product_embedding_service import embed_product, embed_variant
from app.utils.api_error import not_found, bad_request


# =====================================================
# PUBLIC: LIST PRODUCTS
# =====================================================

async def list_products(
    db: AsyncSession,
    *,
    user_id: UUID | None = None,
    meta: dict | None = None,
):
    res = await db.execute(
        select(Product)
        .where(Product.is_active.is_(True))
        .options(
            selectinload(Product.variants)
        )
    )
    products = res.scalars().unique().all()

    if user_id:
        await record_event(
            db=db,
            user_id=user_id,
            event_type=user_event_type_enum.search,
            metadata=meta or {},
        )

    return products


# =====================================================
# PUBLIC: GET PRODUCT
# =====================================================

async def get_product(
    db: AsyncSession,
    *,
    product_id: UUID,
    user_id: UUID | None = None,
):
    res = await db.execute(
        select(Product)
        .where(Product.id == product_id)
        .options(
            selectinload(Product.variants)
        )
    )
    product = res.scalar_one_or_none()

    if not product or not product.is_active:
        not_found("Product")

    if user_id:
        await record_event(
            db=db,
            user_id=user_id,
            event_type=user_event_type_enum.view_product,
            product_id=product_id,
        )

    return product


# =====================================================
# ADMIN: CREATE PRODUCT
# =====================================================

async def create_product(
    db: AsyncSession,
    *,
    name: str,
    description: str | None = None,
    category: str | None = None,
):
    product = Product(
        id=uuid4(),
        name=name,
        description=description,
        category=category,
        is_active=True,
    )

    db.add(product)
    await db.commit()
    await db.refresh(product)

    await embed_product(db, product.id)
    return product


# =====================================================
# ADMIN: UPDATE PRODUCT
# =====================================================

async def update_product(
    db: AsyncSession,
    *,
    product_id: UUID,
    data: dict,
):
    product = await db.get(Product, product_id)
    if not product:
        not_found("Product")

    for k, v in data.items():
        setattr(product, k, v)

    await db.commit()
    await db.refresh(product)

    if {"name", "description", "category"} & data.keys():
        await embed_product(db, product.id)

    return product


# =====================================================
# ADMIN: SOFT DELETE PRODUCT
# =====================================================

async def delete_product(
    db: AsyncSession,
    *,
    product_id: UUID,
):
    product = await db.get(Product, product_id)
    if not product:
        not_found("Product")

    product.is_active = False
    await db.commit()
    return {"status": "deleted"}


# =====================================================
# ADMIN: CREATE VARIANT (WITH INVENTORY INIT)
# =====================================================

async def create_variant(
    db: AsyncSession,
    *,
    product_id: UUID,
    sku: str,
    price: float,
    attributes: dict | None = None,
):
    product = await db.get(Product, product_id)
    if not product or not product.is_active:
        not_found("Product")

    existing = await db.execute(
        select(ProductVariant).where(ProductVariant.sku == sku)
    )
    if existing.scalar_one_or_none():
        bad_request("SKU already exists")

    variant = ProductVariant(
        id=uuid4(),
        product_id=product_id,
        sku=sku,
        price=price,
        attributes=attributes or {},
    )

    db.add(variant)
    await db.flush()

    # 🔥 GLOBAL INVENTORY AUTO INIT
    gi = GlobalInventory(
        variant_id=variant.id,
        total_stock=0,
        allocated_stock=0,
        reserved_stock=0,
    )
    db.add(gi)

    await db.commit()
    await db.refresh(variant)

    await embed_variant(db, variant.id)
    return variant
