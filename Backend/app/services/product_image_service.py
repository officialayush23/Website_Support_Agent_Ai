# app/services/product_image_service.py

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import update
from uuid import UUID, uuid4
from fastapi import UploadFile

from app.models.models import ProductVariant, ProductImage
from app.services.product_embedding_service import embed_product_image
from app.utils.api_error import not_found, bad_request
from app.core.supabase import supabase

BUCKET = "product_image"


async def upload_product_image(
    db: AsyncSession,
    *,
    variant_id: UUID,
    file: UploadFile,
    is_primary: bool = False,
):
    if not file.content_type or not file.content_type.startswith("image/"):
        bad_request("Only image files allowed")

    variant = await db.get(ProductVariant, variant_id)
    if not variant:
        not_found("Product variant")

    filename = f"{variant.product_id}/{variant_id}/{uuid4()}-{file.filename}"
    content = await file.read()

    supabase.storage.from_(BUCKET).upload(
        filename,
        content,
        {"content-type": file.content_type},
    )

    public_url = supabase.storage.from_(BUCKET).get_public_url(filename)

    if is_primary:
        await db.execute(
            update(ProductImage)
            .where(ProductImage.variant_id == variant_id)
            .values(is_primary=False)
        )

    img = ProductImage(
        id=uuid4(),
        product_id=variant.product_id,
        variant_id=variant_id,
        image_url=public_url,
        is_primary=is_primary,
    )

    db.add(img)
    await db.commit()
    await db.refresh(img)

    # 🔥 IMAGE EMBEDDING
    await embed_product_image(db, img.id)

    return img


async def delete_product_image(
    db: AsyncSession,
    *,
    image_id: UUID,
):
    img = await db.get(ProductImage, image_id)
    if not img:
        not_found("Product image")

    try:
        path = img.image_url.split("/storage/v1/object/public/")[1]
        supabase.storage.from_(BUCKET).remove([path])
    except Exception:
        pass

    await db.delete(img)
    await db.commit()
