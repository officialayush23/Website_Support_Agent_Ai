# app/services/user_service.py
from uuid import UUID, uuid4
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, desc, text

from app.models.models import User, Address, UserPreference
from app.utils.api_error import not_found


# =========================
# USER PROFILE
# =========================

USER_SELF_UPDATE_FIELDS = {"name"}


async def get_me(db: AsyncSession, user_id: UUID):
    user = await db.get(User, user_id)
    if not user:
        not_found("User")
    return user


async def update_me(db: AsyncSession, user_id: UUID, data: dict):
    user = await db.get(User, user_id)
    if not user:
        not_found("User")

    for k, v in data.items():
        if k in USER_SELF_UPDATE_FIELDS:
            setattr(user, k, v)

    await db.commit()
    await db.refresh(user)
    return user


async def update_location(db: AsyncSession, user_id: UUID, lat: float, lng: float):
    await db.execute(
        text("""
        UPDATE users
        SET location = ST_SetSRID(ST_MakePoint(:lng, :lat), 4326),
            location_updated_at = now()
        WHERE id = :uid
        """),
        {"lat": lat, "lng": lng, "uid": user_id},
    )
    await db.commit()


# =========================
# ADDRESSES
# =========================

async def list_addresses(db: AsyncSession, user_id: UUID):
    res = await db.execute(
        select(Address)
        .where(Address.user_id == user_id)
        .order_by(desc(Address.is_default), desc(Address.created_at))
    )
    return res.scalars().all()


async def create_address(db: AsyncSession, user_id: UUID, data: dict):
    if data.get("is_default"):
        await db.execute(
            update(Address)
            .where(Address.user_id == user_id)
            .values(is_default=False)
        )

    addr = Address(id=uuid4(), user_id=user_id, **data)
    db.add(addr)
    await db.commit()
    await db.refresh(addr)
    return addr


async def set_default_address(
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


async def delete_address(db: AsyncSession, user_id: UUID, address_id: UUID):
    addr = await db.get(Address, address_id)
    if not addr or addr.user_id != user_id:
        not_found("Address")

    await db.delete(addr)
    await db.commit()


# =========================
# PREFERENCES (READ ONLY)
# =========================

async def get_user_preferences(db: AsyncSession, user_id: UUID):
    user = await db.get(User, user_id)
    pref = await db.get(UserPreference, user_id)

    return {
        "explicit": user.preferences or {},
        "inferred": {
            "categories": pref.preferred_categories if pref else [],
            "price_range": pref.preferred_price_range if pref else {},
            "brands": pref.preferred_brands if pref else [],
        },
    }
