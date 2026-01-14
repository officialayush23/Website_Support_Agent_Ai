# app/services/recommendation_service.py

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.models import Product, UserPreference

async def recommend_for_user(
    db: AsyncSession,
    user_id,
    limit: int = 10,
):
    pref = await db.get(UserPreference, user_id)

    q = select(Product).where(Product.is_active == True)

    if pref:
        if pref.preferred_categories:
            q = q.where(Product.category.in_(pref.preferred_categories))

        pr = pref.preferred_price_range or {}
        if pr.get("min") is not None and pr.get("max") is not None:
            q = q.where(
                Product.price.between(pr["min"], pr["max"])
            )

    q = q.order_by(Product.created_at.desc()).limit(limit)
    res = await db.execute(q)
    products = res.scalars().all()

    # fallback
    if not products:
        res = await db.execute(
            select(Product)
            .where(Product.is_active == True)
            .order_by(Product.created_at.desc())
            .limit(limit)
        )
        return res.scalars().all()

    return products