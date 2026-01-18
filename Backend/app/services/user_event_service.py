# app/services/user_event_service.py

from uuid import UUID, uuid4
from typing import Union

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from app.models.models import UserEvent, UserPreference, User
from app.models.enums import user_event_type_enum
from app.services.user_preference_llm_service import generate_preferences_from_events
from app.services.embedding_service import generate_text_embedding, store_embedding
from app.services.user_embedding_service import rebuild_user_embedding

# =====================================================
# EVENT TRACKING (CANONICAL)
# =====================================================

async def record_event(
    *,
    db: AsyncSession,
    user_id: UUID,
    event_type: Union[user_event_type_enum, str],
    product_id: UUID | None = None,
    variant_id: UUID | None = None,
    order_id: UUID | None = None,
    metadata: dict | None = None,
):
    # normalize enum → string
    event_type_value = (
        event_type.value
        if isinstance(event_type, user_event_type_enum)
        else str(event_type)
    )

    event = UserEvent(
        id=uuid4(),
        user_id=user_id,
        event_type=event_type_value,
        product_id=product_id,
        variant_id=variant_id,
        order_id=order_id,
        event_metadata=metadata or {},
    )

    db.add(event)
    await db.commit()

    # async-safe recompute
    await recompute_user_preferences(db, user_id)


# =====================================================
# PREFERENCE RECOMPUTE (SOURCE OF TRUTH)
# =====================================================

async def recompute_user_preferences(db: AsyncSession, user_id: UUID):
    res = await db.execute(
        select(UserEvent)
        .where(UserEvent.user_id == user_id)
        .order_by(desc(UserEvent.created_at))
        .limit(100)
    )

    events = [
        {
            "event_type": e.event_type,
            "product_id": str(e.product_id) if e.product_id else None,
            "variant_id": str(e.variant_id) if e.variant_id else None,
            "metadata": e.metadata,
        }
        for e in res.scalars()
    ]

    if not events:
        return

    inferred = await generate_preferences_from_events(events)
    if not isinstance(inferred, dict):
        return

    # ---------------- preference table ----------------
    pref = await db.get(UserPreference, user_id)
    if not pref:
        pref = UserPreference(user_id=user_id)
        db.add(pref)

    pref.preferred_categories = inferred.get("preferred_categories", [])
    pref.preferred_price_range = inferred.get("preferred_price_range", {})
    pref.preferred_brands = inferred.get("preferred_brands", [])

    # ---------------- user summary (IMPORTANT) ----------------
    user = await db.get(User, user_id)
    if user:
        user.preferences = inferred

    await db.commit()

    # ---------------- embedding (single write) ----------------
    emb = await generate_text_embedding(str(inferred))
    await store_embedding(
        db=db,
        source_type="user_pref",
        source_id=user_id,
        embedding=emb,
    )
    await rebuild_user_embedding(db, user_id)



# =====================================================
# USER CONTEXT (UI / AGENT)
# =====================================================

async def get_user_context(db: AsyncSession, user_id: UUID):
    pref = await db.get(UserPreference, user_id)

    return {
        "preferences": {
            "categories": pref.preferred_categories if pref else [],
            "price_range": pref.preferred_price_range if pref else {},
            "brands": pref.preferred_brands if pref else [],
        }
    }
