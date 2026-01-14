from pydantic import BaseModel, Field, model_validator
from typing import Optional, List, Dict, Any, Literal
from uuid import UUID
from datetime import datetime, time

from app.schema.enums import (
    ConversationStatus,
    EmbeddingSourceType,
    OrderStatus,
    ComplaintStatus,
    PaymentStatus,
    MessageRole,
    RefundStatus,
    DeliveryStatus,
)

# =========================
# USER
# =========================

class UserOut(BaseModel):
    id: UUID
    name: Optional[str]
    role: str

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    name: Optional[str] = None


# =========================
# ADDRESS
# =========================

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


# =========================
# STORE & HOURS
# =========================

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


# =========================
# PRODUCT
# =========================

class ProductImageOut(BaseModel):
    id: UUID
    image_url: str
    is_primary: bool

    class Config:
        from_attributes = True


class ProductCreate(BaseModel):
    name: str
    description: Optional[str] = None
    category: Optional[str] = None
    price: float
    attributes: Optional[Dict[str, Any]] = None


class ProductUpdate(BaseModel):
    name: Optional[str]
    description: Optional[str]
    category: Optional[str]
    price: Optional[float]
    attributes: Optional[Dict[str, Any]]
    is_active: Optional[bool]


class ProductOut(BaseModel):
    id: UUID
    name: str
    price: float
    category: Optional[str]
    description: Optional[str]
    images: List[ProductImageOut] = Field(default_factory=list)

    class Config:
        from_attributes = True

# =========================
# OFFER
# =========================

class OfferCreate(BaseModel):
    title: str
    description: Optional[str] = None
    rules: Dict[str, Any]
    priority: int = 0
    stackable: bool = False
    starts_at: datetime
    ends_at: datetime
    is_active: bool = True

    @model_validator(mode="after")
    def validate_dates(self):
        if self.starts_at >= self.ends_at:
            raise ValueError("starts_at must be before ends_at")
        return self


class OfferUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    rules: Optional[Dict[str, Any]] = None
    priority: Optional[int] = None
    stackable: Optional[bool] = None
    starts_at: Optional[datetime] = None
    ends_at: Optional[datetime] = None
    is_active: Optional[bool] = None

    @model_validator(mode="after")
    def validate_dates(self):
        if self.starts_at and self.ends_at and self.starts_at >= self.ends_at:
            raise ValueError("starts_at must be before ends_at")
        return self


class OfferOut(BaseModel):
    id: UUID
    title: str
    description: Optional[str]
    rules: Dict[str, Any]
    priority: int
    stackable: bool
    starts_at: datetime
    ends_at: datetime
    is_active: bool

    class Config:
        from_attributes = True


# =========================
# INVENTORY
# =========================

class InventoryUpdate(BaseModel):
    store_id: UUID
    product_id: UUID
    stock: int = Field(ge=0)


class InventoryOut(BaseModel):
    store_id: UUID
    product_id: UUID
    stock: int
    updated_at: datetime

    class Config:
        from_attributes = True


# =========================
# CART
# =========================

class CartItemCreate(BaseModel):
    product_id: UUID
    quantity: int = Field(gt=0)


class CartItemUpdate(BaseModel):
    quantity: int = Field(
        ge=0,
        description="Set to 0 to remove item from cart"
    )


class CartItemOut(BaseModel):
    product_id: UUID
    quantity: int

    class Config:
        from_attributes = True


# =========================
# ORDER / CHECKOUT
# =========================

class OrderCreate(BaseModel):
    address_id: UUID


class CheckoutCreate(BaseModel):
    address_id: UUID
    payment_provider: str = "dummy"
    fulfillment_type: Literal["delivery", "pickup"] = "delivery"
    store_id: Optional[UUID] = None


class OrderItemOut(BaseModel):
    product_id: UUID
    quantity: int
    price: float


class OrderOut(BaseModel):
    id: UUID
    status: OrderStatus
    total: float
    created_at: datetime
    items: List[OrderItemOut]

    class Config:
        from_attributes = True


# =========================
# PAYMENT
# =========================

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


# =========================
# DELIVERY
# =========================

class DeliveryCreate(BaseModel):
    order_id: UUID
    courier: Optional[str] = None
    tracking_id: Optional[str] = None
    eta: Optional[datetime] = None


class DeliveryUpdate(BaseModel):
    status: DeliveryStatus
    courier: Optional[str] = None
    tracking_id: Optional[str] = None
    eta: Optional[datetime] = None


class DeliveryOut(BaseModel):
    id: UUID
    order_id: UUID
    status: DeliveryStatus
    courier: Optional[str]
    tracking_id: Optional[str]
    eta: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


# =========================
# REFUND
# =========================

class RefundCreate(BaseModel):
    order_id: UUID
    reason: str


class RefundStatusUpdate(BaseModel):
    status: RefundStatus


class RefundOut(BaseModel):
    id: UUID
    order_id: UUID
    status: RefundStatus
    created_at: datetime

    class Config:
        from_attributes = True


class RefundAdminOut(BaseModel):
    id: UUID
    order_id: UUID
    reason: Optional[str]
    status: RefundStatus
    created_at: datetime
    amount: Optional[float]

    class Config:
        from_attributes = True


# =========================
# CONVERSATION / MESSAGE
# =========================

class ConversationOut(BaseModel):
    id: UUID
    status: ConversationStatus
    created_at: datetime

    class Config:
        from_attributes = True


class MessageCreate(BaseModel):
    content: str


class MessageOut(BaseModel):
    id: UUID
    role: MessageRole
    content: str
    created_at: datetime

    class Config:
        from_attributes = True


# =========================
# COMPLAINT
# =========================

class ComplaintCreate(BaseModel):
    order_id: UUID
    description: str


class ComplaintUpdate(BaseModel):
    status: ComplaintStatus


class ComplaintOut(BaseModel):
    id: UUID
    order_id: UUID
    description: str
    status: ComplaintStatus
    created_at: datetime

    class Config:
        from_attributes = True


# =========================
# EMBEDDING
# =========================

class EmbeddingCreate(BaseModel):
    source_type: EmbeddingSourceType
    source_id: UUID
    metadata: Optional[Dict[str, Any]] = None


class EmbeddingOut(BaseModel):
    id: UUID
    source_type: EmbeddingSourceType
    source_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True



class OrderStatusUpdate(BaseModel):
    status: OrderStatus


class StoreInventoryItem(BaseModel):
    product_id: UUID
    product_name: str
    stock: int


class StoreInventoryOut(BaseModel):
    store_id: UUID
    store_name: str
    items: List[StoreInventoryItem]


class DeliveryAdminProduct(BaseModel):
    product_id: UUID
    name: str
    quantity: int
    price: float


class DeliveryAdminOut(BaseModel):
    delivery_id: UUID
    status: DeliveryStatus
    courier: Optional[str]
    tracking_id: Optional[str]

    order_id: UUID
    user_id: UUID
    total: float

    products: List[DeliveryAdminProduct]

    class Config:
        from_attributes = True
class AdminCatalogItem(BaseModel):
    product_id: UUID
    name: str
    price: float
    total_stock: int
    reserved_stock: int

class GlobalStockUpdate(BaseModel):
    product_id: UUID
    total_stock: int = Field(ge=0)
class OrderCancel(BaseModel):
    reason: Optional[str] = None
