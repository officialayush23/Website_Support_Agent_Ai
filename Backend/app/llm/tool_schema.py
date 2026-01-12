# app/llm/tool_schema.py
from google.genai.types import FunctionDeclaration, Schema, Type

TOOLS = [

    # ---------- PRODUCTS ----------
    FunctionDeclaration(
        name="list_products",
        description="List all active products",
        parameters=Schema(
            type=Type.OBJECT,
            properties={},
            required=[]
        ),
    ),

    FunctionDeclaration(
        name="view_product",
        description="View a product by ID",
        parameters=Schema(
            type=Type.OBJECT,
            properties={
                "product_id": Schema(type=Type.STRING),
            },
            required=["product_id"],
        ),
    ),

    FunctionDeclaration(
        name="recommend_products",
        description="Recommend products for the user based on activity",
        parameters=Schema(
            type=Type.OBJECT,
            properties={},
            required=[]
        ),
    ),

    # ---------- CART ----------
    FunctionDeclaration(
        name="add_to_cart",
        description="Add a product to cart",
        parameters=Schema(
            type=Type.OBJECT,
            properties={
                "product_id": Schema(type=Type.STRING),
                "quantity": Schema(type=Type.INTEGER),
            },
            required=["product_id", "quantity"],
        ),
    ),

    FunctionDeclaration(
        name="remove_from_cart",
        description="Remove a product from cart",
        parameters=Schema(
            type=Type.OBJECT,
            properties={
                "product_id": Schema(type=Type.STRING),
            },
            required=["product_id"],
        ),
    ),

    FunctionDeclaration(
        name="view_cart",
        description="View current cart items",
        parameters=Schema(
            type=Type.OBJECT,
            properties={},
            required=[]
        ),
    ),

    # ---------- ADDRESSES ----------
    FunctionDeclaration(
        name="list_addresses",
        description="List user addresses",
        parameters=Schema(
            type=Type.OBJECT,
            properties={},
            required=[]
        ),
    ),

    FunctionDeclaration(
        name="add_address",
        description="Add a new address",
        parameters=Schema(
            type=Type.OBJECT,
            properties={
                "data": Schema(type=Type.OBJECT),
            },
            required=["data"],
        ),
    ),

    FunctionDeclaration(
        name="delete_address",
        description="Delete an address",
        parameters=Schema(
            type=Type.OBJECT,
            properties={
                "address_id": Schema(type=Type.STRING),
            },
            required=["address_id"],
        ),
    ),

    FunctionDeclaration(
        name="set_default_address",
        description="Set default delivery address",
        parameters=Schema(
            type=Type.OBJECT,
            properties={
                "address_id": Schema(type=Type.STRING),
            },
            required=["address_id"],
        ),
    ),

    # ---------- ORDERS ----------
    FunctionDeclaration(
        name="create_order",
        description="Create an order using cart and address",
        parameters=Schema(
            type=Type.OBJECT,
            properties={
                "address_id": Schema(type=Type.STRING),
            },
            required=["address_id"],
        ),
    ),

    FunctionDeclaration(
        name="get_delivery_status",
        description="Get delivery status of an order",
        parameters=Schema(
            type=Type.OBJECT,
            properties={
                "order_id": Schema(type=Type.STRING),
            },
            required=["order_id"],
        ),
    ),

    # ---------- COMPLAINTS ----------
    FunctionDeclaration(
        name="raise_complaint",
        description="Raise a complaint for an order",
        parameters=Schema(
            type=Type.OBJECT,
            properties={
                "order_id": Schema(type=Type.STRING),
                "description": Schema(type=Type.STRING),
            },
            required=["order_id", "description"],
        ),
    ),

    FunctionDeclaration(
        name="complaint_status",
        description="Get complaint status",
        parameters=Schema(
            type=Type.OBJECT,
            properties={
                "complaint_id": Schema(type=Type.STRING),
            },
            required=["complaint_id"],
        ),
    ),

    # ---------- REFUNDS ----------
    FunctionDeclaration(
        name="request_refund",
        description="Request a refund for an order",
        parameters=Schema(
            type=Type.OBJECT,
            properties={
                "order_id": Schema(type=Type.STRING),
                "reason": Schema(type=Type.STRING),
            },
            required=["order_id", "reason"],
        ),
    ),

    FunctionDeclaration(
        name="refund_status",
        description="Get refund status",
        parameters=Schema(
            type=Type.OBJECT,
            properties={
                "refund_id": Schema(type=Type.STRING),
            },
            required=["refund_id"],
        ),
    ),

    # ---------- USER PREFERENCES ----------
    FunctionDeclaration(
        name="get_user_preferences",
        description="Get user preference summary",
        parameters=Schema(
            type=Type.OBJECT,
            properties={},
            required=[]
        ),
    ),

    FunctionDeclaration(
        name="update_user_preferences",
        description="Update user preferences",
        parameters=Schema(
            type=Type.OBJECT,
            properties={
                "prefs": Schema(type=Type.OBJECT),
            },
            required=["prefs"],
        ),
    ),
]

# ---------- DELIVERY ----------

FunctionDeclaration(
    name="get_delivery_status",
    description="Get delivery status for an order",
    parameters=Schema(
        type=Type.OBJECT,
        properties={
            "order_id": Schema(type=Type.STRING),
        },
        required=["order_id"],
    ),
),

FunctionDeclaration(
    name="update_delivery",
    description="Update delivery status (admin/support only)",
    parameters=Schema(
        type=Type.OBJECT,
        properties={
            "delivery_id": Schema(type=Type.STRING),
            "status": Schema(
                type=Type.STRING,
                description="pending | assigned | out_for_delivery | delivered | failed | cancelled"
            ),
            "courier": Schema(type=Type.STRING),
            "tracking_id": Schema(type=Type.STRING),
        },
        required=["delivery_id", "status"],
    ),
),
