# app/schema/schemas.py

from pydantic import BaseModel, Field,model_validator
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime
from app.schema.enums import ConversationStatus, EmbeddingSourceType, OrderStatus, ComplaintStatus,PaymentStatus, MessageRole, RefundStatus
from decimal import Decimal
class UserOut(BaseModel):
    id: UUID
    name: Optional[str]
    role: str

    class Config:
        from_attributes = True
class AddressCreate(BaseModel):
    label: str
    address_line1: str
    address_line2: Optional[str]
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
class ProductCreate(BaseModel):
    name: str
    description: Optional[str]
    category: Optional[str]
    price: float
    attributes: Optional[Dict[str, Any]]  # size, color, fabric, fit


class ProductUpdate(BaseModel):
    name: Optional[str]
    description: Optional[str]
    category: Optional[str]
    price: Optional[float]
    attributes: Optional[Dict[str, Any]]
    is_active: Optional[bool]


class ProductOut(ProductCreate):
    id: UUID
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True
class ProductImageCreate(BaseModel):
    image_url: str
    is_primary: bool = False


class ProductImageOut(ProductImageCreate):
    id: UUID
    product_id: UUID
    created_at: datetime

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
class CartItemCreate(BaseModel):
    product_id: UUID
    quantity: int = Field(gt=0)


class CartItemUpdate(BaseModel):
    quantity: int = Field(gt=0)


class CartItemOut(BaseModel):
    product_id: UUID
    quantity: int

    class Config:
        from_attributes = True
class OrderCreate(BaseModel):
    address_id: UUID


class OrderOut(BaseModel):
    id: UUID
    status: OrderStatus
    total: Decimal
    created_at: datetime

    class Config:
        from_attributes = True


class DeliveryUpdate(BaseModel):
    status: OrderStatus

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

class RefundCreate(BaseModel):
    order_id: UUID
    reason: str


class RefundOut(BaseModel):
    id: UUID
    order_id: UUID
    status: RefundStatus
    created_at: datetime

    class Config:
        from_attributes = True
class OfferCreate(BaseModel):
    title: str
    description: Optional[str] = None
    rules: Dict[str, Any]          # discount logic JSON
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
    title: Optional[str]
    description: Optional[str]
    rules: Optional[Dict[str, Any]]
    priority: Optional[int]
    stackable: Optional[bool]
    starts_at: Optional[datetime]
    ends_at: Optional[datetime]
    is_active: Optional[bool]
    @model_validator(mode="after")
    def validate_dates(self):
        if self.starts_at >= self.ends_at:
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

class EmbeddingCreate(BaseModel):
    source_type: EmbeddingSourceType
   # product | offer | faq | policy | order
    source_id: UUID
    metadata: Optional[Dict[str, Any]]


class EmbeddingOut(BaseModel):
    id: UUID
    source_type: EmbeddingSourceType

    source_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True



class RefundCreate(BaseModel):
    order_id: UUID
    reason: str


class RefundOut(BaseModel):
    id: UUID
    order_id: UUID
    status: RefundStatus
    created_at: datetime

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


class InventoryUpdate(BaseModel):
    store_id: UUID
    product_id: UUID
    stock: int = Field(ge=0)


from app.schema.enums import DeliveryStatus

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
