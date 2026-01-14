# app/services/offer_service.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import uuid4, UUID
from datetime import datetime, timezone

from app.models.models import Offer
from app.utils.api_error import not_found, bad_request


def utcnow() -> datetime:
    return datetime.utcnow()


def to_utc_naive(dt: datetime) -> datetime:
    if dt.tzinfo:
        return dt.astimezone(timezone.utc).replace(tzinfo=None)
    return dt


# =========================
# PUBLIC
# =========================

async def list_active_offers(db: AsyncSession):
    now = utcnow()

    res = await db.execute(
        select(Offer)
        .where(
            Offer.is_active == True,
            Offer.starts_at <= now,
            Offer.ends_at >= now,
        )
        .order_by(Offer.priority.desc())
    )
    return res.scalars().all()


# =========================
# ADMIN
# =========================

async def list_all_offers(db: AsyncSession):
    res = await db.execute(
        select(Offer).order_by(Offer.created_at.desc())
    )
    return res.scalars().all()


async def create_offer(
    db: AsyncSession,
    data: dict,
    created_by: UUID,
):
    starts_at = to_utc_naive(data["starts_at"])
    ends_at = to_utc_naive(data["ends_at"])

    if starts_at >= ends_at:
        bad_request("starts_at must be before ends_at")

    offer = Offer(
        id=uuid4(),
        created_by=created_by,
        starts_at=starts_at,
        ends_at=ends_at,
        **{k: v for k, v in data.items() if k not in ("starts_at", "ends_at")},
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

    new_starts = to_utc_naive(data.get("starts_at", offer.starts_at))
    new_ends = to_utc_naive(data.get("ends_at", offer.ends_at))

    if new_starts >= new_ends:
        bad_request("starts_at must be before ends_at")

    for k, v in data.items():
        setattr(offer, k, v)

    offer.updated_at = utcnow()
    await db.commit()
    await db.refresh(offer)
    return offer


async def deactivate_offer(
    db: AsyncSession,
    offer_id: UUID,
):
    offer = await db.get(Offer, offer_id)
    if not offer:
        not_found("Offer")

    offer.is_active = False
    offer.updated_at = utcnow()

    await db.commit()
