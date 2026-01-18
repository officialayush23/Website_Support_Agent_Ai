from app.services.user_event_service import recompute_user_preferences
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID, uuid4
async def rebuild_user_profile(db: AsyncSession, user_id: UUID):
    try:
        await recompute_user_preferences(db, user_id)
    except Exception as e:
        # log only, never crash user flow
        print("Preference rebuild failed:", e)