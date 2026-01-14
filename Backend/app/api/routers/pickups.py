# app/api/routers/pickups.py
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.core.database import get_db
from app.core.auth import get_current_user
from app.services.pickup_service import (
    list_store_pickups,
    update_pickup_status,
)
from app.utils.api_error import forbidden

router = APIRouter(prefix="/store/pickups", tags=["Store Pickup"])


@router.get("/{store_id}")
async def list_pickups(
    store_id: UUID,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    if user["role"] not in ("admin", "store_manager"):
        forbidden()

    return await list_store_pickups(db, store_id)


@router.patch("/{pickup_id}")
async def update_status(
    pickup_id: UUID,
    status: str,  # ready | picked_up | cancelled
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    if user["role"] not in ("admin", "store_manager"):
        forbidden()

    await update_pickup_status(db, pickup_id, status)
    return {"status": "updated"}
