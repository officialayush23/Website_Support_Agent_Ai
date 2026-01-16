# app/schema/enums.py

from enum import Enum

class OrderStatus(str, Enum):
    pending = "pending"
    paid = "paid"
    shipped = "shipped"
    delivered = "delivered"
    completed = "completed"
    cancelled = "cancelled"
class PickupStatus(str, Enum):
    ready = "ready"
    picked_up = "picked_up"
    cancelled = "cancelled"


class PaymentStatus(str, Enum):
    initiated = "initiated"
    pending = "pending"
    success = "success"
    failed = "failed"
    refunded = "refunded"



class ComplaintStatus(str, Enum):
    open = "open"
    in_progress = "in_progress"
    resolved = "resolved"


class RefundStatus(str, Enum):
    initiated = "initiated"
    approved = "approved"
    rejected = "rejected"
    completed = "completed"

class ConversationStatus(str, Enum):
    active = "active"
    closed = "closed"

class DeliveryStatus(str, Enum):
    pending = "pending"
    assigned = "assigned"
    out_for_delivery = "out_for_delivery"
    delivered = "delivered"
    failed = "failed"
    cancelled = "cancelled"


class FulfillmentType(str, Enum):
    delivery = "delivery"
    pickup = "pickup"


class FulfillmentSource(str, Enum):
    global_ = "global"   # Python-safe, maps to DB enum
    store = "store"


class MessageRole(str, Enum):
    system = "system"
    user = "user"
    assistant = "assistant"

class UserEventType(str, Enum):
    view_product = "view_product"
    click_product = "click_product"
    search = "search"
    filter = "filter"
    add_to_cart = "add_to_cart"
    remove_from_cart = "remove_from_cart"

    checkout_started = "checkout_started"
    order_created = "order_created"
    payment_success = "payment_success"
    payment_failed = "payment_failed"
    order_cancelled = "order_cancelled"
    refund_requested = "refund_requested"

    complaint_created = "complaint_created"
    chat_message = "chat_message"
