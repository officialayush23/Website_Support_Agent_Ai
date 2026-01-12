# app/llm/tools.py
from uuid import UUID
from typing import Optional, Dict, Any

class Tools:
    """
    Every method here is a capability the chatbot has.
    """

    def __init__(self, db, user_id):
        self.db = db
        self.user_id = user_id

        # 🔌 service wiring
        from app.services import (
            product_service,
            cart_service,
            complaint_service,
            refund_service,
            address_service,
            recommendation_service,
            offer_service,
            order_service,
            user_service,delivery_service
        )

        self.product_service = product_service
        self.cart_service = cart_service
        self.complaint_service = complaint_service
        self.refund_service = refund_service
        self.address_service = address_service
        self.reco_service = recommendation_service
        self.offer_service = offer_service
        self.order_service = order_service
        self.user_service = user_service
        self.delivery_service = delivery_service

    # ---------- PRODUCTS ----------
    async def list_products(self, filters: Optional[Dict[str, Any]] = None):
        return await self.product_service.list_products(
            self.db, filters, self.user_id
        )

    async def view_product(self, product_id: UUID):
        return await self.product_service.get_product(
            self.db, product_id, self.user_id
        )

    async def recommend_products(self):
        return await self.reco_service.recommend_for_user(
            self.db, self.user_id
        )

    async def offers_for_product(self, product_id: UUID):
        return await self.offer_service.get_offers_for_product(
            self.db, product_id
        )

    # ---------- CART ----------
    async def add_to_cart(self, product_id: UUID, quantity: int):
        await self.cart_service.add_item(
            self.db, self.user_id, product_id, quantity
        )
        return {"status": "added"}

    async def remove_from_cart(self, product_id: UUID):
        await self.cart_service.update_item(
            self.db, self.user_id, product_id, 0
        )
        return {"status": "removed"}

    async def view_cart(self):
        return await self.cart_service.get_cart_items(
            self.db, self.user_id
        )

    # ---------- ADDRESSES ----------
    async def list_addresses(self):
        return await self.address_service.list_addresses(
            self.db, self.user_id
        )

    async def add_address(self, data: Dict[str, Any]):
        return await self.address_service.create_address(
            self.db, self.user_id, data
        )

    async def delete_address(self, address_id: UUID):
        await self.address_service.delete_address(
            self.db, self.user_id, address_id
        )
        return {"status": "deleted"}

    async def set_default_address(self, address_id: UUID):
        await self.address_service.set_default(
            self.db, self.user_id, address_id
        )
        return {"status": "updated"}

    # ---------- ORDERS ----------
    async def create_order(self, address_id: UUID):
        return await self.order_service.create_order(
            self.db, self.user_id, address_id
        )

    async def get_delivery_status(self, order_id: UUID):
        return await self.order_service.get_status(
            self.db, self.user_id, order_id
        )

    # ---------- COMPLAINTS ----------
    async def raise_complaint(self, order_id: UUID, description: str):
        return await self.complaint_service.create(
            self.db, self.user_id, order_id, description
        )

    async def complaint_status(self, complaint_id: UUID):
        return await self.complaint_service.get_status(
            self.db, self.user_id, complaint_id
        )

    # ---------- REFUNDS ----------
    async def request_refund(self, order_id: UUID, reason: str):
        return await self.refund_service.create(
            self.db, self.user_id, order_id, reason
        )

    async def refund_status(self, refund_id: UUID):
        return await self.refund_service.get_status(
            self.db, self.user_id, refund_id
        )

    # ---------- USER PREFERENCES ----------
    async def get_user_preferences(self):
        return await self.user_service.get_preferences(
            self.db, self.user_id
        )

    async def update_user_preferences(self, prefs: Dict[str, Any]):
        await self.user_service.update_preferences(
            self.db, self.user_id, prefs
        )
        return {"status": "updated"}
        # ---------- DELIVERY ----------

    async def update_delivery_status(
        self,
        delivery_id: UUID,
        status: str,
    ):
        return await self.delivery_service.update_delivery(
            self.db,
            delivery_id,
            DeliveryStatus(status),
        )

