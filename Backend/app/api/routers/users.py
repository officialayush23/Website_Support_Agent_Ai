# app/api/routers/users.py
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.core.database import get_db
from app.core.auth import get_current_user
from app.schema.schemas import UserOut, UserUpdate
from app.services.user_service import get_me, get_preferences, update_me

router = APIRouter(prefix="/users", tags=["Users"])


@router.patch("/location")
async def update_location(
    lat: float,
    lng: float,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    await db.execute(
        text("""
        UPDATE users
        SET location = ST_SetSRID(ST_MakePoint(:lng, :lat), 4326),
            location_updated_at = now()
        WHERE id = :uid
        """),
        {"lat": lat, "lng": lng, "uid": user["user_id"]},
    )
    await db.commit()
    return {"status": "updated"}


@router.get("/me", response_model=UserOut)
async def me(
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    return await get_me(db, user["user_id"])


@router.patch("/me", response_model=UserOut)
async def update_me_endpoint(
    payload: UserUpdate,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    return await update_me(
        db,
        user["user_id"],
        payload.model_dump(exclude_unset=True),
    )
# app/api/routers/users.py
@router.get("/me/preferences")
async def my_preferences(
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    return await get_preferences(db, user["user_id"])
