# app/llm/tool_schema.py
# app/llm/tool_schema.py
from google.genai.types import FunctionDeclaration, Schema, Type

TOOLS = [

    # ===== PRODUCTS =====
    FunctionDeclaration(
        name="list_products",
        description="List all active products",
        parameters=Schema(type=Type.OBJECT, properties={}, required=[]),
    ),

    FunctionDeclaration(
        name="view_product",
        description="View product details",
        parameters=Schema(
            type=Type.OBJECT,
            properties={"product_id": Schema(type=Type.STRING)},
            required=["product_id"],
        ),
    ),

    FunctionDeclaration(
        name="recommend_products",
        description="Recommend products for the user",
        parameters=Schema(type=Type.OBJECT, properties={}, required=[]),
    ),

    # ===== CART =====
    FunctionDeclaration(
        name="view_cart",
        description="View cart with totals",
        parameters=Schema(type=Type.OBJECT, properties={}, required=[]),
    ),

    FunctionDeclaration(
        name="add_to_cart",
        description="Add variant to cart",
        parameters=Schema(
            type=Type.OBJECT,
            properties={
                "variant_id": Schema(type=Type.STRING),
                "quantity": Schema(type=Type.INTEGER),
            },
            required=["variant_id", "quantity"],
        ),
    ),

    FunctionDeclaration(
        name="remove_from_cart",
        description="Remove variant from cart",
        parameters=Schema(
            type=Type.OBJECT,
            properties={"variant_id": Schema(type=Type.STRING)},
            required=["variant_id"],
        ),
    ),

    # ===== ORDERS =====
    FunctionDeclaration(
        name="create_order",
        description="Checkout cart",
        parameters=Schema(
            type=Type.OBJECT,
            properties={
                "address_id": Schema(type=Type.STRING),
                "fulfillment_type": Schema(type=Type.STRING),
                "store_id": Schema(type=Type.STRING),
            },
            required=["fulfillment_type"],

        ),
    ),

    FunctionDeclaration(
        name="cancel_order",
        description="Cancel order",
        parameters=Schema(
            type=Type.OBJECT,
            properties={"order_id": Schema(type=Type.STRING)},
            required=["order_id"],
        ),
    ),

    FunctionDeclaration(
        name="order_timeline",
        description="Order timeline",
        parameters=Schema(
            type=Type.OBJECT,
            properties={"order_id": Schema(type=Type.STRING)},
            required=["order_id"],
        ),
    ),

    # ===== DELIVERY =====
    FunctionDeclaration(
        name="get_delivery_status",
        description="Get delivery status",
        parameters=Schema(
            type=Type.OBJECT,
            properties={"order_id": Schema(type=Type.STRING)},
            required=["order_id"],
        ),
    ),

    # ===== ADDRESSES =====
    FunctionDeclaration(
        name="list_addresses",
        description="List addresses",
        parameters=Schema(type=Type.OBJECT, properties={}, required=[]),
    ),

    FunctionDeclaration(
        name="add_address",
        description="Add address",
        parameters=Schema(
            type=Type.OBJECT,
            properties={"data": Schema(type=Type.OBJECT)},
            required=["data"],
        ),
    ),

    FunctionDeclaration(
        name="delete_address",
        description="Delete address",
        parameters=Schema(
            type=Type.OBJECT,
            properties={"address_id": Schema(type=Type.STRING)},
            required=["address_id"],
        ),
    ),

    FunctionDeclaration(
        name="set_default_address",
        description="Set default address",
        parameters=Schema(
            type=Type.OBJECT,
            properties={"address_id": Schema(type=Type.STRING)},
            required=["address_id"],
        ),
    ),

    # ===== COMPLAINTS =====
    FunctionDeclaration(
        name="raise_complaint",
        description="Raise complaint",
        parameters=Schema(
            type=Type.OBJECT,
            properties={
                "order_id": Schema(type=Type.STRING),
                "description": Schema(type=Type.STRING),
            },
            required=["order_id", "description"],
        ),
    ),

    # ===== REFUNDS =====
    FunctionDeclaration(
        name="request_refund",
        description="Request refund",
        parameters=Schema(
            type=Type.OBJECT,
            properties={
                "order_id": Schema(type=Type.STRING),
                "reason": Schema(type=Type.STRING),
            },
            required=["order_id", "reason"],
        ),
    ),

    # ===== USER =====
    FunctionDeclaration(
        name="get_user_preferences",
        description="Get user preferences",
        parameters=Schema(type=Type.OBJECT, properties={}, required=[]),
    ),

    FunctionDeclaration(
        name="update_user_profile",
        description="Update user name",
        parameters=Schema(
            type=Type.OBJECT,
            properties={"name": Schema(type=Type.STRING)},
            required=[],
        ),
    ),
]
