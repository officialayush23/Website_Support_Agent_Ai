# app/services/chat_context_service.py
from uuid import UUID, uuid4
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.models import ChatContext, Embedding
from app.services.embedding_service import generate_text_embedding as embed_text


async def summarize_chat_session(
    db: AsyncSession,
    *,
    chat_session_id: UUID,
    summary: str,
    token_count: int,
    confidence: float,
):
    ctx = ChatContext(
        id=uuid4(),
        chat_session_id=chat_session_id,
        summary=summary,
        token_count=token_count,
        confidence=confidence,
    )
    db.add(ctx)

    emb = Embedding(
        id=uuid4(),
        source_type="chat_summary",
        source_id=ctx.id,
        embedding=await embed_text(summary),
    )
    db.add(emb)

    await db.commit()
