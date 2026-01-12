# app/services/order_service.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID, uuid4

from app.models.models import Order, OrderItem, Cart, CartItem, Address
from app.models.py_enums import OrderStatus
from app.utils.api_error import bad_request, not_found


ORDER_CANCEL_ALLOWED = {OrderStatus.pending}


async def create_order(
    db: AsyncSession,
    user_id: UUID,
    address_id: UUID,
):
    # validate address ownership
    address = await db.get(Address, address_id)
    if not address or address.user_id != user_id:
        not_found("Address")

    # fetch cart
    cart = await db.execute(
        select(Cart).where(Cart.user_id == user_id)
    )
    cart = cart.scalar_one_or_none()
    if not cart:
        bad_request("Cart is empty")

    items = await db.execute(
        select(CartItem)
        .where(CartItem.cart_id == cart.id)
    )
    items = items.scalars().all()

    if not items:
        bad_request("Cart is empty")

    order = Order(
        id=uuid4(),
        user_id=user_id,
        address_id=address_id,
        status=OrderStatus.pending.value,
        total=0,
    )
    db.add(order)
    await db.flush()

    total = 0
    for item in items:
        price = float(item.product.price)
        total += price * item.quantity

        db.add(
            OrderItem(
                id=uuid4(),
                order_id=order.id,
                product_id=item.product_id,
                quantity=item.quantity,
                price=price,
            )
        )

    order.total = total

    # clear cart
    for item in items:
        await db.delete(item)

    await db.commit()
    await db.refresh(order)
    return order


async def list_orders(db: AsyncSession, user_id: UUID):
    res = await db.execute(
        select(Order).where(Order.user_id == user_id)
    )
    return res.scalars().all()


async def cancel_order(
    db: AsyncSession,
    user_id: UUID,
    order_id: UUID,
):
    order = await db.get(Order, order_id)
    if not order or order.user_id != user_id:
        not_found("Order")

    current = OrderStatus(order.status)

    if current not in ORDER_CANCEL_ALLOWED:
        bad_request("Order cannot be cancelled")

    order.status = OrderStatus.cancelled.value
    await db.commit()
