# app/services/recommendation_service.py

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
from sqlalchemy.orm import selectinload
from uuid import UUID

from app.models.models import Product, ProductVariant, Embedding


async def recommend_for_user(
    db: AsyncSession,
    *,
    user_id: UUID,
    limit: int = 10,
):
    # 1. Fetch user embedding
    res_user = await db.execute(
        select(Embedding)
        .where(
            Embedding.source_type == "user",
            Embedding.source_id == user_id,
        )
        .order_by(Embedding.created_at.desc())
        .limit(1)
    )
    user_emb = res_user.scalar_one_or_none()

    # 2. If no user embedding → fallback
    if not user_emb:
        res = await db.execute(
            select(Product)
            .where(Product.is_active.is_(True))
            .order_by(Product.created_at.desc())
            .limit(limit)
        )
        return res.scalars().unique().all()

    # 3. Semantic ranking using cosine similarity
    stmt = text("""
        SELECT p.*
        FROM products p
        JOIN embeddings e
          ON e.source_id = p.id
         AND e.source_type = 'product'
        ORDER BY e.embedding <=> :user_embedding
        LIMIT :limit
    """)

    res = await db.execute(
        stmt,
        {
            "user_embedding": user_emb.embedding,
            "limit": limit,
        },
    )

    product_ids = [row[0] for row in res.fetchall()]
    if not product_ids:
        return []

    # 4. Hydrate ORM objects
    res = await db.execute(
        select(Product)
        .where(Product.id.in_(product_ids))
        .options(
            selectinload(Product.variants)
            .selectinload(ProductVariant.images)
        )
    )

    return res.scalars().unique().all()
