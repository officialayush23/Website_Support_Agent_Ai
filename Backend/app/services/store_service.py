# app/services/store_service.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import uuid4, UUID

from app.models.models import Store, Inventory, Product
from app.utils.api_error import not_found, bad_request


async def list_stores(db: AsyncSession):
    res = await db.execute(
        select(Store).where(Store.is_active.is_(True))
    )
    return res.scalars().all()


async def create_store(db: AsyncSession, data: dict):
    store = Store(id=uuid4(), **data)
    db.add(store)
    await db.commit()
    await db.refresh(store)
    return store


async def update_stock(
    db: AsyncSession,
    store_id: UUID,
    product_id: UUID,
    stock: int,
):
    if stock < 0:
        bad_request("Stock cannot be negative")

    product = await db.get(Product, product_id)
    if not product:
        not_found("Product")

    inv = await db.get(
        Inventory,
        {"store_id": store_id, "product_id": product_id},
    )

    if not inv:
        inv = Inventory(
            store_id=store_id,
            product_id=product_id,
            stock=stock,
        )
        db.add(inv)
    else:
        inv.stock = stock

    await db.commit()
    await db.refresh(inv)
    return inv
