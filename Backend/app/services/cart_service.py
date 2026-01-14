# app/services/cart_service.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from uuid import UUID, uuid4

from app.models.models import (
    Cart,
    CartItem,
    Product,
    Order,
    OrderItem,
    GlobalInventory,
    Inventory,
    Pickup,
)
from app.schema.schemas import CheckoutCreate
from app.schema.enums import OrderStatus, UserEventType
from app.services.user_event_service import record_event
from app.utils.api_error import not_found, bad_request


# ---------------- CART ---------------- #

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
        .options(selectinload(CartItem.product))
    )

    items = res.scalars().all()
    total = 0.0

    response_items = []
    for item in items:
        line_total = float(item.product.price) * item.quantity
        total += line_total

        response_items.append({
            "product_id": item.product_id,
            "quantity": item.quantity,
            "line_total": line_total,
        })

    return {
        "cart_id": cart.id,
        "items": response_items,
        "total": total,
    }


async def add_item(
    db: AsyncSession,
    user_id: UUID,
    product_id: UUID,
    qty: int,
):
    if qty <= 0:
        bad_request("Quantity must be positive")

    cart = await get_or_create_cart(db, user_id)

    item = await db.get(
        CartItem,
        {"cart_id": cart.id, "product_id": product_id},
    )

    if item:
        item.quantity += qty
    else:
        db.add(
            CartItem(
                cart_id=cart.id,
                product_id=product_id,
                quantity=qty,
            )
        )

    cart.updated_at = func.now()

    await record_event(
        db=db,
        user_id=user_id,
        event_type=UserEventType.add_to_cart,
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
        CartItem,
        {"cart_id": cart.id, "product_id": product_id},
    )
    if not item:
        not_found("Cart item")

    if qty <= 0:
        await db.delete(item)
        await record_event(
            db=db,
            user_id=user_id,
            event_type=UserEventType.remove_from_cart,
            product_id=product_id,
        )
    else:
        item.quantity = qty

    cart.updated_at = func.now()
    await db.commit()


async def clear_cart(db: AsyncSession, user_id: UUID):
    cart = await get_or_create_cart(db, user_id)

    await db.execute(
        CartItem.__table__.delete().where(
            CartItem.cart_id == cart.id
        )
    )
    await db.commit()


# ---------------- CHECKOUT ---------------- #

async def checkout(
    db: AsyncSession,
    user_id: UUID,
    payload: CheckoutCreate,
):
    cart = await get_or_create_cart(db, user_id)

    res = await db.execute(
        select(CartItem)
        .where(CartItem.cart_id == cart.id)
        .options(selectinload(CartItem.product))
    )
    items = res.scalars().all()

    if not items:
        bad_request("Cart is empty")

    total = sum(
        float(i.product.price) * i.quantity
        for i in items
    )

    order = Order(
        id=uuid4(),
        user_id=user_id,
        address_id=payload.address_id,
        fulfillment_type=payload.fulfillment_type,
        store_id=payload.store_id,
        status=OrderStatus.pending.value,
        total=total,
    )
    db.add(order)
    await db.flush()

    # ----- INVENTORY LOCKING -----

    if payload.fulfillment_type == "delivery":
        for item in items:
            gi = await db.get(GlobalInventory, item.product_id)
            if not gi or gi.total_stock - gi.reserved_stock < item.quantity:
                bad_request("Out of stock")

            gi.reserved_stock += item.quantity

    else:  # pickup
        if not payload.store_id:
            bad_request("store_id required for pickup")

        for item in items:
            inv = await db.get(
                Inventory,
                {
                    "store_id": payload.store_id,
                    "product_id": item.product_id,
                },
            )
            if not inv or inv.stock < item.quantity:
                bad_request("Store out of stock")

            inv.stock -= item.quantity

            gi = await db.get(GlobalInventory, item.product_id)
            gi.reserved_stock += item.quantity

        db.add(
            Pickup(
                id=uuid4(),
                order_id=order.id,
                store_id=payload.store_id,
                user_id=user_id,
                amount=total,
                status="ready",
            )
        )

    # ----- ORDER ITEMS -----
    for item in items:
        db.add(
            OrderItem(
                id=uuid4(),
                order_id=order.id,
                product_id=item.product_id,
                quantity=item.quantity,
                price=float(item.product.price),
            )
        )

    # clear cart
    await db.execute(
        CartItem.__table__.delete().where(
            CartItem.cart_id == cart.id
        )
    )

    await record_event(
        db=db,
        user_id=user_id,
        event_type=UserEventType.order_created,
        order_id=order.id,
    )

    await db.commit()
    await db.refresh(order)
    return order
