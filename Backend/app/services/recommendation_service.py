# app/services/recommendation_service.py

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models.models import Product, ProductVariant, UserPreference


async def recommend_for_user(
    db: AsyncSession,
    *,
    user_id,
    limit: int = 10,
):
    pref = await db.get(UserPreference, user_id)

    q = (
        select(Product)
        .where(Product.is_active.is_(True))
        .options(
            selectinload(Product.variants)
            .selectinload(ProductVariant.images)
        )
    )

    if pref:
        if pref.preferred_categories:
            q = q.where(Product.category.in_(pref.preferred_categories))

    q = q.order_by(Product.created_at.desc()).limit(limit)

    res = await db.execute(q)
    products = res.scalars().unique().all()

    if products:
        return products

    # fallback
    res = await db.execute(
        select(Product)
        .where(Product.is_active.is_(True))
        .order_by(Product.created_at.desc())
        .limit(limit)
    )
    return res.scalars().all()
