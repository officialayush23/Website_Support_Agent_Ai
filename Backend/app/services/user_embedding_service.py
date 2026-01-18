# app/services/user_embedding_service.py
# app/services/user_embedding_service.py

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, delete
from uuid import UUID

from app.models.models import ChatContext, UserEvent, Embedding, Product,ChatSession
from app.services.embedding_service import generate_text_embedding, store_embedding


async def rebuild_user_embedding(
    db: AsyncSession,
    user_id: UUID,
):
    """
    Builds ONE canonical user embedding.
    Source of truth for personalization.
    """

    # 1. Last chat summaries
    res_ctx = await db.execute(
        select(ChatContext.summary)
        .join(ChatSession, ChatSession.id == ChatContext.chat_session_id)
        .where(ChatSession.user_id == user_id)
        .order_by(desc(ChatContext.created_at))
        .limit(5)
    )
    summaries = [r[0] for r in res_ctx.fetchall()]

    # 2. Recent user events
    res_evt = await db.execute(
        select(UserEvent.event_type, UserEvent.metadata)
        .where(UserEvent.user_id == user_id)
        .order_by(desc(UserEvent.created_at))
        .limit(20)
    )
    events = [f"{e.event_type}:{e.metadata}" for e in res_evt.scalars()]

    # 3. Combine into one semantic document
    combined_text = "\n".join(
        ["CHAT_SUMMARIES:"] + summaries +
        ["USER_EVENTS:"] + events
    )

    if not combined_text.strip():
        return

    # 4. Generate embedding
    embedding = await generate_text_embedding(combined_text)

    # 5. Enforce SINGLE user embedding
    await db.execute(
        delete(Embedding)
        .where(
            Embedding.source_type == "user",
            Embedding.source_id == user_id,
        )
    )

    await store_embedding(
        db=db,
        source_type="user",
        source_id=user_id,
        embedding=embedding,
        metadata={"kind": "canonical_user_vector"},
    )
