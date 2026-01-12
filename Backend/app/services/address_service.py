# app/services/address_service.py
from uuid import uuid4, UUID
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import Address
from app.utils.api_error import not_found, bad_request


async def list_addresses(db: AsyncSession, user_id: UUID):
    res = await db.execute(
        select(Address).where(Address.user_id == user_id)
    )
    return res.scalars().all()


async def create_address(
    db: AsyncSession,
    user_id: UUID,
    data: dict,
):
    addr = Address(
        id=uuid4(),
        user_id=user_id,
        **data,
    )
    db.add(addr)
    await db.commit()
    await db.refresh(addr)
    return addr


async def delete_address(
    db: AsyncSession,
    user_id: UUID,
    address_id: UUID,
):
    addr = await db.get(Address, address_id)
    if not addr or addr.user_id != user_id:
        not_found("Address")

    await db.delete(addr)
    await db.commit()


async def set_default(
    db: AsyncSession,
    user_id: UUID,
    address_id: UUID,
):
    addr = await db.get(Address, address_id)
    if not addr or addr.user_id != user_id:
        not_found("Address")

    await db.execute(
        update(Address)
        .where(Address.user_id == user_id)
        .values(is_default=False)
    )

    addr.is_default = True
    await db.commit()
