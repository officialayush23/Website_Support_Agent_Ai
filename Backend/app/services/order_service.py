# app/services/order_service.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from uuid import UUID, uuid4
from sqlalchemy.orm import selectinload
from app.models.models import Order, OrderItem, Cart, CartItem, Address
from app.utils.api_error import bad_request, not_found
from app.schema.enums import OrderStatus

ORDER_CANCEL_ALLOWED = {"pending"}


# =========================
# CREATE ORDER
# =========================
async def create_order(
    db: AsyncSession,
    user_id: UUID,
    address_id: UUID,
):
    # 🔒 Validate address
    address = await db.get(Address, address_id)
    if not address or address.user_id != user_id:
        not_found("Address")

    # 🛒 Fetch cart
    res = await db.execute(
        select(Cart).where(Cart.user_id == user_id)
    )
    cart = res.scalar_one_or_none()
    if not cart:
        bad_request("Cart is empty")

    # 🧾 Fetch cart items + products (NO N+1)
    res = await db.execute(
        select(CartItem)
        .where(CartItem.cart_id == cart.id)
        .options(selectinload(CartItem.product))
    )
    items = res.scalars().all()

    if not items:
        bad_request("Cart is empty")

    # 📦 Create order
    order = Order(
        id=uuid4(),
        user_id=user_id,
        address_id=address_id,
        status="pending",   # ✅ string, DB enum handles it
        total=0,
    )
    db.add(order)
    await db.flush()

    total = 0.0

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

    # 🧹 Clear cart in one shot
    await db.execute(
        delete(CartItem).where(CartItem.cart_id == cart.id)
    )

    await db.commit()
    await db.refresh(order)
    return order


# =========================
# LIST ORDERS
# =========================
async def list_orders(
    db: AsyncSession,
    user_id: UUID,
):
    res = await db.execute(
        select(Order)
        .where(Order.user_id == user_id)
        .options(selectinload(Order.items))
        .order_by(Order.created_at.desc())
    )
    return res.scalars().all()


# =========================
# CANCEL ORDER
# =========================
from app.services.inventory_service import release_inventory_for_order

async def cancel_order(
    db: AsyncSession,
    user_id: UUID,
    order_id: UUID,
):
    order = await db.get(Order, order_id)
    if not order or order.user_id != user_id:
        not_found("Order")

    if order.status != OrderStatus.pending.value:
        bad_request("Order cannot be cancelled")

    order.status = OrderStatus.cancelled.value

    await release_inventory_for_order(db, order_id)

    await db.commit()
