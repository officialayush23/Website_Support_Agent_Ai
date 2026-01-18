from uuid import uuid4
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy import DateTime
from sqlalchemy.dialects.postgresql import ARRAY

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
    location_updated_at = Column(TIMESTAMP)

    is_payment_agent_enabled = Column(Boolean, server_default="false")
    created_at = Column(TIMESTAMP, server_default=func.now())

class UserPreference(Base):
    __tablename__ = "user_preferences"

    user_id = Column(UUID, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    preferred_categories = Column(JSONB, server_default="'{}'::jsonb")
    preferred_price_range = Column(JSONB, server_default="'{}'::jsonb")
    preferred_brands = Column(JSONB, server_default="'{}'::jsonb")

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

    price = Column(Numeric, nullable=False)
    rating = Column(Numeric, server_default="0")
    reviews = Column(Text)
    images = Column(ARRAY(Text), server_default="{}")

    is_active = Column(Boolean, server_default="true")
    created_at = Column(TIMESTAMP, server_default=func.now())




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

    product_id = Column(
        UUID,
        ForeignKey("products.id", ondelete="CASCADE"),
        primary_key=True,
    )

    total_stock = Column(Integer, nullable=False, server_default="0")
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

    store_id = Column(
        UUID,
        ForeignKey("stores.id", ondelete="CASCADE"),
        primary_key=True,
    )
    product_id = Column(
        UUID,
        ForeignKey("products.id", ondelete="CASCADE"),
        primary_key=True,
    )

    allocated_stock = Column(Integer, nullable=False, server_default="0")
    in_hand_stock = Column(Integer, nullable=False, server_default="0")

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

    cart_id = Column(
        UUID,
        ForeignKey("carts.id", ondelete="CASCADE"),
        primary_key=True,
    )
    product_id = Column(
        UUID,
        ForeignKey("products.id"),
        primary_key=True,
    )

    quantity = Column(Integer, nullable=False)


# ================= ORDERS =================
class Order(Base):
    __tablename__ = "orders"

    id = Column(UUID, primary_key=True, default=uuid4)
    user_id = Column(UUID, ForeignKey("users.id"))
    address_id = Column(UUID, ForeignKey("addresses.id"))
    store_id = Column(UUID, ForeignKey("stores.id"))

    fulfillment_type = Column(fulfillment_type_enum, server_default="delivery")

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
    product_id = Column(UUID, ForeignKey("products.id"))

    quantity = Column(Integer, nullable=False)
    price = Column(Numeric, nullable=False)



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
    Column(embedding_source_enum, nullable=False)
    source_id = Column(UUID)

    embedding = Column(Vector(768))
    event_metadata = Column("metadata", JSON, nullable=True)

    created_at = Column(TIMESTAMP, server_default=func.now())


# ================= ANALYTICS =================

class UserEvent(Base):
    __tablename__ = "user_events"

    id = Column(UUID, primary_key=True, default=uuid4)
    user_id = Column(UUID, ForeignKey("users.id", ondelete="CASCADE"))

    event_type = Column(Text, nullable=False)

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

    id = Column(UUID(as_uuid=True), primary_key=True)
    name = Column(String, nullable=False)

    input_type = Column(String, nullable=False)   # ← was value_type
    allowed_values = Column(ARRAY(String), nullable=True)

    is_required = Column(Boolean, default=False)
    applies_to = Column(String, default="variant")

    created_at = Column(DateTime, server_default=func.now())

from app.models.enums import fulfillment_target_enum

class InventoryMovement(Base):
    __tablename__ = "inventory_movements"

    id = Column(UUID, primary_key=True, default=uuid4)
    product_id = Column(UUID, ForeignKey("products.id"), nullable=False)

    source = Column(Text)
    destination = Column(Text)

    quantity = Column(Integer, nullable=False)
    reason = Column(Text)

    reference_type = Column(Text)
    reference_id = Column(UUID)

    created_at = Column(TIMESTAMP, server_default=func.now())
