# app/services/product_embedding_service.py

from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import Product, ProductVariant, ProductImage
from app.services.embedding_service import (
    generate_text_embedding,
    generate_image_embedding,
    store_embedding,
)
from app.utils.api_error import not_found


# =========================
# PRODUCT TEXT
# =========================

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
            ],
        )
    )

    embedding = await generate_text_embedding(text)

    await store_embedding(
        db=db,
        source_type="product",
        source_id=product_id,
        embedding=embedding,
        metadata={"kind": "product_text"},
    )


# =========================
# VARIANT ATTRIBUTES
# =========================

async def embed_variant(
    db: AsyncSession,
    variant_id: UUID,
):
    variant = await db.get(ProductVariant, variant_id)
    if not variant:
        not_found("Variant")

    text = f"variant attributes: {variant.attributes or {}}"

    embedding = await generate_text_embedding(text)

    await store_embedding(
        db=db,
        source_type="variant",
        source_id=variant_id,
        embedding=embedding,
        metadata={"kind": "variant_attributes"},
    )


# =========================
# IMAGE (TEXTUAL PROXY)
# =========================

async def embed_product_image(
    db: AsyncSession,
    image_id: UUID,
):
    image = await db.get(ProductImage, image_id)
    if not image:
        not_found("Product image")

    embedding = await generate_image_embedding(image.image_url)

    await store_embedding(
        db=db,
        source_type="image",
        source_id=image_id,
        embedding=embedding,
        metadata={
            "product_id": str(image.product_id),
            "variant_id": str(image.variant_id),
            "is_primary": image.is_primary,
        },
    )
