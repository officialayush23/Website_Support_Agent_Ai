# app/services/product_service.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID, uuid4

from app.models.models import Product, GlobalInventory
from app.services.user_event_service import record_event
from app.services.product_embedding_service import embed_product
from app.utils.api_error import not_found
from app.schema.enums import UserEventType


async def list_products(
    db: AsyncSession,
    *,
    user_id: UUID | None = None,
    meta: dict | None = None,
):
    res = await db.execute(
        select(Product).where(Product.is_active.is_(True))
    )
    products = res.scalars().all()

    if user_id:
        await record_event(
            db=db,
            user_id=user_id,
            event_type=UserEventType.search.value,
            metadata=meta or {},
        )

    return products


async def get_product(
    db: AsyncSession,
    *,
    product_id: UUID,
    user_id: UUID | None = None,
):
    product = await db.get(Product, product_id)
    if not product or not product.is_active:
        not_found("Product")

    if user_id:
        await record_event(
            db=db,
            user_id=user_id,
            event_type=UserEventType.view_product.value,
            product_id=product_id,
        )

    return product


async def create_product(
    db: AsyncSession,
    *,
    name: str,
    description: str | None = None,
    category: str | None = None,
    price: float,
    images: list[str] | None = None,
):
    product = Product(
        id=uuid4(),
        name=name,
        description=description,
        category=category,
        price=price,
        images=images or [],
        is_active=True,
    )

    db.add(product)
    await db.flush()

    db.add(
        GlobalInventory(
            product_id=product.id,
            total_stock=0,
            allocated_stock=0,
            reserved_stock=0,
        )
    )

    await db.commit()
    await db.refresh(product)

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
