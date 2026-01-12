# app/api/routers/recommendations.py
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.auth import get_current_user
from app.services.recommendation_service import recommend_for_user
from app.schema.schemas import ProductOut

router = APIRouter(prefix="/recommendations", tags=["Recommendations"])


@router.get("/", response_model=list[ProductOut])
async def recommend(
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    return await recommend_for_user(db, user["user_id"])
