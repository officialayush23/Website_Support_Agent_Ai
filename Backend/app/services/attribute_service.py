# app/services/attribute_service.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID, uuid4

from app.models.models import AttributeDefinition
from app.utils.api_error import not_found, bad_request


# =========================
# ADMIN: LIST
# =========================

async def list_attributes(db: AsyncSession):
    res = await db.execute(
        select(AttributeDefinition)
        .order_by(AttributeDefinition.created_at.desc())
    )
    return res.scalars().all()


# =========================
# ADMIN: CREATE
# =========================

async def create_attribute(
    db: AsyncSession,
    *,
    data: dict,
):
    # uniqueness
    exists = await db.execute(
        select(AttributeDefinition)
        .where(AttributeDefinition.name == data["name"])
    )
    if exists.scalar_one_or_none():
        bad_request("Attribute already exists")

    if data.get("value_type") == "enum" and not data.get("allowed_values"):
        bad_request("Enum attribute must have allowed_values")

    attr = AttributeDefinition(
        id=uuid4(),
        **data,
    )

    db.add(attr)
    await db.commit()
    await db.refresh(attr)
    return attr


# =========================
# ADMIN: UPDATE
# =========================

async def update_attribute(
    db: AsyncSession,
    *,
    attribute_id: UUID,
    data: dict,
):
    attr = await db.get(AttributeDefinition, attribute_id)
    if not attr:
        not_found("Attribute")

    if (
        "value_type" in data
        and data["value_type"] == "enum"
        and not data.get("allowed_values", attr.allowed_values)
    ):
        bad_request("Enum attribute must have allowed_values")

    for k, v in data.items():
        setattr(attr, k, v)

    await db.commit()
    await db.refresh(attr)
    return attr


# =========================
# ADMIN: DELETE (SOFT)
# =========================

async def deactivate_attribute(
    db: AsyncSession,
    *,
    attribute_id: UUID,
):
    attr = await db.get(AttributeDefinition, attribute_id)
    if not attr:
        not_found("Attribute")

    attr.is_active = False
    await db.commit()
    return {"status": "deactivated"}
