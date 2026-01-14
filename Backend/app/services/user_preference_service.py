# app/services/user_preference_service.py
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.models import UserPreference
from uuid import UUID
from sqlalchemy import select, func, desc



from app.models.models import (
    UserEvent,
    Product,
    UserPreference,
)


async def get_preferences(db: AsyncSession, user_id: UUID):
    return await db.get(UserPreference, user_id)



async def recompute_user_preferences(
    db: AsyncSession,
    user_id: UUID,
):
    # ---------- CATEGORY PREFERENCE ----------
    cat_res = await db.execute(
        select(
            Product.category,
            func.count(UserEvent.id).label("cnt"),
        )
        .join(Product, Product.id == UserEvent.product_id)
        .where(
            UserEvent.user_id == user_id,
            Product.category.isnot(None),
        )
        .group_by(Product.category)
        .order_by(desc("cnt"))
        .limit(5)
    )

    categories = [r.category for r in cat_res.all()]

    # ---------- PRICE RANGE ----------
    price_res = await db.execute(
        select(
            func.min(Product.price),
            func.max(Product.price),
        )
        .join(Product, Product.id == UserEvent.product_id)
        .where(UserEvent.user_id == user_id)
    )

    min_price, max_price = price_res.one()

    price_range = {}
    if min_price is not None and max_price is not None:
        price_range = {
            "min": float(min_price),
            "max": float(max_price),
        }

    # ---------- LAST SEEN PRODUCTS ----------
    seen_res = await db.execute(
        select(UserEvent.product_id)
        .where(
            UserEvent.user_id == user_id,
            UserEvent.product_id.isnot(None),
        )
        .order_by(UserEvent.created_at.desc())
        .limit(20)
    )

    last_seen = [r.product_id for r in seen_res.all()]

    pref = await db.get(UserPreference, user_id)
    if not pref:
        pref = UserPreference(user_id=user_id)
        db.add(pref)

    pref.preferred_categories = categories
    pref.preferred_price_range = price_range
    pref.last_seen_products = last_seen

    await db.commit()
    return pref
