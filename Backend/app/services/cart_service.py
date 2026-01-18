# app/services/cart_service.py

from uuid import UUID, uuid4
from typing import List, Dict

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, delete,text
from sqlalchemy.orm import selectinload

from app.models.models import (
    Cart,
    CartItem,
    Order,
    OrderItem,
    GlobalInventory,
    StoreInventory,
    Pickup,
    ProductVariant,
)

from app.schema.schemas import CheckoutCreate  # OK (request DTO)
from app.models.enums import (
    order_status_enum,          # DB write only
    fulfillment_type_enum,
    fulfillment_source_enum,
)
from app.schema.enums import (
    FulfillmentType,
    FulfillmentSource,
    PickupStatus,
    UserEventType,
)

from app.models.enums import user_event_type_enum
from app.services.user_event_service import record_event
from app.services.offer_service import list_active_offers, evaluate_offer
from app.services.pickup_service import find_best_store_for_pickup
from app.utils.api_error import not_found, bad_request


# =====================================================
# CART CORE (VARIANT BASED)
# =====================================================

async def get_or_create_cart(db: AsyncSession, user_id: UUID) -> Cart:
    res = await db.execute(
        select(Cart).where(Cart.user_id == user_id)
    )
    cart = res.scalar_one_or_none()

    if not cart:
        cart = Cart(id=uuid4(), user_id=user_id)
        db.add(cart)
        await db.commit()
        await db.refresh(cart)

    return cart


async def get_cart_items(db: AsyncSession, user_id: UUID) -> Dict:
    cart = await get_or_create_cart(db, user_id)

    res = await db.execute(
        select(CartItem)
        .where(CartItem.cart_id == cart.id)
        .options(
            selectinload(CartItem.variant)
            .selectinload(ProductVariant.product)
        )
    )
    items = res.scalars().all()

    total = 0.0
    out_items = []

    for item in items:
        price = float(item.variant.price)
        line_total = price * item.quantity
        total += line_total

        out_items.append({
            "variant_id": item.variant_id,
            "product_id": item.variant.product_id,
            "name": item.variant.product.name,
            "price": price,
            "quantity": item.quantity,
            "line_total": line_total,
            "attributes": item.variant.attributes,
        })

    return {
        "cart_id": cart.id,
        "total": total,
        "items": out_items,
    }


async def add_item(
    db: AsyncSession,
    *,
    user_id: UUID,
    variant_id: UUID,
    quantity: int,
):
    if quantity <= 0:
        bad_request("Quantity must be positive")

    cart = await get_or_create_cart(db, user_id)

    item = await db.get(
        CartItem,
        {"cart_id": cart.id, "variant_id": variant_id},
    )

    if item:
        item.quantity += quantity
    else:
        db.add(
            CartItem(
                cart_id=cart.id,
                variant_id=variant_id,
                quantity=quantity,
            )
        )

    cart.updated_at = func.now()

    await record_event(
        db=db,
        user_id=user_id,
        event_type=user_event_type_enum.add_to_cart,
        variant_id=variant_id,
    )

    await db.commit()


async def update_item(
    db: AsyncSession,
    *,
    user_id: UUID,
    variant_id: UUID,
    quantity: int,
):
    cart = await get_or_create_cart(db, user_id)

    item = await db.get(
        CartItem,
        {"cart_id": cart.id, "variant_id": variant_id},
    )
    if not item:
        not_found("Cart item")

    if quantity <= 0:
        await db.delete(item)
        await record_event(
            db=db,
            user_id=user_id,
            event_type=user_event_type_enum.remove_from_cart,
            variant_id=variant_id,
        )
    else:
        item.quantity = quantity

    cart.updated_at = func.now()
    await db.commit()


async def clear_cart(db: AsyncSession, user_id: UUID):
    cart = await get_or_create_cart(db, user_id)
    await db.execute(
        delete(CartItem).where(CartItem.cart_id == cart.id)
    )
    await db.commit()


# =====================================================
# AVAILABILITY (FALLBACK FOR UI)
# =====================================================
async def list_stores_that_can_fulfill_cart(
    db: AsyncSession,
    *,
    user_id: UUID,
) -> list[dict]:
    """
    Returns stores that can fulfill ENTIRE cart,
    ordered by nearest distance to user.
    """

    res = await db.execute(
        select(CartItem)
        .join(Cart)
        .where(Cart.user_id == user_id)
    )
    items = res.scalars().all()
    if not items:
        bad_request("Cart is empty")

    variant_ids = [i.variant_id for i in items]
    qty_map = {i.variant_id: i.quantity for i in items}

    res = await db.execute(
        text("""
        SELECT
            s.id AS store_id,
            s.name,
            ST_Distance(s.location, u.location) AS distance
        FROM stores s
        JOIN users u ON u.id = :user_id
        JOIN store_inventory si ON si.store_id = s.id
        WHERE s.is_active = true
          AND si.variant_id = ANY(:variant_ids)
        GROUP BY s.id, u.location
        HAVING COUNT(DISTINCT si.variant_id) = :variant_count
        ORDER BY distance
        """),
        {
            "user_id": user_id,
            "variant_ids": variant_ids,
            "variant_count": len(variant_ids),
        },
    )

    stores = []
    for row in res.fetchall():
        inv_res = await db.execute(
            select(StoreInventory)
            .where(
                StoreInventory.store_id == row.store_id,
                StoreInventory.variant_id.in_(variant_ids),
            )
        )
        inventories = inv_res.scalars().all()

        if all(inv.in_hand_stock >= qty_map[inv.variant_id] for inv in inventories):
            stores.append({
                "store_id": row.store_id,
                "name": row.name,
                "distance_m": row.distance,
            })

    return stores



# =====================================================
# OFFERS PREVIEW (UI SAFE)
# =====================================================

async def preview_cart_offers(
    db: AsyncSession,
    *,
    user_id: UUID,
) -> Dict:
    cart = await get_or_create_cart(db, user_id)

    res = await db.execute(
        select(CartItem)
        .where(CartItem.cart_id == cart.id)
        .options(selectinload(CartItem.variant))
    )
    items = res.scalars().all()

    if not items:
        return {"subtotal": 0, "offers": [], "best_discount": 0}

    subtotal = sum(
        float(i.variant.price) * i.quantity for i in items
    )

    offers = await list_active_offers(db)
    applied = []

    for offer in offers:
        discount = evaluate_offer(offer, subtotal)
        if discount > 0:
            applied.append({
                "offer_id": offer.id,
                "title": offer.title,
                "discount": discount,
            })

    best = max((o["discount"] for o in applied), default=0)

    return {
        "subtotal": subtotal,
        "offers": applied,
        "best_discount": best,
        "payable": subtotal - best,
    }


# =====================================================
# CHECKOUT (STRICT + CANONICAL)
# =====================================================
async def checkout(
    db: AsyncSession,
    *,
    user_id: UUID,
    payload: CheckoutCreate,
):
    # =====================================================
    # LOAD CART
    # =====================================================
    cart = await get_or_create_cart(db, user_id)

    res = await db.execute(
        select(CartItem)
        .where(CartItem.cart_id == cart.id)
        .options(selectinload(CartItem.variant))
    )
    items = res.scalars().all()

    if not items:
        bad_request("Cart is empty")

    # deterministic ordering (important for locks)
    items.sort(key=lambda x: x.variant_id)

    subtotal = sum(float(i.variant.price) * i.quantity for i in items)

    # =====================================================
    # FULFILLMENT VALIDATION
    # =====================================================
    store_id: UUID | None = None

    if payload.fulfillment_type == FulfillmentType.pickup:
        # ❗ user MUST choose store explicitly
        if not payload.store_id:
            bad_request("store_id is required for pickup")

        store_id = payload.store_id

        # validate store can fulfill ENTIRE cart (lock store rows)
        for item in items:
            inv = await db.get(
                StoreInventory,
                {
                    "store_id": store_id,
                    "variant_id": item.variant_id,
                },
                with_for_update=True,
            )
            if not inv or inv.in_hand_stock < item.quantity:
                bad_request("Selected store cannot fulfill cart")

    # =====================================================
    # OFFERS
    # =====================================================
    offers = await list_active_offers(db)
    discount_total = max(
        (evaluate_offer(o, subtotal=subtotal) for o in offers),
        default=0,
    )

    total = max(subtotal - discount_total, 0)

    # =====================================================
    # CREATE ORDER
    # =====================================================
    order = Order(
        id=uuid4(),
        user_id=user_id,
        address_id=payload.address_id
        if payload.fulfillment_type == FulfillmentType.delivery
        else None,
        fulfillment_type=payload.fulfillment_type.value,
        store_id=store_id,
        status=order_status_enum.pending,
        subtotal=subtotal,
        discount_total=discount_total,
        total=total,
    )
    db.add(order)
    await db.flush()

    await record_event(
        db=db,
        user_id=user_id,
        event_type=user_event_type_enum.checkout_started,
    )

    # =====================================================
    # INVENTORY LOCK (ATOMIC + SAFE)
    # =====================================================
    # 1️⃣ validate global inventory first
    for item in items:
        gi = (
            await db.execute(
                select(GlobalInventory)
                .where(GlobalInventory.variant_id == item.variant_id)
                .with_for_update()
            )
        ).scalar_one_or_none()

        if not gi or gi.total_stock - gi.reserved_stock < item.quantity:
            bad_request("Out of stock")

    # 2️⃣ apply mutations only after all checks pass
    for item in items:
        gi = await db.get(GlobalInventory, item.variant_id)
        gi.reserved_stock += item.quantity

        if payload.fulfillment_type == FulfillmentType.pickup:
            inv = await db.get(
                StoreInventory,
                {
                    "store_id": store_id,
                    "variant_id": item.variant_id,
                },
            )
            inv.in_hand_stock -= item.quantity

    # =====================================================
    # ORDER ITEMS
    # =====================================================
    for item in items:
        db.add(
            OrderItem(
                id=uuid4(),
                order_id=order.id,
                variant_id=item.variant_id,
                quantity=item.quantity,
                price=float(item.variant.price),
                fulfillment_source=(
                    FulfillmentSource.store.value
                    if payload.fulfillment_type == FulfillmentType.pickup
                    else FulfillmentSource.global_.value
                ),
                fulfillment_ref_id=(
                    store_id
                    if payload.fulfillment_type == FulfillmentType.pickup
                    else item.variant_id
                ),
            )
        )

    # =====================================================
    # PICKUP RECORD
    # =====================================================
    if payload.fulfillment_type == FulfillmentType.pickup:
        db.add(
            Pickup(
                id=uuid4(),
                order_id=order.id,
                store_id=store_id,
                user_id=user_id,
                amount=total,
                status=PickupStatus.ready.value,
            )
        )

    # =====================================================
    # CLEANUP + EVENTS
    # =====================================================
    await db.execute(
        delete(CartItem).where(CartItem.cart_id == cart.id)
    )

    await record_event(
        db=db,
        user_id=user_id,
        event_type=user_event_type_enum.order_created,
        order_id=order.id,
    )

    await db.commit()

    # =====================================================
    # RESPONSE
    # =====================================================
    return {
        "order_id": order.id,
        "status": order.status,
        "subtotal": subtotal,
        "discount_total": discount_total,
        "total": total,
        "fulfillment_type": payload.fulfillment_type.value,
        "store_id": store_id,
        "created_at": order.created_at,
    }
