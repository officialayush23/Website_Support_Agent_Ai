# # app/api/routers/admin.py
# from app.models.models import GlobalInventory
# from fastapi import APIRouter, Depends
# from sqlalchemy.ext.asyncio import AsyncSession
# from uuid import UUID

# from app.core.database import get_db
# from app.core.auth import get_current_user
# from app.schema.schemas import GlobalStockUpdate
# from app.services.inventory_admin_service import update_global_stock
# from app.services.product_service import (
#     create_product,
#     update_product,
#     delete_product,
# )
# from app.schema.schemas import ProductCreate, ProductUpdate
# from app.utils.api_error import forbidden

# router = APIRouter(prefix="/admin", tags=["Admin"])


# def admin_only(user):
#     if user["role"] != "admin":
#         forbidden()


# @router.post("/products")
# async def create(
#     payload: ProductCreate,
#     db: AsyncSession = Depends(get_db),
#     user=Depends(get_current_user),
# ):
#     admin_only(user)
#     p = await create_product(db, payload.model_dump())
#     return {"id": p.id}


# @router.patch("/products/{product_id}")
# async def update(
#     product_id: UUID,
#     payload: ProductUpdate,
#     db: AsyncSession = Depends(get_db),
#     user=Depends(get_current_user),
# ):
#     admin_only(user)
#     await update_product(
#         db,
#         product_id,
#         payload.model_dump(exclude_unset=True),
#     )
#     return {"status": "updated"}


# @router.delete("/products/{product_id}")
# async def delete(
#     product_id: UUID,
#     db: AsyncSession = Depends(get_db),
#     user=Depends(get_current_user),
# ):
#     admin_only(user)
#     await delete_product(db, product_id)
#     return {"status": "deleted"}







# @router.patch("/inventory/global")
# async def set_global_stock(
#     payload: GlobalStockUpdate,
#     db: AsyncSession = Depends(get_db),
#     user=Depends(get_current_user),
# ):
#     if user["role"] != "admin":
#         forbidden()

#     await update_global_stock(
#         db,
#         payload.product_id,
#         payload.total_stock,
#     )
#     return {"status": "updated"}


# @router.get("/products/{product_id}/stock")
# async def product_stock(
#     product_id: UUID,
#     db: AsyncSession = Depends(get_db),
#     user=Depends(get_current_user),
# ):
#     if user["role"] != "admin":
#         forbidden()

#     gi = await db.get(GlobalInventory, product_id)

#     if not gi:
#         gi = GlobalInventory(
#             product_id=product_id,
#             total_stock=0,
#             reserved_stock=0,
#         )
#         db.add(gi)
#         await db.commit()
#         await db.refresh(gi)

#     return {
#         "total": gi.total_stock,
#         "reserved": gi.reserved_stock,
#         "available": gi.total_stock - gi.reserved_stock,
#     }


# app/api/routers/admin.py

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from sqlalchemy import select, func
from app.core.database import get_db
from app.core.auth import get_current_user
from app.services.product_service import (
    create_product,
    update_product,
    delete_product,
)
from app.models.models import Order
from app.services.store_service import update_global_stock
from app.schema.schemas import ProductCreate, ProductUpdate, GlobalStockUpdate
from app.utils.api_error import forbidden

router = APIRouter(prefix="/admin", tags=["Admin"])


def admin_only(user):
    if user["role"] != "admin":
        forbidden()


@router.post("/products")
async def create(
    payload: ProductCreate,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    admin_only(user)
    p = await create_product(db, **payload.model_dump())
    return {"id": p.id}


@router.patch("/products/{product_id}")
async def update(
    product_id: UUID,
    payload: ProductUpdate,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    admin_only(user)
    await update_product(
        db=db,
        product_id=product_id,
        data=payload.model_dump(exclude_unset=True),
    )
    return {"status": "updated"}


@router.delete("/products/{product_id}")
async def delete(
    product_id: UUID,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    admin_only(user)
    await delete_product(db=db, product_id=product_id)
    return {"status": "deleted"}


@router.patch("/inventory/global")
async def set_global_stock(
    payload: GlobalStockUpdate,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    admin_only(user)
    await update_global_stock(
        db=db,
        variant_id=payload.variant_id,
        total_stock=payload.total_stock,
    )
    return {"status": "updated"}


@router.get("/admin/summary")
async def kpi_summary(
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    if user["role"] != "admin":
        forbidden()

    res = await db.execute(
        select(
            func.count(Order.id),
            func.sum(Order.total),
        )
    )

    orders, revenue = res.first()

    return {
        "total_orders": orders or 0,
        "total_revenue": float(revenue or 0),
    }
