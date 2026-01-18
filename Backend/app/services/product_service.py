# app/services/product_service.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from uuid import UUID, uuid4

from app.models.models import (
    Product,
    ProductVariant,
    GlobalInventory,
    AttributeDefinition,
)
from app.models.enums import user_event_type_enum
from app.services.user_event_service import record_event
from app.services.product_embedding_service import embed_product, embed_variant
from app.utils.api_error import not_found, bad_request


# =====================================================
# INTERNAL: ATTRIBUTE VALIDATION
# =====================================================

async def validate_attributes(db: AsyncSession, attributes: dict):
    res = await db.execute(select(AttributeDefinition))
    defs = {d.name: d for d in res.scalars().all()}

    # unknown attributes
    for key in attributes.keys():
        if key not in defs:
            bad_request(f"Unknown attribute: {key}")

    for name, d in defs.items():
        if d.is_required and name not in attributes:
            bad_request(f"Missing required attribute: {name}")

        if name in attributes and d.allowed_values:
            if attributes[name] not in d.allowed_values:
                bad_request(
                    f"Invalid value for {name}. "
                    f"Allowed: {d.allowed_values}"
                )


# =====================================================
# PUBLIC
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
        .options(selectinload(Product.variants))
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


async def get_product(
    db: AsyncSession,
    *,
    product_id: UUID,
    user_id: UUID | None = None,
):
    res = await db.execute(
        select(Product)
        .where(Product.id == product_id, Product.is_active.is_(True))
        .options(selectinload(Product.variants))
    )
    product = res.scalar_one_or_none()
    if not product:
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
# ADMIN: PRODUCT
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

    # 🔥 embedding is mandatory
    await embed_product(db, product.id)

    return product


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
# ADMIN: VARIANTS
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

    exists = await db.execute(
        select(ProductVariant).where(ProductVariant.sku == sku)
    )
    if exists.scalar_one_or_none():
        bad_request("SKU already exists")

    attrs = attributes or {}
    await validate_attributes(db, attrs)

    variant = ProductVariant(
        id=uuid4(),
        product_id=product_id,
        sku=sku,
        price=price,
        attributes=attrs,
    )

    db.add(variant)
    await db.flush()

    # 🔥 global inventory always initialized
    db.add(
        GlobalInventory(
            variant_id=variant.id,
            total_stock=0,
            allocated_stock=0,
            reserved_stock=0,
        )
    )

    await db.commit()
    await db.refresh(variant)

    # 🔥 embedding is mandatory
    await embed_variant(db, variant.id)

    return variant


async def get_product_full(
    db: AsyncSession,
    *,
    product_id: UUID,
):
    res = await db.execute(
        select(Product)
        .where(Product.id == product_id, Product.is_active.is_(True))
        .options(
            selectinload(Product.variants)
            .selectinload(ProductVariant.images)
        )
    )
    product = res.scalar_one_or_none()
    if not product:
        not_found("Product")

    return {
        "id": product.id,
        "name": product.name,
        "description": product.description,
        "category": product.category,
        "variants": [
            {
                "id": v.id,
                "sku": v.sku,
                "price": float(v.price),
                "attributes": v.attributes,
                "images": [
                    {
                        "id": img.id,
                        "url": img.image_url,
                        "is_primary": img.is_primary,
                    }
                    for img in v.images
                ],
            }
            for v in product.variants
        ],
    }
