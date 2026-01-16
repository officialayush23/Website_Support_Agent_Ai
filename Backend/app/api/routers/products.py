# app/api/routers/products.py

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.core.database import get_db
from app.core.auth import get_current_user
from app.services.product_service import (
    get_product_full,
    list_products,
    get_product,
    create_variant,
)
from app.schema.schemas import (
    ProductOut,
    ProductVariantCreate,
    ProductVariantOut,
)
from app.utils.api_error import forbidden

router = APIRouter(prefix="/products", tags=["Products"])


@router.get("/", response_model=list[ProductOut])
async def all_products(db: AsyncSession = Depends(get_db)):
    return await list_products(db)


@router.get("/{product_id}", response_model=ProductOut)
async def product_detail(
    product_id: UUID,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user, use_cache=False),
):
    user_id = user["user_id"] if user else None
    return await get_product(
        db=db,
        product_id=product_id,
        user_id=user_id,
    )


# ================= ADMIN =================

@router.post("/admin/variants", response_model=ProductVariantOut)
async def create_product_variant(
    payload: ProductVariantCreate,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    if user["role"] != "admin":
        forbidden()

    return await create_variant(
        db=db,
        product_id=payload.product_id,
        sku=payload.sku,
        price=payload.price,
        attributes=payload.attributes,
    )

@router.get("/{product_id}/full")
async def product_full(
    product_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    return await get_product_full(db=db, product_id=product_id)
