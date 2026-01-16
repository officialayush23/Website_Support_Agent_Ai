# app/api/routers/offers.py
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.core.database import get_db
from app.core.auth import get_current_user
from app.services.offer_service import (
    list_active_offers,
    list_all_offers,
    create_offer,
    update_offer,
    deactivate_offer,
    preview_offers,
)
from app.schema.schemas import OfferCreate, OfferUpdate, OfferOut
from app.utils.api_error import forbidden

router = APIRouter(prefix="/offers", tags=["Offers"])


# =====================================================
# PUBLIC
# =====================================================

@router.get("/", response_model=list[OfferOut])
async def active(db: AsyncSession = Depends(get_db)):
    return await list_active_offers(db)


@router.get("/preview")
async def preview(
    subtotal: float,
    db: AsyncSession = Depends(get_db),
):
    """
    Used by:
    - Cart page
    - Checkout screen
    - Chat assistant ("You save ₹X using OFFER_Y")
    """
    return await preview_offers(db=db, subtotal=subtotal)


# =====================================================
# ADMIN
# =====================================================

@router.get("/admin", response_model=list[OfferOut])
async def admin_list(
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    if user["role"] != "admin":
        forbidden()

    return await list_all_offers(db)


@router.post("/admin", response_model=OfferOut)
async def create(
    payload: OfferCreate,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    if user["role"] != "admin":
        forbidden()

    return await create_offer(
        db=db,
        data=payload.model_dump(),
        created_by=user["user_id"],
    )


@router.patch("/admin/{offer_id}", response_model=OfferOut)
async def update(
    offer_id: UUID,
    payload: OfferUpdate,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    if user["role"] != "admin":
        forbidden()

    return await update_offer(
        db=db,
        offer_id=offer_id,
        data=payload.model_dump(exclude_unset=True),
    )


@router.delete("/admin/{offer_id}")
async def deactivate(
    offer_id: UUID,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    if user["role"] != "admin":
        forbidden()

    await deactivate_offer(db, offer_id)
    return {"status": "deactivated"}
