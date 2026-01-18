# app/services/product_image_service.py
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID, uuid4
from fastapi import UploadFile

from app.models.models import Product
from app.services.product_embedding_service import embed_product
from app.utils.api_error import not_found, bad_request
from app.core.supabase import supabase

BUCKET = "product_image"


async def upload_product_image(
    db: AsyncSession,
    *,
    product_id: UUID,
    file: UploadFile,
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

    product.images = (product.images or []) + [public_url]
    await db.commit()

    await embed_product(db, product.id)
    return {"image_url": public_url}


async def delete_product_image(
    db: AsyncSession,
    *,
    image_id: UUID,
):
    bad_request("Image deletion requires full product image index handling")
