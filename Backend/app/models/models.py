from uuid import uuid4
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from geoalchemy2 import Geography
from pgvector.sqlalchemy import Vector
from sqlalchemy import JSON
from app.core.database import Base
from app.models.enums import *
from sqlalchemy import (
    Column, Text, Boolean, Numeric, ForeignKey,
    TIMESTAMP, Integer, String, Time, Index
)
from datetime import datetime



# ================= USERS =================

class User(Base):
    __tablename__ = "users"

    id = Column(UUID, primary_key=True)
    name = Column(Text)
    role = Column(user_role_enum, server_default="customer")
    preferences = Column(JSONB, server_default="'{}'::jsonb")

    location = Column(Geography("POINT", srid=4326))
    is_payment_agent_enabled = Column(Boolean, server_default="false")
    location_updated_at = Column(TIMESTAMP)

    created_at = Column(TIMESTAMP, server_default=func.now())

class UserPreference(Base):
    __tablename__ = "user_preferences"

    user_id = Column(
        UUID,
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    )

    preferred_categories = Column(JSONB, server_default="'[]'::jsonb")
    preferred_price_range = Column(JSONB, server_default="'{}'::jsonb")
    preferred_brands = Column(JSONB, server_default="'[]'::jsonb")

    last_updated_at = Column(TIMESTAMP, server_default=func.now())



# ================= ADDRESSES =================

class Address(Base):
    __tablename__ = "addresses"

    id = Column(UUID, primary_key=True, default=uuid4)
    user_id = Column(UUID, ForeignKey("users.id", ondelete="CASCADE"))

    label = Column(Text)
    address_line1 = Column(Text)
    address_line2 = Column(Text)
    city = Column(Text)
    state = Column(Text)
    pincode = Column(Text)
    country = Column(Text, server_default="India")

    is_default = Column(Boolean, server_default="false")
    created_at = Column(TIMESTAMP, server_default=func.now())


# ================= PRODUCTS =================

class Product(Base):
    __tablename__ = "products"

    id = Column(UUID, primary_key=True, default=uuid4)
    name = Column(Text, nullable=False)
    description = Column(Text)
    category = Column(Text)

    is_active = Column(Boolean, server_default="true")
    created_at = Column(TIMESTAMP, server_default=func.now())

    variants = relationship("ProductVariant", back_populates="product")


class ProductVariant(Base):
    __tablename__ = "product_variants"

    id = Column(UUID, primary_key=True, default=uuid4)
    product_id = Column(UUID, ForeignKey("products.id", ondelete="CASCADE"))

    sku = Column(Text, unique=True)
    price = Column(Numeric, nullable=False)
    attributes = Column(JSONB)

    created_at = Column(TIMESTAMP, server_default=func.now())

    product = relationship("Product", back_populates="variants")
    images = relationship("ProductImage", back_populates="variant")


class ProductImage(Base):
    __tablename__ = "product_images"

    id = Column(UUID, primary_key=True, default=uuid4)
    product_id = Column(UUID, ForeignKey("products.id", ondelete="CASCADE"))
    variant_id = Column(UUID, ForeignKey("product_variants.id", ondelete="CASCADE"))

    image_url = Column(Text, nullable=False)
    is_primary = Column(Boolean, server_default="false")
    created_at = Column(TIMESTAMP, server_default=func.now())

    variant = relationship("ProductVariant", back_populates="images")


# ================= INVENTORY =================

class GlobalInventory(Base):
    __tablename__ = "global_inventory"

    variant_id = Column(UUID, ForeignKey("product_variants.id", ondelete="CASCADE"), primary_key=True)
    total_stock = Column(Integer, nullable=False)
    allocated_stock = Column(Integer, nullable=False, server_default="0")
    reserved_stock = Column(Integer, nullable=False, server_default="0")

    updated_at = Column(TIMESTAMP, server_default=func.now())

class OrderStatusHistory(Base):
    __tablename__ = "order_status_history"

    id = Column(UUID, primary_key=True, default=uuid4)
    order_id = Column(UUID, ForeignKey("orders.id", ondelete="CASCADE"))
    status = Column(order_status_enum, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now()) 

    order = relationship("Order", back_populates="status_history")

class StoreInventory(Base):
    __tablename__ = "store_inventory"

    store_id = Column(UUID, ForeignKey("stores.id", ondelete="CASCADE"), primary_key=True)
    variant_id = Column(UUID, ForeignKey("product_variants.id", ondelete="CASCADE"), primary_key=True)

    allocated_stock = Column(Integer, nullable=False)
    in_hand_stock = Column(Integer, nullable=False)

    updated_at = Column(TIMESTAMP, server_default=func.now())


# ================= STORES =================

class Store(Base):
    __tablename__ = "stores"

    id = Column(UUID, primary_key=True, default=uuid4)
    name = Column(Text)
    city = Column(Text)
    state = Column(Text)

    location = Column(Geography("POINT", srid=4326))
    is_active = Column(Boolean, server_default="true")

    created_at = Column(TIMESTAMP, server_default=func.now())

    working_hours = relationship("StoreWorkingHour", back_populates="store")


class StoreWorkingHour(Base):
    __tablename__ = "store_working_hours"

    id = Column(UUID, primary_key=True, default=uuid4)
    store_id = Column(UUID, ForeignKey("stores.id", ondelete="CASCADE"))

    day_of_week = Column(Integer)
    opens_at = Column(Time)
    closes_at = Column(Time)
    is_closed = Column(Boolean, server_default="false")

    store = relationship("Store", back_populates="working_hours")


# ================= CART =================

class Cart(Base):
    __tablename__ = "carts"

    id = Column(UUID, primary_key=True, default=uuid4)
    user_id = Column(UUID, ForeignKey("users.id", ondelete="CASCADE"), unique=True)
    updated_at = Column(TIMESTAMP, server_default=func.now())


class CartItem(Base):
    __tablename__ = "cart_items"

    cart_id = Column(UUID, ForeignKey("carts.id", ondelete="CASCADE"), primary_key=True)
    variant_id = Column(UUID, ForeignKey("product_variants.id"), primary_key=True)
    quantity = Column(Integer, nullable=False)

    variant = relationship("ProductVariant")


# ================= ORDERS =================

class Order(Base):
    __tablename__ = "orders"

    id = Column(UUID, primary_key=True, default=uuid4)
    user_id = Column(UUID, ForeignKey("users.id"))
    address_id = Column(UUID, ForeignKey("addresses.id"))
    store_id = Column(UUID, ForeignKey("stores.id"))

    status = Column(order_status_enum, server_default="pending")
    fulfillment_type = Column(fulfillment_type_enum, server_default="delivery")
    status_history = relationship("OrderStatusHistory", back_populates="order", cascade="all, delete")

    subtotal = Column(Numeric)
    discount_total = Column(Numeric, server_default="0")
    total = Column(Numeric, nullable=False)

    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP)

    items = relationship("OrderItem", cascade="all, delete")


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(UUID, primary_key=True, default=uuid4)
    order_id = Column(UUID, ForeignKey("orders.id", ondelete="CASCADE"))
    variant_id = Column(UUID, ForeignKey("product_variants.id"))

    quantity = Column(Integer)
    price = Column(Numeric)

    fulfillment_source = Column(fulfillment_source_enum, nullable=False)
    fulfillment_ref_id = Column(UUID, nullable=False)

    variant = relationship("ProductVariant")


# ================= PAYMENTS =================

class Payment(Base):
    __tablename__ = "payments"

    id = Column(UUID, primary_key=True, default=uuid4)
    order_id = Column(UUID, ForeignKey("orders.id"))

    provider = Column(Text)
    amount = Column(Numeric)
    status = Column(payment_status_enum, server_default="initiated")

    created_at = Column(TIMESTAMP, server_default=func.now())

    __table_args__ = (
        Index(
            "one_successful_payment_per_order",
            "order_id",
            unique=True,
            postgresql_where=(status == "success"),
        ),
    )


# ================= DELIVERY / PICKUP =================

class Delivery(Base):
    __tablename__ = "deliveries"

    id = Column(UUID, primary_key=True, default=uuid4)
    order_id = Column(UUID, ForeignKey("orders.id"))
    user_id = Column(UUID, ForeignKey("users.id"))
    address_id = Column(UUID, ForeignKey("addresses.id"))

    status = Column(delivery_status_enum, server_default="pending")
    eta = Column(TIMESTAMP)

    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP)

    order = relationship("Order")


class Pickup(Base):
    __tablename__ = "pickups"

    id = Column(UUID, primary_key=True, default=uuid4)
    order_id = Column(UUID, ForeignKey("orders.id"))
    store_id = Column(UUID, ForeignKey("stores.id"))
    user_id = Column(UUID, ForeignKey("users.id"))

    amount = Column(Numeric)
    status = Column(pickup_status_enum, server_default="ready")
    picked_up_at = Column(TIMESTAMP)

    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP)

    order = relationship("Order")

# ================= OFFERS =================

class Offer(Base):
    __tablename__ = "offers"

    id = Column(UUID, primary_key=True, default=uuid4)

    title = Column(Text, nullable=False)
    description = Column(Text)

    min_cart_value = Column(Numeric, server_default="0")
    percentage_off = Column(Numeric)
    amount_off = Column(Numeric)
    max_discount = Column(Numeric)

    priority = Column(Integer, server_default="0")
    stackable = Column(Boolean, server_default="false")

    starts_at = Column(TIMESTAMP, nullable=False)
    ends_at = Column(TIMESTAMP, nullable=False)
    is_active = Column(Boolean, server_default="true")

    created_by = Column(UUID, ForeignKey("users.id"))
    event_metadata = Column("metadata", JSON, nullable=True)

    created_at = Column(TIMESTAMP, server_default=func.now())


# ================= COMPLAINTS / REFUNDS =================

class Complaint(Base):
    __tablename__ = "complaints"

    id = Column(UUID, primary_key=True, default=uuid4)
    user_id = Column(UUID, ForeignKey("users.id"))
    order_id = Column(UUID, ForeignKey("orders.id"))

    description = Column(Text)
    status = Column(complaint_status_enum, server_default="open")

    created_at = Column(TIMESTAMP, server_default=func.now())


class Refund(Base):
    __tablename__ = "refunds"

    id = Column(UUID, primary_key=True, default=uuid4)
    order_id = Column(UUID, ForeignKey("orders.id"))

    reason = Column(Text)
    status = Column(refund_status_enum, server_default="initiated")

    created_at = Column(TIMESTAMP, server_default=func.now())


# ================= CHAT =================

class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id = Column(UUID, primary_key=True, default=uuid4)
    user_id = Column(UUID, ForeignKey("users.id", ondelete="CASCADE"))
    title = Column(Text)
    is_active = Column(Boolean, server_default="true")
    created_at = Column(TIMESTAMP, server_default=func.now())
    last_activity_at = Column(TIMESTAMP, server_default=func.now())

    # Relationships
    conversations = relationship("Conversation", back_populates="chat_session")
    contexts = relationship("ChatContext", back_populates="chat_session")


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(UUID, primary_key=True, default=uuid4)
    # [NEW] Link to Session
    chat_session_id = Column(UUID, ForeignKey("chat_sessions.id", ondelete="CASCADE"))
    user_id = Column(UUID, ForeignKey("users.id"))
    
    status = Column(Text, server_default="active") # or Enum if you use it
    
    # [NEW] Handoff Fields
    handled_by = Column(Text, server_default="llm") # 'llm' or 'human'
    assigned_to = Column(UUID, ForeignKey("users.id")) # Support agent ID
    handed_off_at = Column(TIMESTAMP)
    handoff_reason = Column(Text)
    ai_confidence = Column(Numeric)

    created_at = Column(TIMESTAMP, server_default=func.now())
    last_message_at = Column(TIMESTAMP, server_default=func.now())

    # Relationships
    chat_session = relationship("ChatSession", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation")


class Message(Base):
    __tablename__ = "messages"
    
    id = Column(UUID, primary_key=True, default=uuid4)
    conversation_id = Column(UUID, ForeignKey("conversations.id", ondelete="CASCADE"))
    # [NEW] Direct link for easier history fetching
    chat_session_id = Column(UUID, ForeignKey("chat_sessions.id", ondelete="CASCADE"))
    
    role = Column(Text) # 'user', 'assistant', 'system'
    content = Column(Text)
    created_at = Column(TIMESTAMP, server_default=func.now())

    conversation = relationship("Conversation", back_populates="messages")

class ChatContext(Base):
    __tablename__ = "chat_contexts"

    id = Column(UUID, primary_key=True, default=uuid4)
    chat_session_id = Column(UUID, ForeignKey("chat_sessions.id", ondelete="CASCADE"))
    conversation_id = Column(UUID, ForeignKey("conversations.id", ondelete="CASCADE"))
    
    summary = Column(Text, nullable=False)
    token_count = Column(Integer)
    confidence = Column(Numeric)
    created_at = Column(TIMESTAMP, server_default=func.now())

    chat_session = relationship("ChatSession", back_populates="contexts")


# ================= EMBEDDINGS =================

class Embedding(Base):
    __tablename__ = "embeddings"

    id = Column(UUID, primary_key=True, default=uuid4)
    source_type = Column(Text)
    source_id = Column(UUID)

    embedding = Column(Vector(768))
    event_metadata = Column("metadata", JSON, nullable=True)

    created_at = Column(TIMESTAMP, server_default=func.now())


# ================= ANALYTICS =================

class UserEvent(Base):
    __tablename__ = "user_events"

    id = Column(UUID, primary_key=True, default=uuid4)
    user_id = Column(UUID, ForeignKey("users.id", ondelete="CASCADE"))

    event_type = Column(user_event_type_enum, nullable=False)

    product_id = Column(UUID, ForeignKey("products.id"))
    variant_id = Column(UUID, ForeignKey("product_variants.id"))
    order_id = Column(UUID, ForeignKey("orders.id"))

    event_metadata = Column("metadata", JSON, nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now())


class AgentAction(Base):
    __tablename__ = "agent_actions"

    id = Column(UUID, primary_key=True, default=uuid4)
    conversation_id = Column(UUID, ForeignKey("conversations.id"))
    action_type = Column(Text)
    payload = Column(JSONB)
    status = Column(agent_action_status_enum, server_default="executed")
    confidence = Column(Numeric)
    created_at = Column(TIMESTAMP, server_default=func.now())


class Lead(Base):
    __tablename__ = "leads"

    id = Column(UUID, primary_key=True, default=uuid4)
    email = Column(Text, nullable=False)
    requirements = Column(Text)
    status = Column(Text, server_default="new")
    created_at = Column(TIMESTAMP, server_default=func.now())


class AttributeDefinition(Base):
    __tablename__ = "attribute_definitions"

    id = Column(UUID, primary_key=True, default=uuid4)

    name = Column(String, nullable=False, unique=True)
    description = Column(Text)

    # simple typing for now (extensible later)
    value_type = Column(
        String,
        nullable=False,
        server_default="string",  # string | number | enum
    )

    # enum-style allowed values
    allowed_values = Column(JSONB)  # ["S", "M", "L"]

    is_required = Column(Boolean, server_default="false")
    is_active = Column(Boolean, server_default="true")

    created_at = Column(TIMESTAMP, server_default=func.now())
from app.models.enums import fulfillment_target_enum


class InventoryMovement(Base):
    __tablename__ = "inventory_movements"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)

    variant_id = Column(
        UUID(as_uuid=True),
        ForeignKey("product_variants.id", ondelete="CASCADE"),
        nullable=False,
    )

    source = Column(
        fulfillment_target_enum,
        nullable=True,
    )

    destination = Column(
        fulfillment_target_enum,
        nullable=True,
    )

    quantity = Column(Integer, nullable=False)

    reason = Column(Text, nullable=False)

    reference_type = Column(Text, nullable=True)
    reference_id = Column(UUID(as_uuid=True), nullable=True)

    created_at = Column(
        default=datetime.utcnow,
        nullable=False,
    )