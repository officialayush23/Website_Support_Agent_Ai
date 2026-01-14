# app/models/models.py

from sqlalchemy import text
from sqlalchemy import (
    Column,
    String,
    Text,
    Boolean,
    Numeric,
    ForeignKey,
    TIMESTAMP,
    CheckConstraint,
    Integer,
)
from pgvector.sqlalchemy import Vector
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from sqlalchemy import Float
from uuid import uuid4
from app.core.database import Base
from app.models.enums import (
    order_status_enum,
    payment_status_enum,
    complaint_status_enum,
    complaint_created_by_enum,
    conversation_status_enum,
    message_role_enum,
    agent_action_status_enum,
    refund_status_enum,
    delivery_status_enum
)
from geoalchemy2 import Geography
from sqlalchemy import Time


class User(Base):
    __tablename__ = "users"

    id = Column(UUID, primary_key=True)
    name = Column(Text)
    role = Column(String, server_default="customer")
    preferences = Column(
        JSONB,
        server_default=text("'{}'::jsonb")
    )


    location = Column(
        Geography(geometry_type="POINT", srid=4326),
        nullable=True,
    )
    location_updated_at = Column(TIMESTAMP)
    created_at = Column(TIMESTAMP, server_default=func.now())


class GlobalInventory(Base):
    __tablename__ = "global_inventory"

    product_id = Column(UUID, ForeignKey("products.id", ondelete="CASCADE"), primary_key=True)
    total_stock = Column(Integer, nullable=False)
    reserved_stock = Column(Integer, nullable=False, default=0)
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

class Address(Base):
    __tablename__ = "addresses"

    id = Column(UUID, primary_key=True)
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

class Product(Base):
    __tablename__ = "products"

    id = Column(UUID, primary_key=True)
    name = Column(Text, nullable=False)
    description = Column(Text)
    category = Column(Text)
    price = Column(Numeric, nullable=False)
    attributes = Column(JSONB)
    is_active = Column(Boolean, server_default="true")
    created_at = Column(TIMESTAMP, server_default=func.now())

    images = relationship("ProductImage", back_populates="product")


class ProductImage(Base):
    __tablename__ = "product_images"

    id = Column(UUID, primary_key=True)
    product_id = Column(UUID, ForeignKey("products.id", ondelete="CASCADE"))
    image_url = Column(Text, nullable=False)
    is_primary = Column(Boolean, server_default="false")
    created_at = Column(TIMESTAMP, server_default=func.now())

    product = relationship("Product", back_populates="images")

class Store(Base):
    __tablename__ = "stores"

    id = Column(UUID, primary_key=True)
    name = Column(Text)
    city = Column(Text)
    state = Column(Text)

    location = Column(
        Geography(geometry_type="POINT", srid=4326),
        nullable=False,
    )

    is_active = Column(Boolean, server_default="true")

    inventory = relationship("Inventory", back_populates="store")
    working_hours = relationship("StoreWorkingHour", back_populates="store")

class Inventory(Base):
    __tablename__ = "inventory"

    store_id = Column(UUID, ForeignKey("stores.id", ondelete="CASCADE"), primary_key=True)
    product_id = Column(UUID, ForeignKey("products.id", ondelete="CASCADE"), primary_key=True)
    stock = Column(Integer, nullable=False, default=0)
    updated_at = Column(TIMESTAMP, server_default=func.now())

    store = relationship("Store", back_populates="inventory")
    product = relationship("Product")


class Cart(Base):
    __tablename__ = "carts"

    id = Column(UUID, primary_key=True)
    user_id = Column(UUID, ForeignKey("users.id", ondelete="CASCADE"))
    updated_at = Column(TIMESTAMP, server_default=func.now())

    items = relationship("CartItem", back_populates="cart", cascade="all, delete")


class CartItem(Base):
    __tablename__ = "cart_items"

    cart_id = Column(UUID, ForeignKey("carts.id", ondelete="CASCADE"), primary_key=True)
    product_id = Column(UUID, ForeignKey("products.id"), primary_key=True)
    quantity = Column(Integer, nullable=False)

    cart = relationship("Cart", back_populates="items")
    product = relationship("Product")
class Order(Base):
    __tablename__ = "orders"

    id = Column(UUID, primary_key=True)
    user_id = Column(UUID, ForeignKey("users.id"))
    address_id = Column(UUID, ForeignKey("addresses.id"))
    store_id = Column(UUID, ForeignKey("stores.id"), nullable=True)
    pickup = relationship("Pickup", back_populates="order", uselist=False)

    fulfillment_type = Column(String, server_default="delivery")
    status = Column(order_status_enum, nullable=False, server_default="pending")
    total = Column(Numeric, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())

    items = relationship("OrderItem", back_populates="order", cascade="all, delete")
    delivery = relationship("Delivery", back_populates="order", uselist=False)
    refunds = relationship("Refund", back_populates="order")


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(UUID, primary_key=True)
    order_id = Column(UUID, ForeignKey("orders.id", ondelete="CASCADE"))
    product_id = Column(UUID, ForeignKey("products.id"))
    quantity = Column(Integer)
    price = Column(Numeric)

    order = relationship("Order", back_populates="items")
    product = relationship("Product")


class Pickup(Base):
    __tablename__ = "pickups"

    id = Column(UUID, primary_key=True)
    order_id = Column(UUID, ForeignKey("orders.id", ondelete="CASCADE"))
    store_id = Column(UUID, ForeignKey("stores.id"))
    user_id = Column(UUID, ForeignKey("users.id"))
    
    order = relationship("Order", back_populates="pickup")  #

    amount = Column(Numeric, nullable=False)
    status = Column(String)  # ready | picked_up | cancelled
    picked_up_at = Column(TIMESTAMP)
class StoreWorkingHour(Base):
    __tablename__ = "store_working_hours"

    id = Column(UUID, primary_key=True)
    store_id = Column(UUID, ForeignKey("stores.id", ondelete="CASCADE"))

    day_of_week = Column(Integer)  # 0 = Sunday
    opens_at = Column(Time)
    closes_at = Column(Time)
    is_closed = Column(Boolean, server_default="false")

    store = relationship("Store", back_populates="working_hours")

class Payment(Base):
    __tablename__ = "payments"

    id = Column(UUID, primary_key=True)
    order_id = Column(UUID, ForeignKey("orders.id"))
    provider = Column(Text)
    status = Column(payment_status_enum, server_default="initiated")
    amount = Column(Numeric)
    created_at = Column(TIMESTAMP, server_default=func.now())


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(UUID, primary_key=True, default=uuid4)
    user_id = Column(UUID, ForeignKey("users.id"))
    status = Column(conversation_status_enum, server_default="active")
    handled_by = Column(String, server_default="llm")
    context = Column(
    JSONB,
    server_default=text("'{}'::jsonb")
)

    handed_off_at = Column(TIMESTAMP)
    handoff_reason = Column(String)
    ai_confidence = Column(Float)
    assigned_to = Column(UUID, ForeignKey("users.id"))

    last_message_at = Column(TIMESTAMP, server_default=func.now())
    created_at = Column(TIMESTAMP, server_default=func.now())


class Message(Base):
    __tablename__ = "messages"

    id = Column(UUID, primary_key=True)
    conversation_id = Column(UUID, ForeignKey("conversations.id", ondelete="CASCADE"))
    role = Column(message_role_enum, nullable=False)
    content = Column(Text)
    created_at = Column(TIMESTAMP, server_default=func.now())

class Complaint(Base):
    __tablename__ = "complaints"

    id = Column(UUID, primary_key=True)
    user_id = Column(UUID, ForeignKey("users.id"))
    order_id = Column(UUID, ForeignKey("orders.id"))
    description = Column(Text)
    status = Column(
    complaint_status_enum,
    server_default="open",
)
    created_by = Column(
    complaint_created_by_enum,
    server_default="agent",
)

    created_at = Column(TIMESTAMP, server_default=func.now())



class Meeting(Base):
    __tablename__ = "meetings"

    id = Column(UUID, primary_key=True)
    user_id = Column(UUID, ForeignKey("users.id"))
    scheduled_at = Column(TIMESTAMP)
    status = Column(Text)

class AgentAction(Base):
    __tablename__ = "agent_actions"

    id = Column(UUID, primary_key=True)
    conversation_id = Column(UUID, ForeignKey("conversations.id", ondelete="CASCADE"))
    action_type = Column(Text)
    payload = Column(JSONB)
    status = Column(agent_action_status_enum, server_default="executed")
    confidence = Column(Numeric)
    created_at = Column(TIMESTAMP, server_default=func.now())


class Embedding(Base):
    __tablename__ = "embeddings"

    id = Column(UUID, primary_key=True)
    source_type = Column(Text)
    source_id = Column(UUID)
    embedding = Column(Vector(768))
    meta = Column("metadata", JSONB)
    created_at = Column(TIMESTAMP, server_default=func.now())

class Offer(Base):
    __tablename__ = "offers"

    id = Column(UUID, primary_key=True)
    title = Column(Text)
    description = Column(Text)

    rules = Column(JSONB, nullable=False)

    priority = Column(Integer, default=0)
    stackable = Column(Boolean, default=False)

    starts_at = Column(TIMESTAMP)
    ends_at = Column(TIMESTAMP)

    is_active = Column(Boolean, default=True)

    created_by = Column(UUID, ForeignKey("users.id"))
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP)
class Refund(Base):
    __tablename__ = "refunds"

    id = Column(UUID, primary_key=True)
    order_id = Column(UUID, ForeignKey("orders.id"))
    reason = Column(Text)
    status = Column(refund_status_enum, server_default="initiated")
    created_at = Column(TIMESTAMP, server_default=func.now())

    order = relationship("Order", back_populates="refunds")



from app.models.enums import user_event_type_enum

class UserEvent(Base):
    __tablename__ = "user_events"

    id = Column(UUID, primary_key=True)
    user_id = Column(UUID, ForeignKey("users.id", ondelete="CASCADE"))
    event_type = Column(user_event_type_enum)
    product_id = Column(UUID, ForeignKey("products.id"))
    order_id = Column(UUID, ForeignKey("orders.id"))
    meta = Column("metadata", JSONB)
    created_at = Column(TIMESTAMP, server_default=func.now())

class UserPreference(Base):
    __tablename__ = "user_preferences"

    user_id = Column(UUID, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)

    preferred_categories = Column(
        JSONB,
        server_default=text("'{}'::jsonb")
    )
    preferred_price_range = Column(
        JSONB,
        server_default=text("'{}'::jsonb")
    )
    last_seen_products = Column(
        ARRAY(UUID),
        server_default=text("'{}'::uuid[]")
    )

    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())


from app.models.enums import delivery_status_enum
class Delivery(Base):
    __tablename__ = "deliveries"

    id = Column(UUID, primary_key=True)
    order_id = Column(UUID, ForeignKey("orders.id"))
    user_id = Column(UUID, ForeignKey("users.id"))
    address_id = Column(UUID, ForeignKey("addresses.id"))

    status = Column(delivery_status_enum, server_default="pending")
    courier = Column(String)
    tracking_id = Column(String)
    eta = Column(TIMESTAMP)
    created_at = Column(TIMESTAMP, server_default=func.now())

    order = relationship("Order", back_populates="delivery")
