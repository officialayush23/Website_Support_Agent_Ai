# app/services/product_image_service.py
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import uuid4, UUID
from sqlalchemy import update
from fastapi import UploadFile

from app.models.models import ProductImage, Product
from app.utils.api_error import not_found, bad_request
from app.core.supabase import supabase

BUCKET = "product_image"  # keep if already created


async def upload_product_image(
    db: AsyncSession,
    product_id: UUID,
    file: UploadFile,
    is_primary: bool = False,
):
    if not file.content_type or not file.content_type.startswith("image/"):
        bad_request("Only image files allowed")

    product = await db.get(Product, product_id)
    if not product:
        not_found("Product")

    filename = f"{product_id}/{uuid4()}-{file.filename}"
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
            .where(ProductImage.product_id == product_id)
            .values(is_primary=False)
        )

    img = ProductImage(
        id=uuid4(),
        product_id=product_id,
        image_url=public_url,
        is_primary=is_primary,
    )

    db.add(img)
    await db.commit()
    await db.refresh(img)

    return img


async def delete_product_image(
    db: AsyncSession,
    image_id: UUID,
):
    img = await db.get(ProductImage, image_id)
    if not img:
        not_found("Product image")

    try:
        path = img.image_url.split("/storage/v1/object/public/")[1]
        supabase.storage.from_(BUCKET).remove([path])
    except Exception:
        pass  # storage cleanup failure should not block DB delete

    await db.delete(img)
    await db.commit()
