# app/schema/enums.py
from enum import Enum


class OrderStatus(str, Enum):
    pending = "pending"
    paid = "paid"
    shipped = "shipped"
    delivered = "delivered"
    cancelled = "cancelled"


class PaymentStatus(str, Enum):
    initiated = "initiated"
    success = "success"
    failed = "failed"


class ComplaintStatus(str, Enum):
    open = "open"
    in_progress = "in_progress"
    resolved = "resolved"


class ConversationStatus(str, Enum):
    active = "active"
    closed = "closed"


class MessageRole(str, Enum):
    system = "system"
    user = "user"
    assistant = "assistant"


class RefundStatus(str, Enum):
    initiated = "initiated"
    approved = "approved"
    rejected = "rejected"
    completed = "completed"
class AgentActionStatus(str, Enum):
    pending = "pending"
    executed = "executed"
    failed = "failed"


class EmbeddingSourceType(str, Enum):
    product = "product"
    offer = "offer"
    policy = "policy"
    faq = "faq"
    order = "order"
class DeliveryStatus(str, Enum):
    pending = "pending"
    assigned = "assigned"
    out_for_delivery = "out_for_delivery"
    delivered = "delivered"
    failed = "failed"
    cancelled = "cancelled"