# app/api/routers/users.py
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.core.database import get_db
from app.core.auth import get_current_user
from app.schema.schemas import (
    UserOut, UserUpdate,
    AddressCreate, AddressOut,
)
from app.services.user_service import *
router = APIRouter(prefix="/users", tags=["Users"])


# ================= PROFILE =================

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


@router.patch("/location")
async def update_user_location(
    lat: float,
    lng: float,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    await update_location(db, user["user_id"], lat, lng)
    return {"status": "updated"}


# ================= ADDRESSES =================

@router.get("/addresses", response_model=list[AddressOut])
async def list_user_addresses(
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    return await list_addresses(db, user["user_id"])


@router.post("/addresses", response_model=AddressOut)
async def add_address(
    payload: AddressCreate,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    return await create_address(
        db=db,
        user_id=user["user_id"],
        data=payload.model_dump(),
    )


@router.delete("/addresses/{address_id}")
async def remove_address(
    address_id: UUID,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    await delete_address(db, user["user_id"], address_id)
    return {"status": "deleted"}


@router.patch("/addresses/{address_id}/default")
async def make_default_address(
    address_id: UUID,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    await set_default_address(db, user["user_id"], address_id)
    return {"status": "updated"}


# ================= PREFERENCES =================

@router.get("/preferences")
async def my_preferences(
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    return await get_user_preferences(db, user["user_id"])
