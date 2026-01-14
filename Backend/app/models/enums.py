# app/models/enums.py
from sqlalchemy import Enum

order_status_enum = Enum(
    "pending",
    "paid",
    "shipped",
    "delivered",
    "cancelled",
    name="order_status_enum",
    native_enum=True,
)

payment_status_enum = Enum(
    "initiated",
    "success",
    "failed",
    name="payment_status_enum",
    native_enum=True,
)

complaint_status_enum = Enum(
    "open",
    "in_progress",
    "resolved",
    name="complaint_status_enum",
    native_enum=True,
)

conversation_status_enum = Enum(
    "active",
    "closed",
    name="conversation_status_enum",
    native_enum=True,
)

message_role_enum = Enum(
    "system",
    "user",
    "assistant",
    name="message_role_enum",
    native_enum=True,
)

agent_action_status_enum = Enum(
    "pending",
    "executed",
    "failed",
    name="agent_action_status_enum",
    native_enum=True,
)

complaint_created_by_enum = Enum(
    "user",
    "agent",
    "support",
    name="complaint_created_by_enum",
    native_enum=True,
)


refund_status_enum = Enum(
    "initiated",
    "approved",
    "rejected",
    "completed",
    name="refund_status_enum",
    native_enum=True,   
)

user_event_type_enum = Enum(  
  'view_product',
  'click_product',
  'search',
  'filter',
  'add_to_cart',
  'remove_from_cart',
  'order_created',
  'payment_success',
  'complaint_created',
 name ="user_event_type_enum",
    native_enum=True,
)

delivery_status_enum = Enum(
    "pending",
    "assigned",
    "out_for_delivery",
    "delivered",
    "failed",
    "cancelled",
    name="delivery_status_enum",
    native_enum=True,
)