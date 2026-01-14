# app/services/user_service.py
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.models.models import User
from app.utils.api_error import not_found


# Fields user is allowed to update themselves
USER_SELF_UPDATE_FIELDS = {"name"}


async def get_me(db: AsyncSession, user_id: UUID):
    user = await db.get(User, user_id)
    if not user:
        not_found("User")
    return user


async def update_me(
    db: AsyncSession,
    user_id: UUID,
    data: dict,
):
    user = await db.get(User, user_id)
    if not user:
        not_found("User")

    for k, v in data.items():
        if k in USER_SELF_UPDATE_FIELDS:
            setattr(user, k, v)

    await db.commit()
    await db.refresh(user)
    return user

from app.models.models import User, UserPreference

async def get_preferences(db: AsyncSession, user_id):
    user = await db.get(User, user_id)
    pref = await db.get(UserPreference, user_id)

    return {
        "explicit": user.preferences or {},
        "inferred": {
            "categories": pref.preferred_categories if pref else [],
            "price_range": pref.preferred_price_range if pref else {},
            "last_seen_products": pref.last_seen_products if pref else [],
        },
        "updated_at": pref.updated_at if pref else None,
    }