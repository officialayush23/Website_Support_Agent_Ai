# app/services/offer_service.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import uuid4, UUID
from datetime import datetime

from app.models.models import Offer
from app.utils.api_error import not_found, bad_request


async def list_active_offers(db: AsyncSession):
    now = datetime.utcnow()

    res = await db.execute(
        select(Offer)
        .where(Offer.is_active == True)
        .where(Offer.starts_at <= now)
        .where(Offer.ends_at >= now)
        .order_by(Offer.priority.desc())
    )
    return res.scalars().all()


async def create_offer(
    db: AsyncSession,
    data: dict,
    created_by: UUID,
):
    if data["starts_at"] >= data["ends_at"]:
        bad_request("starts_at must be before ends_at")

    offer = Offer(
        id=uuid4(),
        created_by=created_by,
        **data,
    )
    db.add(offer)
    await db.commit()
    await db.refresh(offer)
    return offer


async def update_offer(
    db: AsyncSession,
    offer_id: UUID,
    data: dict,
):
    offer = await db.get(Offer, offer_id)
    if not offer:
        not_found("Offer")

    # validate date range even on partial update
    new_starts = data.get("starts_at", offer.starts_at)
    new_ends = data.get("ends_at", offer.ends_at)

    if new_starts >= new_ends:
        bad_request("starts_at must be before ends_at")

    for k, v in data.items():
        setattr(offer, k, v)

    offer.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(offer)
    return offer
