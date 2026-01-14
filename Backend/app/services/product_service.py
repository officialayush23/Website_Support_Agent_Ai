# app/services/product_service.py

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID, uuid4
from sqlalchemy.orm import selectinload

from app.models.models import GlobalInventory, Product
from app.models.enums import user_event_type_enum
from app.services.user_event_service import record_event
from app.utils.api_error import not_found


# =========================
# LIST PRODUCTS
# =========================
async def list_products(
    db: AsyncSession,
    user_id: UUID | None = None,
    meta: dict | None = None,
):
    res = await db.execute(
        select(Product)
        .options(selectinload(Product.images))
        .where(Product.is_active.is_(True))
    )
    products = res.scalars().all()

    if user_id:
        await record_event(
            db=db,
            user_id=user_id,
            event_type=user_event_type_enum.search,
            metadata=meta or {},
        )

    return products


# =========================
# GET PRODUCT
# =========================
async def get_product(
    db: AsyncSession,
    product_id: UUID,
    user_id: UUID | None = None,
):
    res = await db.execute(
        select(Product)
        .options(selectinload(Product.images))
        .where(Product.id == product_id)
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


# =========================
# CREATE PRODUCT
# =========================
async def create_product(db: AsyncSession, data: dict):
    product = Product(**data)
    db.add(product)
    await db.flush()  # ✅ ensures product.id exists

    gi = GlobalInventory(
        product_id=product.id,
        total_stock=0,
        reserved_stock=0,
    )
    db.add(gi)

    await db.commit()
    await db.refresh(product)
    return product


# =========================
# UPDATE PRODUCT
# =========================
async def update_product(
    db: AsyncSession,
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
    return product


# =========================
# SOFT DELETE PRODUCT
# =========================
async def delete_product(
    db: AsyncSession,
    product_id: UUID,
):
    product = await db.get(Product, product_id)
    if not product:
        not_found("Product")

    product.is_active = False
    await db.commit()
    return {"status": "deleted"}
