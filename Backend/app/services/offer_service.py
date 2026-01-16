# app/services/offer_service.py

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID, uuid4
from datetime import datetime, timezone

from app.models.models import Offer
from app.utils.api_error import not_found, bad_request


# =====================================================
# TIME HELPERS
# =====================================================

def utcnow() -> datetime:
    return datetime.utcnow()


def to_utc_naive(dt: datetime) -> datetime:
    if dt.tzinfo:
        return dt.astimezone(timezone.utc).replace(tzinfo=None)
    return dt


# =====================================================
# PUBLIC
# =====================================================

async def list_active_offers(db: AsyncSession):
    now = utcnow()

    res = await db.execute(
        select(Offer)
        .where(
            Offer.is_active.is_(True),
            Offer.starts_at <= now,
            Offer.ends_at >= now,
        )
        .order_by(
            Offer.priority.desc(),
            Offer.created_at.desc(),
        )
    )
    return res.scalars().all()


# =====================================================
# DISCOUNT ENGINE (SAFE + DETERMINISTIC)
# =====================================================

def evaluate_offer(
    offer: Offer,
    *,
    subtotal: float,
) -> float:
    """
    Returns discount amount (NOT final price)
    """

    if subtotal <= 0:
        return 0.0

    if offer.min_cart_value and subtotal < float(offer.min_cart_value):
        return 0.0

    discount = 0.0

    if offer.percentage_off:
        discount = subtotal * (float(offer.percentage_off) / 100)

    elif offer.amount_off:
        discount = float(offer.amount_off)

    if offer.max_discount:
        discount = min(discount, float(offer.max_discount))

    return round(min(discount, subtotal), 2)


def apply_offers(
    *,
    offers: list[Offer],
    subtotal: float,
) -> dict:
    """
    Applies offers in priority order.
    Respects stackable flag.
    """

    applied = []
    discount_total = 0.0

    for offer in offers:
        discount = evaluate_offer(offer, subtotal=subtotal)

        if discount <= 0:
            continue

        applied.append(
            {
                "offer_id": offer.id,
                "title": offer.title,
                "discount": discount,
            }
        )

        discount_total += discount

        if not offer.stackable:
            break  # 🚫 HARD STOP

    discount_total = round(min(discount_total, subtotal), 2)

    return {
        "discount_total": discount_total,
        "applied_offers": applied,
    }


# =====================================================
# PREVIEW (CART / CHAT / CHECKOUT)
# =====================================================

async def preview_offers(
    db: AsyncSession,
    *,
    subtotal: float,
):
    offers = await list_active_offers(db)
    return apply_offers(offers=offers, subtotal=subtotal)


# =====================================================
# ADMIN
# =====================================================

async def list_all_offers(db: AsyncSession):
    res = await db.execute(
        select(Offer)
        .order_by(Offer.created_at.desc())
    )
    return res.scalars().all()


async def create_offer(
    db: AsyncSession,
    *,
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
    *,
    offer_id: UUID,
    data: dict,
):
    offer = await db.get(Offer, offer_id)
    if not offer:
        not_found("Offer")

    if "starts_at" in data:
        offer.starts_at = to_utc_naive(data["starts_at"])
    if "ends_at" in data:
        offer.ends_at = to_utc_naive(data["ends_at"])

    for k, v in data.items():
        if k not in ("starts_at", "ends_at"):
            setattr(offer, k, v)

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
    await db.commit()
