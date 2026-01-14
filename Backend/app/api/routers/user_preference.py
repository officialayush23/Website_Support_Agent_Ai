# app/api/routers/user_preference.py
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.auth import get_current_user
from app.services.user_preference_service import get_preferences

router = APIRouter(prefix="/users/preferences", tags=["User Preferences"])


@router.get("/")
async def my_preferences(
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    return await get_preferences(db, user["user_id"])
