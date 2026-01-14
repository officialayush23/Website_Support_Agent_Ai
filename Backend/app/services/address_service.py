# app/services/address_service.py
# app/services/address_service.py

from uuid import uuid4, UUID
from sqlalchemy import select, update, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import Address
from app.utils.api_error import not_found


async def list_addresses(db: AsyncSession, user_id: UUID):
    res = await db.execute(
        select(Address)
        .where(Address.user_id == user_id)
        .order_by(desc(Address.is_default), desc(Address.created_at))
    )
    return res.scalars().all()


async def create_address(
    db: AsyncSession,
    user_id: UUID,
    data: dict,
):
    is_default = data.get("is_default", False)

    # If this address is marked default, unset others first
    if is_default:
        await db.execute(
            update(Address)
            .where(Address.user_id == user_id)
            .values(is_default=False)
        )

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

    was_default = addr.is_default

    await db.delete(addr)
    await db.commit()

    # If default address was deleted, promote latest address (if any)
    if was_default:
        res = await db.execute(
            select(Address)
            .where(Address.user_id == user_id)
            .order_by(desc(Address.created_at))
            .limit(1)
        )
        new_default = res.scalar_one_or_none()
        if new_default:
            new_default.is_default = True
            await db.commit()


async def set_default(
    db: AsyncSession,
    user_id: UUID,
    address_id: UUID,
):
    addr = await db.get(Address, address_id)
    if not addr or addr.user_id != user_id:
        not_found("Address")

    # Unset all defaults
    await db.execute(
        update(Address)
        .where(Address.user_id == user_id)
        .values(is_default=False)
    )

    addr.is_default = True
    await db.commit()
    await db.refresh(addr)
    return addr
