# app/services/product_embedding_service.py
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import Product
from app.services.embedding_service import (
    generate_text_embedding,
    store_embedding,
)
from app.utils.api_error import not_found


async def embed_product(
    db: AsyncSession,
    product_id: UUID,
):
    product = await db.get(Product, product_id)
    if not product:
        not_found("Product")

    text = " | ".join(
        filter(
            None,
            [
                product.name,
                product.description,
                product.category,
                f"price {product.price}",
                " ".join(product.images or []),
            ],
        )
    )

    embedding = await generate_text_embedding(text)

    await store_embedding(
        db=db,
        source_type="product",
        source_id=product_id,
        embedding=embedding,
        metadata={"kind": "product"},
    )
