# app/models/models.py

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
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(UUID, primary_key=True)
    name = Column(Text)
    role = Column(String)
    preferences = Column(JSONB)
    created_at = Column(TIMESTAMP, server_default=func.now())


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
    country = Column(Text)
    is_default = Column(Boolean)
    created_at = Column(TIMESTAMP, server_default=func.now())


class Product(Base):
    __tablename__ = "products"

    id = Column(UUID, primary_key=True)
    name = Column(Text, nullable=False)
    description = Column(Text)
    category = Column(Text)
    price = Column(Numeric, nullable=False)
    attributes = Column(JSONB)
    is_active = Column(Boolean)
    created_at = Column(TIMESTAMP, server_default=func.now())


class ProductImage(Base):
    __tablename__ = "product_images"

    id = Column(UUID, primary_key=True)
    product_id = Column(UUID, ForeignKey("products.id", ondelete="CASCADE"))
    image_url = Column(Text, nullable=False)
    is_primary = Column(Boolean)
    created_at = Column(TIMESTAMP, server_default=func.now())


class Store(Base):
    __tablename__ = "stores"

    id = Column(UUID, primary_key=True)
    name = Column(Text)
    city = Column(Text)
    state = Column(Text)
    latitude = Column(Numeric)
    longitude = Column(Numeric)
    is_active = Column(Boolean)


class Inventory(Base):
    __tablename__ = "inventory"

    store_id = Column(UUID, ForeignKey("stores.id", ondelete="CASCADE"), primary_key=True)
    product_id = Column(
        UUID, ForeignKey("products.id", ondelete="CASCADE"), primary_key=True
    )
    stock = Column(Integer)
    updated_at = Column(TIMESTAMP, server_default=func.now())


class Cart(Base):
    __tablename__ = "carts"

    id = Column(UUID, primary_key=True)
    user_id = Column(UUID, ForeignKey("users.id", ondelete="CASCADE"))
    updated_at = Column(TIMESTAMP, server_default=func.now())


class CartItem(Base):
    __tablename__ = "cart_items"

    cart_id = Column(
        UUID, ForeignKey("carts.id", ondelete="CASCADE"), primary_key=True
    )
    product_id = Column(UUID, ForeignKey("products.id"), primary_key=True)
    quantity = Column(Integer)


class Order(Base):
    __tablename__ = "orders"

    id = Column(UUID, primary_key=True)
    user_id = Column(UUID, ForeignKey("users.id"))
    address_id = Column(UUID, ForeignKey("addresses.id"))
    status = Column(String)
    total = Column(Numeric)
    created_at = Column(TIMESTAMP, server_default=func.now())


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(UUID, primary_key=True)
    order_id = Column(UUID, ForeignKey("orders.id", ondelete="CASCADE"))
    product_id = Column(UUID, ForeignKey("products.id"))
    quantity = Column(Integer)
    price = Column(Numeric)


class Payment(Base):
    __tablename__ = "payments"

    id = Column(UUID, primary_key=True)
    order_id = Column(UUID, ForeignKey("orders.id"))
    provider = Column(Text)
    status = Column(Text)
    amount = Column(Numeric)
    created_at = Column(TIMESTAMP, server_default=func.now())


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(UUID, primary_key=True)
    user_id = Column(UUID, ForeignKey("users.id"))
    status = Column(Text)
    context = Column(JSONB)
    last_message_at = Column(TIMESTAMP, server_default=func.now())
    created_at = Column(TIMESTAMP, server_default=func.now())


class Message(Base):
    __tablename__ = "messages"

    id = Column(UUID, primary_key=True)
    conversation_id = Column(
        UUID, ForeignKey("conversations.id", ondelete="CASCADE")
    )
    role = Column(Text)
    content = Column(Text)
    created_at = Column(TIMESTAMP, server_default=func.now())


class Complaint(Base):
    __tablename__ = "complaints"

    id = Column(UUID, primary_key=True)
    user_id = Column(UUID, ForeignKey("users.id"))
    order_id = Column(UUID, ForeignKey("orders.id"))
    description = Column(Text)
    status = Column(Text)
    created_by = Column(Text)
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
    conversation_id = Column(
        UUID, ForeignKey("conversations.id", ondelete="CASCADE")
    )
    action_type = Column(Text)
    payload = Column(JSONB)
    status = Column(Text)
    created_at = Column(TIMESTAMP, server_default=func.now())


class Embedding(Base):
    __tablename__ = "embeddings"

    id = Column(UUID, primary_key=True)
    source_type = Column(Text)
    source_id = Column(UUID)
    embedding = Column(Text)  # pgvector handled at DB level
    metadata = Column(JSONB)
    created_at = Column(TIMESTAMP, server_default=func.now())
