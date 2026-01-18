# app/api/routers/attributes.py
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.core.database import get_db
from app.core.auth import get_current_user
from app.services.attribute_service import (
    list_attributes,
    create_attribute,
    update_attribute,
    deactivate_attribute,
)
from app.schema.schemas import (
    AttributeDefinitionCreate,
    AttributeDefinitionUpdate,
    AttributeDefinitionOut,
)
from app.utils.api_error import forbidden

router = APIRouter(
    prefix="/admin/attributes",
    tags=["Admin Attributes"],
)


def admin_only(user):
    if user["role"] != "admin":
        forbidden()


@router.get("/", response_model=list[AttributeDefinitionOut])
async def all_attributes(
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    admin_only(user)
    return await list_attributes(db)


@router.post("/", response_model=AttributeDefinitionOut)
async def create(
    payload: AttributeDefinitionCreate,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    admin_only(user)
    return await create_attribute(
        db=db,
        data=payload.model_dump(),
    )


@router.patch("/{attribute_id}", response_model=AttributeDefinitionOut)
async def update(
    attribute_id: UUID,
    payload: AttributeDefinitionUpdate,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    admin_only(user)
    return await update_attribute(
        db=db,
        attribute_id=attribute_id,
        data=payload.model_dump(exclude_unset=True),
    )


@router.delete("/{attribute_id}")
async def deactivate(
    attribute_id: UUID,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    admin_only(user)
    return await deactivate_attribute(
        db=db,
        attribute_id=attribute_id,
    )
