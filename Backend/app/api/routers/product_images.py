# app/api/routers/product_images.py
from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.core.database import get_db
from app.core.auth import get_current_user
from app.services.product_image_service import (
    upload_product_image,
    delete_product_image,
)
from app.utils.api_error import forbidden

router = APIRouter(
    prefix="/admin/products/images",
    tags=["Admin Products"],
)


@router.post("/")
async def upload_image(
    product_id: UUID,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    if user["role"] != "admin":
        forbidden()

    img = await upload_product_image(
        db=db,
        product_id=product_id,
        file=file,
    )

    return {
        "id": img.id,
        "url": img.image_url,
    }


@router.delete("/{image_id}")
async def remove_image(
    image_id: UUID,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    if user["role"] != "admin":
        forbidden()

    await delete_product_image(db, image_id=image_id)
    return {"status": "deleted"}
