# app/llm/tools.py
from uuid import UUID
from app.schema.schemas import CheckoutCreate

class Tools:
    def __init__(self, db, user_id: UUID):
        self.db = db
        self.user_id = user_id

        from app.services import (
            product_service,
            cart_service,
            order_service,
            delivery_service,
            complaint_service,
            refund_service,
            user_service,
            recommendation_service
        )

        self.product_service = product_service
        self.cart_service = cart_service
        self.order_service = order_service
        self.delivery_service = delivery_service
        self.complaint_service = complaint_service
        self.refund_service = refund_service
        self.user_service = user_service
        self.recommendation_service = recommendation_service

    async def list_products(self):
        return await self.product_service.list_products(self.db)

    async def view_product(self, product_id: str):
        return await self.product_service.get_product(
            self.db, UUID(product_id), self.user_id
        )

    async def recommend_products(self):
        return await self.recommendation_service.recommend_for_user(
            self.db, self.user_id
        )

    async def view_cart(self):
        return await self.cart_service.get_cart_items(
            self.db, self.user_id
        )

    async def add_to_cart(self, variant_id: str, quantity: int):
        await self.cart_service.add_item(
            self.db, self.user_id, UUID(variant_id), quantity
        )
        return {"status": "added"}

    async def remove_from_cart(self, variant_id: str):
        await self.cart_service.update_item(
            self.db, self.user_id, UUID(variant_id), 0
        )
        return {"status": "removed"}

    async def create_order(self, address_id: str, fulfillment_type="delivery", store_id=None):
        # Fix: Convert dict args to Pydantic Model required by service
        payload = CheckoutCreate(
            address_id=UUID(address_id),
            fulfillment_type=fulfillment_type,
            store_id=UUID(store_id) if store_id else None
        )
        
        return await self.order_service.checkout(
            db=self.db,
            user_id=self.user_id,
            payload=payload, 
        )

    async def cancel_order(self, order_id: str):
        await self.order_service.cancel_order(
            self.db, self.user_id, UUID(order_id)
        )
        return {"status": "cancelled"}

    async def order_timeline(self, order_id: str):
        return await self.order_service.get_order_timeline(
            self.db, UUID(order_id), self.user_id
        )

    async def get_delivery_status(self, order_id: str):
        return await self.delivery_service.get_delivery_for_order(
            self.db, UUID(order_id), self.user_id
        )

    async def raise_complaint(self, order_id: str, description: str):
        return await self.complaint_service.create(
            self.db, self.user_id, UUID(order_id), description
        )

    async def request_refund(self, order_id: str, reason: str):
        return await self.refund_service.create(
            self.db, self.user_id, UUID(order_id), reason
        )

    async def get_user_preferences(self):
        return await self.user_service.get_user_preferences(
            self.db, self.user_id
        )

    async def update_user_profile(self, name: str | None = None):
        return await self.user_service.update_me(
            self.db, self.user_id, {"name": name}
        )
