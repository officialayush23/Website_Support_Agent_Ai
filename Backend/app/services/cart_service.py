# app/services/cart_service.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID, uuid4

from app.models.models import Cart, CartItem, Product
from app.services.user_event_service import record_event
from app.utils.api_error import not_found, bad_request


async def get_or_create_cart(db: AsyncSession, user_id: UUID) -> Cart:
    res = await db.execute(
        select(Cart).where(Cart.user_id == user_id)
    )
    cart = res.scalar_one_or_none()

    if not cart:
        cart = Cart(id=uuid4(), user_id=user_id)
        db.add(cart)
        await db.flush()

    return cart


async def get_cart_items(db: AsyncSession, user_id: UUID):
    cart = await get_or_create_cart(db, user_id)

    res = await db.execute(
        select(CartItem)
        .where(CartItem.cart_id == cart.id)
        .options()  # product relationship already lazy-loaded
    )
    return res.scalars().all()


async def add_item(
    db: AsyncSession,
    user_id: UUID,
    product_id: UUID,
    qty: int,
):
    if qty <= 0:
        bad_request("Quantity must be greater than zero")

    product = await db.get(Product, product_id)
    if not product or not product.is_active:
        not_found("Product")

    cart = await get_or_create_cart(db, user_id)

    item = await db.get(
        CartItem, {"cart_id": cart.id, "product_id": product_id}
    )

    if item:
        item.quantity += qty
    else:
        item = CartItem(
            cart_id=cart.id,
            product_id=product_id,
            quantity=qty,
        )
        db.add(item)

    await record_event(
        db=db,
        user_id=user_id,
        event_type="add_to_cart",
        product_id=product_id,
    )

    await db.commit()


async def update_item(
    db: AsyncSession,
    user_id: UUID,
    product_id: UUID,
    qty: int,
):
    cart = await get_or_create_cart(db, user_id)

    item = await db.get(
        CartItem, {"cart_id": cart.id, "product_id": product_id}
    )
    if not item:
        not_found("Cart item")

    if qty <= 0:
        await db.delete(item)
        await record_event(
            db=db,
            user_id=user_id,
            event_type="remove_from_cart",
            product_id=product_id,
        )
    else:
        item.quantity = qty

    await db.commit()


async def clear_cart(db: AsyncSession, user_id: UUID):
    cart = await get_or_create_cart(db, user_id)

    await db.execute(
        CartItem.__table__.delete().where(CartItem.cart_id == cart.id)
    )

    await db.commit()
