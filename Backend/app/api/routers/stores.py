# app/api/routers/stores.py
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.auth import get_current_user
from app.services.store_service import list_stores, create_store, update_stock
from app.schema.schemas import StoreCreate, StoreOut, InventoryUpdate, InventoryOut
from app.utils.api_error import forbidden

router = APIRouter(prefix="/stores", tags=["Stores"])


@router.get("/", response_model=list[StoreOut])
async def list_(
    db: AsyncSession = Depends(get_db),
):
    return await list_stores(db)


@router.post("/admin", response_model=StoreOut)
async def create(
    payload: StoreCreate,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    if user["role"] != "admin":
        forbidden()

    return await create_store(db, payload.model_dump())


@router.patch("/admin/inventory", response_model=InventoryOut)
async def update_inventory(
    payload: InventoryUpdate,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    if user["role"] != "admin":
        forbidden()

    return await update_stock(
        db=db,
        store_id=payload.store_id,
        product_id=payload.product_id,
        stock=payload.stock,
    )

