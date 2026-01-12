# app/api/routers/offers.py
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.core.database import get_db
from app.core.auth import get_current_user
from app.services.offer_service import (
    list_active_offers,
    create_offer,
    update_offer,
)
from app.schema.schemas import OfferCreate, OfferUpdate, OfferOut
from app.utils.api_error import forbidden

router = APIRouter(prefix="/offers", tags=["Offers"])


@router.get("/", response_model=list[OfferOut])
async def active(db: AsyncSession = Depends(get_db)):
    return await list_active_offers(db)


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
