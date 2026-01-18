# app/models/enums.py
from sqlalchemy import Enum

user_role_enum = Enum(
    "customer", "support", "admin","store_manager",
    name="user_role_enum",
    native_enum=True,
)

order_status_enum = Enum(
    "pending", "paid", "shipped", "delivered", "cancelled","completed",
    name="order_status_enum",
    native_enum=True,
)

fulfillment_type_enum = Enum(
    "delivery", "pickup",
    name="fulfillment_type_enum",
    native_enum=True,
)

fulfillment_source_enum = Enum(
    "global", "store",
    name="fulfillment_source_enum",
    native_enum=True,
)

payment_status_enum = Enum(
    "initiated", "pending", "success", "failed", "refunded",
    name="payment_status_enum",
    native_enum=True,
)


delivery_status_enum = Enum(
    "pending", "assigned", "out_for_delivery",
    "delivered", "failed", "cancelled",
    name="delivery_status_enum",
    native_enum=True,
)

pickup_status_enum = Enum(
    "ready", "picked_up", "cancelled",
    name="pickup_status_enum",
    native_enum=True,
)

complaint_status_enum = Enum(
    "open", "in_progress", "resolved",
    name="complaint_status_enum",
    native_enum=True,
)

refund_status_enum = Enum(
    "initiated", "approved", "rejected", "completed",
    name="refund_status_enum",
    native_enum=True,
)

conversation_status_enum = Enum(
    "active", "closed",
    name="conversation_status_enum",
    native_enum=True,
)

message_role_enum = Enum(
    "system", "user", "assistant",
    name="message_role_enum",
    native_enum=True,
)

agent_action_status_enum = Enum(
    "pending", "executed", "failed",
    name="agent_action_status_enum",
    native_enum=True,
)

user_event_type_enum = Enum(
    "view_product",
    "click_product",
    "search",
    "filter",
    "add_to_cart",
    "remove_from_cart",

    "checkout_started",
    "order_created",
    "payment_success",
    "payment_failed",
    "order_cancelled",
    "refund_requested",

    "complaint_created",
    "chat_message",

    name="user_event_type_enum",
    native_enum=True,
)


fulfillment_target_enum=Enum(
"global_inventory",
 "store_inventory",
 name="fulfillment_target_enum",
 native_enum = True,)

embedding_source_enum = Enum(
   "product",
  "variant",
  "offer",
  "chat_summary",
  "image",
  "user",
  name="embedding_source_enum",
  native_enum= True,
)