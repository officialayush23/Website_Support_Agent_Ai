# app/models/py_enums.py
# app/models/py_enums.py
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

class UserEventType(str, Enum):
    view_product = "view_product"
    click_product = "click_product"
    search = "search"
    filter = "filter"
    add_to_cart = "add_to_cart"
    remove_from_cart = "remove_from_cart"
    order_created = "order_created"
    payment_success = "payment_success"
    complaint_created = "complaint_created"

class DeliveryStatus(str, Enum):
    pending = "pending"
    assigned = "assigned"
    out_for_delivery = "out_for_delivery"
    delivered = "delivered"
    failed = "failed"
    cancelled = "cancelled"
