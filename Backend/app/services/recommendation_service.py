# app/services/recommendation_service.py
# app/services/recommendation_service.py

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
from uuid import UUID

from app.models.models import Product, Embedding


async def recommend_for_user(
    db: AsyncSession,
    *,
    user_id: UUID,
    limit: int = 10,
):
    # =================================================
    # 1. Fetch latest user embedding
    # =================================================
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

    # =================================================
    # 2. Fallback: no personalization yet
    # =================================================
    if not user_emb:
        res = await db.execute(
            select(Product)
            .where(Product.is_active.is_(True))
            .order_by(Product.created_at.desc())
            .limit(limit)
        )
        return res.scalars().all()

    # =================================================
    # 3. Semantic ranking (cosine distance via pgvector)
    # =================================================
    stmt = text("""
        SELECT p.id
        FROM products p
        JOIN embeddings e
          ON e.source_id = p.id
         AND e.source_type = 'product'
        WHERE p.is_active = true
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

    product_ids = [row.id for row in res.fetchall()]
    if not product_ids:
        return []

    # =================================================
    # 4. Preserve similarity order
    # =================================================
    order_map = {pid: idx for idx, pid in enumerate(product_ids)}

    # =================================================
    # 5. Hydrate products
    # =================================================
    res = await db.execute(
        select(Product)
        .where(Product.id.in_(product_ids))
    )
    products = res.scalars().all()

    # =================================================
    # 6. Restore semantic ranking
    # =================================================
    products.sort(key=lambda p: order_map[p.id])

    return products
