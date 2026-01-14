# app/services/inventory_admin_service.py

from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from app.models.models import GlobalInventory
from app.utils.api_error import not_found

async def update_global_stock(
    db: AsyncSession,
    product_id: UUID,
    total_stock: int,
):
    gi = await db.get(GlobalInventory, product_id)
    if not gi:
        not_found("Global inventory")

    if total_stock < gi.reserved_stock:
        raise ValueError("total_stock < reserved_stock")

    gi.total_stock = total_stock
    await db.commit()
    return gi
