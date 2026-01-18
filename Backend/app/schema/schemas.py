# app/schema/schemas.py
from pydantic import BaseModel, Field, model_validator
from typing import Optional, List, Dict, Any,Literal
from uuid import UUID
from datetime import datetime, time

from app.schema.enums import *
from app.models.enums import (
    user_role_enum,)

# ================= USERS =================



class UserOut(BaseModel):
    id: UUID
    name: Optional[str]
    role: str 
    is_payment_agent_enabled: bool


    class Config:
        from_attributes = True


# ================= ADDRESSES =================

class AddressCreate(BaseModel):
    label: str
    address_line1: str
    address_line2: Optional[str] = None
    city: str
    state: str
    pincode: str
    country: str = "India"
    is_default: bool = False


class AddressOut(AddressCreate):
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True


# ================= STORES =================

class StoreHourCreate(BaseModel):
    day_of_week: int = Field(ge=0, le=6)
    opens_at: time
    closes_at: time
    is_closed: bool = False


class StoreHourOut(StoreHourCreate):
    id: UUID

    class Config:
        from_attributes = True


class StoreCreate(BaseModel):
    name: str
    city: str
    state: str
    latitude: float
    longitude: float
    is_active: bool = True


class StoreOut(StoreCreate):
    id: UUID

    class Config:
        from_attributes = True


# ================= PRODUCTS =================

class ProductVariantCreate(BaseModel):
    product_id: UUID
    sku: str
    price: float
    attributes: Optional[Dict[str, Any]] = None


class ProductVariantOut(BaseModel):
    id: UUID
    sku: Optional[str]
    price: float
    attributes: Optional[Dict[str, Any]]

    class Config:
        from_attributes = True


class ProductOut(BaseModel):
    id: UUID
    name: str
    category: Optional[str]
    description: Optional[str]
    variants: List[ProductVariantOut] = []

    class Config:
        from_attributes = True


# ================= CART =================

class CartItemCreate(BaseModel):
    variant_id: UUID
    quantity: int = Field(gt=0)


class CartItemUpdate(BaseModel):
    quantity: int = Field(ge=0)


class CartItemOut(BaseModel):
    variant_id: UUID
    quantity: int

    class Config:
        from_attributes = True

class CartOut(BaseModel):
    id: UUID
    user_id: UUID
    items: List[CartItemOut]
    updated_at: datetime

    class Config:
        from_attributes = True

# ================= OFFERS =================

class OfferCreate(BaseModel):
    title: str
    description: Optional[str] = None

    min_cart_value: float = 0
    percentage_off: Optional[float] = None
    amount_off: Optional[float] = None
    max_discount: Optional[float] = None

    priority: int = 0
    stackable: bool = False

    starts_at: datetime
    ends_at: datetime
    is_active: bool = True

    @model_validator(mode="after")
    def validate_discount(self):
        if not self.percentage_off and not self.amount_off:
            raise ValueError("Either percentage_off or amount_off required")
        return self


class OfferOut(OfferCreate):
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True


# ================= CHECKOUT / ORDERS =================
class CheckoutOut(BaseModel):
    order_id: UUID
    status: str
    subtotal: float
    discount_total: float
    total: float
    fulfillment_type: FulfillmentType
    store_id: Optional[UUID]
    created_at: datetime

class CheckoutCreate(BaseModel):
    address_id: Optional[UUID] = None
    fulfillment_type: FulfillmentType = FulfillmentType.delivery
    store_id: Optional[UUID] = None
    payment_provider: str = "dummy"


class OrderItemOut(BaseModel):
    variant_id: UUID
    quantity: int
    price: float
    fulfillment_source: FulfillmentSource

class OrderStatusHistoryOut(BaseModel):
    status: OrderStatus
    created_at: datetime

    class Config:
        from_attributes = True

class OrderOut(BaseModel):
    id: UUID
    status: OrderStatus
    fulfillment_type: FulfillmentType
    store_id: Optional[UUID]
    subtotal: float
    discount_total: float
    status_history: List[OrderStatusHistoryOut] = []
    total: float
    created_at: datetime
    items: List[OrderItemOut]

    class Config:
        from_attributes = True

class AgentActionOut(BaseModel):
    id: UUID
    conversation_id: UUID
    action_type: str        
    payload: Dict[str, Any] 
    status: str             
    created_at: datetime

    class Config:
        from_attributes = True



# ================= DELIVERY / PICKUP =================

class DeliveryOut(BaseModel):
    id: UUID
    order_id: UUID
    status: DeliveryStatus
    eta: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True
class PickupOut(BaseModel):
    id: UUID
    order_id: UUID
    store_id: UUID
    user_id: UUID
    amount: float
    status: PickupStatus
    picked_up_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


# ================= COMPLAINTS / REFUNDS =================

class ComplaintCreate(BaseModel):
    order_id: UUID
    description: str


class ComplaintOut(BaseModel):
    id: UUID
    order_id: UUID
    description: str
    status: ComplaintStatus
    created_at: datetime

    class Config:
        from_attributes = True


class RefundCreate(BaseModel):
    order_id: UUID
    reason: str


class RefundOut(BaseModel):
    id: UUID
    order_id: UUID
    reason: str
    status: RefundStatus
    created_at: datetime

    class Config:
        from_attributes = True


# ================= CHAT =================

class MessageOut(BaseModel):
    id: UUID
    conversation_id: UUID
    role: MessageRole
    content: str
    created_at: datetime

    class Config:
        from_attributes = True

class MessageCreate(BaseModel):
    content: str


class ConversationOut(BaseModel):
    id: UUID
    status: str
    handled_by: str
    created_at: str
    last_message_at: str | None = None



# ================= ADMIN: PRODUCTS =================

class ProductCreate(BaseModel):
    name: str
    description: Optional[str] = None
    category: Optional[str] = None


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    is_active: Optional[bool] = None


# ================= INVENTORY =================

class GlobalStockUpdate(BaseModel):
    variant_id: UUID
    total_stock: int = Field(ge=0)


class InventoryUpdate(BaseModel):
    store_id: UUID
    variant_id: UUID
    allocated_stock: int = Field(ge=0)


class StoreInventoryItemOut(BaseModel):
    variant_id: UUID
    sku: str
    price: float
    allocated_stock: int
    in_hand_stock: int


class StoreInventoryOut(BaseModel):
    store_id: UUID
    store_name: str
    items: list[StoreInventoryItemOut]

# ================= PAYMENTS =================

class PaymentCreate(BaseModel):
    order_id: UUID
    provider: str = "dummy"


class PaymentOut(BaseModel):
    id: UUID
    order_id: UUID
    provider: str
    status: PaymentStatus
    amount: float
    created_at: datetime

    class Config:
        from_attributes = True


# ================= REFUNDS (ADMIN EXTENDED) =================

class RefundStatusUpdate(BaseModel):
    status: RefundStatus


class RefundAdminOut(BaseModel):
    id: UUID
    order_id: UUID
    reason: str
    status: RefundStatus
    amount: float
    created_at: datetime

class OfferUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None

    min_cart_value: Optional[float] = None
    percentage_off: Optional[float] = None
    amount_off: Optional[float] = None
    max_discount: Optional[float] = None

    priority: Optional[int] = None
    stackable: Optional[bool] = None

    starts_at: Optional[datetime] = None
    ends_at: Optional[datetime] = None
    is_active: Optional[bool] = None
class DeliveryAdminOut(BaseModel):
    id: UUID
    order_id: UUID
    user_id: UUID
    address_id: UUID | None

    status: DeliveryStatus
    eta: Optional[datetime]

    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True
class DeliveryCreate(BaseModel):
    order_id: UUID


class DeliveryUpdate(BaseModel):
    status: DeliveryStatus
    eta: Optional[datetime] = None
class ComplaintUpdate(BaseModel):
    status: ComplaintStatus

class UserUpdate(BaseModel):
    name: Optional[str] = None

class LeadCreate(BaseModel):
    email: str
    requirements: Optional[str] = None

class LeadOut(LeadCreate):
    id: UUID
    status: str
    created_at: datetime

    class Config:
        from_attributes = True

class StockAllocation(BaseModel):
    variant_id: UUID
    quantity: int



class AttributeDefinitionCreate(BaseModel):
    name: str
    description: Optional[str] = None
    value_type: str = "string"  # string | number | enum
    allowed_values: Optional[list[str]] = None
    is_required: bool = False
    is_active: bool = True


class AttributeDefinitionUpdate(BaseModel):
    description: Optional[str] = None
    value_type: Optional[str] = None
    allowed_values: Optional[list[str]] = None
    is_required: Optional[bool] = None
    is_active: Optional[bool] = None


class AttributeDefinitionOut(AttributeDefinitionCreate):
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True

class ProductStockOverviewOut(BaseModel):
    product_id: UUID
    name: str
    total_stock: int


class VariantStockOut(BaseModel):
    variant_id: UUID
    sku: str
    price: float
    total_stock: int
    available_stock: int


class InventoryMovementOut(BaseModel):
    id: UUID
    variant_id: UUID

    source: Optional[Literal["global_inventory", "store_inventory"]]
    destination: Optional[Literal["global_inventory", "store_inventory"]]

    quantity: int
    reason: str

    reference_type: Optional[str]
    reference_id: Optional[UUID]

    created_at: datetime