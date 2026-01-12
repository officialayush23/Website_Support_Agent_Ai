# app/api/routers/addresses.py
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.core.database import get_db
from app.core.auth import get_current_user
from app.schema.schemas import AddressCreate, AddressOut
from app.services.address_service import (
    list_addresses,
    create_address,
    delete_address,
    set_default,
)

router = APIRouter(prefix="/addresses", tags=["Addresses"])


@router.get("/", response_model=list[AddressOut])
async def list_user_addresses(
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    return await list_addresses(db, user["user_id"])


@router.post("/", response_model=AddressOut)
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


@router.delete("/{address_id}")
async def remove_address(
    address_id: UUID,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    await delete_address(
        db=db,
        user_id=user["user_id"],
        address_id=address_id,
    )
    return {"status": "deleted"}


@router.patch("/{address_id}/default")
async def make_default(
    address_id: UUID,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    await set_default(
        db=db,
        user_id=user["user_id"],
        address_id=address_id,
    )
    return {"status": "updated"}
