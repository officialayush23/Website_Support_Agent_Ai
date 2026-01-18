# app/services/embedding_service.py

from uuid import uuid4, UUID
from typing import Optional, List

from sqlalchemy.ext.asyncio import AsyncSession

from google import genai
from google.genai import types
from app.models.models import Embedding
from app.core.config import settings
from app.utils.api_error import internal_error


# =====================================================
# GEMINI CLIENT (NEW SDK)
# =====================================================

client = genai.Client(api_key=settings.GEMINI_API_KEY)

EMBEDDING_MODEL = "gemini-embedding-001"
EMBEDDING_DIM = 768  # must match VECTOR(768)


# =====================================================
# GENERATORS
# =====================================================

async def generate_text_embedding(text: str) -> List[float]:
    """
    Generates a 768-dim embedding using Gemini.
    Canonical for:
    - products
    - variants
    - offers
    - user preferences
    - chat context
    """
    try:
        result = client.models.embed_content(
            model=EMBEDDING_MODEL,
            contents=text,
            config=types.EmbedContentConfig(output_dimensionality=768)
        )

        embedding = result.embeddings[0].values

        if len(embedding) != EMBEDDING_DIM:
            internal_error(
                f"Embedding dimension mismatch: {len(embedding)} != {EMBEDDING_DIM}"
            )

        return embedding

    except Exception as e:
        internal_error(f"Gemini text embedding failed: {e}")


async def generate_image_embedding(image_url: str) -> List[float]:
    """
    Gemini does not expose public image embeddings yet.
    Industry-standard workaround:
    - embed image URL + semantic hint text
    - replace later when true multimodal embeddings are released
    """
    pseudo_text = f"product image: {image_url}"
    return await generate_text_embedding(pseudo_text)


# =====================================================
# STORAGE
# =====================================================

async def store_embedding(
    *,
    db: AsyncSession,
    source_type: str,
    source_id: UUID,
    embedding: List[float],
    metadata: Optional[dict] = None,
):
    """
    Stores embedding in pgvector-backed table.
    This is the SINGLE source of truth for semantic search.
    """
    try:
        db.add(
            Embedding(
                id=uuid4(),
                source_type=source_type,
                source_id=source_id,
                embedding=embedding,
                metadata=metadata or {},
            )
        )
        await db.commit()

    except Exception as e:
        await db.rollback()
        internal_error(f"Failed to store embedding: {e}")
