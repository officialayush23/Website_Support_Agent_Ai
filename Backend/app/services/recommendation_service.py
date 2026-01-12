# app/services/recommendation_service.py
# app/services/recommendation_service.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.models.models import Product, UserEvent
from app.models.enums import user_event_type_enum


async def recommend_for_user(
    db: AsyncSession,
    user_id,
    limit: int = 10,
):
    """
    V1 recommendation:
    - based on user's past product interactions
    - only active products
    - popularity-weighted
    """

    res = await db.execute(
        select(Product)
        .join(UserEvent, UserEvent.product_id == Product.id)
        .where(
            UserEvent.user_id == user_id,
            Product.is_active == True,
        )
        .group_by(Product.id)
        .order_by(func.count(UserEvent.id).desc())
        .limit(limit)
    )

    products = res.scalars().all()

    # fallback for cold-start users
    if not products:
        fallback = await db.execute(
            select(Product)
            .where(Product.is_active == True)
            .order_by(Product.created_at.desc())
            .limit(limit)
        )
        return fallback.scalars().all()

    return products
