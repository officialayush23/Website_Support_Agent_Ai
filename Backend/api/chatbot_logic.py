# import os
# from supabase import create_client, Client

# SUPABASE_URL = os.getenv("SUPABASE_URL")
# SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY")  # service key (server side)
# supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# if not SUPABASE_URL or not SUPABASE_KEY:
#     raise RuntimeError("Missing SUPABASE_URL or SUPABASE_SERVICE_KEY environment variables.")

# def detect_intent(text: str) -> str:
#     t = (text or "").lower()
    
#     # New intents
#     if "cart" in t or "my cart" in t:
#         return "cart"
#     if "return" in t or "schedule a return" in t:
#         return "returns"
#     if "update" in t or "change my" in t or "password" in t:
#         return "update_profile"
        
#     # Existing intents
#     if "product" in t or "price" in t or "available" in t:
#         return "products"
#     if "complaint" in t or "issue" in t or "problem" in t:
#         return "complaints"
#     if "order" in t or "tracking" in t or "status" in t:
#         return "orders"
#     if "account" in t or "profile" in t or "details" in t:
#         return "account"
#     return "general"

# def get_context_data(intent: str, user_id: int | None = None):
#     """
#     Return a compact JSON-serializable context (not huge dumps) based on intent.
#     Keep it small — pass to Gemini as context.
#     """
#     if not user_id:
#         return {"site": "Daksha.ai - Anonymous user. User must be logged in for most actions."}

#     # if intent == "products":
#     #     # return top 10 product names + price + stock
#     #     res = supabase.table("products").select("product_id,name,price,stock").limit(10).execute()
#     #     return res.data or []
#     if intent == "products":
#     # Return a small list (top 10) with rich fields so Gemini can reason about product attributes.
#         res = supabase.table("products").select(
#             "product_id, name, description, price, stock, rating, type, style, color, category, image_url"
#         ).limit(10).execute()
#         return res.data or []

    
#     if intent == "complaints":
#         res = supabase.table("complaints").select("complaint_id,order_id,status,created_at").eq("user_id", user_id).order("created_at", {"ascending": False}).limit(10).execute()
#         return res.data or []
    
#     if intent == "orders":
#         res = supabase.table("orders").select("order_id,order_date,status,total_amount,expected_delivery").eq("user_id", user_id).order("order_date", {"ascending": False}).limit(10).execute()
#         return res.data or []
    
#     if intent == "account":
#         res = supabase.table("users").select("user_id,name,email,phone,city,state").eq("user_id", user_id).execute()
#         return res.data[0] if res.data else {}

 

#     if intent == "cart":
#         """
#         Read cart_items for the user and include product info (name, price, image_url).
#         This keeps cart display in sync with how create_order_from_cart reads the cart.
#         """
#         try:
#             # fetch cart items and their product rows in one query (supabase returns products as nested)
#             res = supabase.table("cart_items").select(
#                 "cart_item_id, product_id, quantity, products(product_id, name, price, image_url, stock)"
#             ).eq("user_id", user_id).execute()

#             cart_rows = res.data or []
#             if not cart_rows:
#                 return {"cart_items": [], "total": 0}

#             items = []
#             total = 0.0
#             for r in cart_rows:
#                 prod = r.get("products") or {}
#                 price = prod.get("price") or 0
#                 qty = r.get("quantity", 0)
#                 item_total = float(price) * int(qty)
#                 total += item_total

#                 items.append({
#                     "cart_item_id": r.get("cart_item_id"),
#                     "product_id": r.get("product_id"),
#                     "product_name": prod.get("name"),
#                     "quantity": qty,
#                     "price": float(price),
#                     "image_url": prod.get("image_url"),
#                     "stock": prod.get("stock"),
#                     # optional: small subtotal
#                     "subtotal": round(item_total, 2)
#                 })

#             return {"cart_items": items, "total": round(total, 2)}
#         except Exception as e:
#             print(f"Error fetching cart (cart_items): {e}")
#             return {"error": "Could not fetch cart."}
# # ---- end replacement ----


#     if intent == "returns":
#         try:
#             # 1. Get user's orders
#             order_res = supabase.table("orders").select("order_id").eq("user_id", user_id).execute()
#             if not order_res.data:
#                 return {"recent_returns": [], "eligible_orders": []}
            
#             order_ids = [o['order_id'] for o in order_res.data]
            
#             # 2. Get returns for those orders
#             return_res = supabase.table("returns").select("return_id, order_id, product_id, reason, status, requested_date") \
#                                  .in_("order_id", order_ids).order("requested_date", {"ascending": False}).limit(5).execute()
            
#             # 3. Get eligible orders (e.g., delivered) to *create* a return
#             eligible_orders = supabase.table("orders").select("order_id, status, total_amount, order_date") \
#                                         .in_("order_id", order_ids).eq("status", "delivered").order("order_date", {"ascending": False}).limit(5).execute()

#             return {"recent_returns": return_res.data or [], "eligible_orders": eligible_orders.data or []}
#         except Exception as e:
#             print(f"Error fetching returns: {e}")
#             return {"error": "Could not fetch return info."}
            
#     # --- END NEW LOGIC ---

#     # general website info (short)
#     return {
#         "site": "Daksha.ai - products, support, orders, returns. You can ask about products, orders, returns, complaints and schedule meetings with support."
#     }

# def get_filtered_products(filters: dict, limit: int = 10):
#     """
#     Safely filter the products table using ilike for fuzzy matching.
#     Returns a supabase result object (.data holds list).
#     """
#     allowed_cols = {"product_id","name","description","price","stock","rating","type","style","color","category","image_url"}
#     q = supabase.table("products").select(
#         "product_id, name, description, price, stock, rating, type, style, color, category, image_url"
#     )

#     try:
#         if not filters:
#             return q.limit(limit).execute()

#         for key, val in filters.items():
#             if key not in allowed_cols or val is None:
#                 continue
#             if isinstance(val, (list, tuple)):
#                 q = q.in_(key, val)
#             else:
#                 # Convert value to string and do case-insensitive partial match
#                 q = q.ilike(key, f"%{str(val)}%")
#         return q.limit(limit).execute()
#     except Exception as e:
#         print(f"get_filtered_products error: {e}")
#         # Return an empty result-like object to keep callers simple
#         class EmptyRes: data = []
#         return EmptyRes()

# api/chatbot_logic.py
import os
from supabase import create_client, Client

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY")  # service key (server side)
if not SUPABASE_URL or not SUPABASE_KEY:
    raise RuntimeError("Missing SUPABASE_URL or SUPABASE_SERVICE_KEY environment variables.")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


def detect_intent(text: str) -> str:
    """
    Improved intent detector:
    - explicit phrase matching first (to avoid LLM handling simple DB reads)
    - then fallback to older heuristics
    """
    import re
    t = (text or "").strip().lower()

    if not t:
        return "general"

    # Normalize whitespace
    t_single = re.sub(r"\s+", " ", t)

    # ----- Explicit phrase checks (priority) -----
    # Cart / show cart
    cart_phrases = [
        "show my cart", "show cart", "my cart", "what's in my cart", "what is in my cart",
        "view cart", "open cart", "see my cart", "see cart", "cart items", "list my cart"
    ]
    if any(p in t_single for p in cart_phrases):
        return "cart"

    # Orders / show orders / list orders
    orders_phrases = [
        "show my orders", "my orders", "list my orders", "order history", "orders placed",
        "list orders", "show orders", "what orders have i placed", "orders i placed"
    ]
    if any(p in t_single for p in orders_phrases):
        return "orders"

    # Show total of cart / order totals
    total_phrases = [
        "show total", "what's the total", "what is the total", "cart total", "total of my cart",
        "total amount", "order total"
    ]
    if any(p in t_single for p in total_phrases):
        return "cart_total"  # you can handle this in backend by returning cart and summing

    # Shipping / tracking / shipping details
    shipping_phrases = [
        "shipping details", "show shipping", "shipping address", "track my order", "tracking",
        "show me the shipping details", "where is my order", "track order"
    ]
    if any(p in t_single for p in shipping_phrases):
        return "shipping"

    # Checkout / order my cart / place order
    checkout_phrases = [
        "checkout", "order my cart", "place order", "please order the items", "order items in my cart",
        "please order", "buy cart", "order now"
    ]
    if any(p in t_single for p in checkout_phrases):
        return "create_order"

    # Return / initiate return
    return_phrases = [
        "i want to return", "return item", "initiate return", "start return", "i want to return a product",
        "return product", "return request", "refund"
    ]
    if any(p in t_single for p in return_phrases):
        return "returns"

    # Complaints / issues
    complaints_phrases = ["file a complaint", "i have an issue", "complaint", "report a problem", "raise an issue"]
    if any(p in t_single for p in complaints_phrases):
        return "complaints"

    # Profile / account
    account_phrases = ["show my profile", "my profile", "account details", "account info", "profile"]
    if any(p in t_single for p in account_phrases):
        return "account"

    # ----- Fallback heuristics (keep your existing rules) -----
    if "cart" in t_single or "my cart" in t_single:
        return "cart"
    if "return" in t_single or "schedule a return" in t_single:
        return "returns"
    if "update" in t_single or "change my" in t_single or "password" in t_single:
        return "update_profile"
    if "product" in t_single or "price" in t_single or "available" in t_single or "show me" in t_single:
        return "products"
    if "complaint" in t_single or "issue" in t_single or "problem" in t_single:
        return "complaints"
    if "order" in t_single or "tracking" in t_single or "status" in t_single:
        return "orders"
    if "account" in t_single or "profile" in t_single or "details" in t_single:
        return "account"

    return "general"



def get_context_data(intent: str, user_id: int | None = None):
    """
    Return a compact JSON-serializable context (not huge dumps) based on intent.
    Keep it small — pass to Gemini as context.
    This function is synchronous (safe to call with async_to_sync).
    """
    if not user_id:
        return {"site": "Daksha.ai - Anonymous user. User must be logged in for most actions."}

    if intent == "products":
        # Return a small list (top 10) with rich fields so Gemini can reason about product attributes.
        res = supabase.table("products").select(
            "product_id, name, description, price, stock, rating, type, style, color, category, image_url"
        ).limit(10).execute()
        return res.data or []

    if intent == "complaints":
        res = supabase.table("complaints_updated").select("complaint_id,order_id,status,created_at").eq("user_id", user_id).order("created_at", {"ascending": False}).limit(10).execute()
        return res.data or []

    if intent == "orders":
        res = supabase.table("orders").select("order_id,order_date,status,total_amount,expected_delivery").eq("user_id", user_id).order("order_date", {"ascending": False}).limit(10).execute()
        return res.data or []

    if intent == "account":
        res = supabase.table("users").select("user_id,name,email,phone,city,state").eq("user_id", user_id).execute()
        return res.data[0] if res.data else {}

    if intent == "cart":
        # Read cart_items for the user and include product info (name, price, image_url).
        try:
            res = supabase.table("cart_items").select(
                "cart_item_id, product_id, quantity, products(product_id, name, price, image_url, stock)"
            ).eq("user_id", user_id).execute()

            cart_rows = res.data or []
            if not cart_rows:
                return {"cart_items": [], "total": 0}

            items = []
            total = 0.0
            for r in cart_rows:
                prod = r.get("products") or {}
                price = prod.get("price") or 0
                qty = r.get("quantity", 0)
                item_total = float(price) * int(qty)
                total += item_total

                items.append({
                    "cart_item_id": r.get("cart_item_id"),
                    "product_id": r.get("product_id"),
                    "product_name": prod.get("name"),
                    "quantity": qty,
                    "price": float(price),
                    "image_url": prod.get("image_url"),
                    "stock": prod.get("stock"),
                    "subtotal": round(item_total, 2)
                })

            return {"cart_items": items, "total": round(total, 2)}
        except Exception as e:
            print(f"Error fetching cart (cart_items): {e}")
            return {"error": "Could not fetch cart."}

    if intent == "returns":
        try:
            order_res = supabase.table("orders").select("order_id").eq("user_id", user_id).execute()
            if not order_res.data:
                return {"recent_returns": [], "eligible_orders": []}
            order_ids = [o['order_id'] for o in order_res.data]

            return_res = supabase.table("returns").select("return_id, order_id, product_id, reason, status, requested_date") \
                .in_("order_id", order_ids).order("requested_date", {"ascending": False}).limit(5).execute()

            eligible_orders = supabase.table("orders").select("order_id, status, total_amount, order_date") \
                .in_("order_id", order_ids).eq("status", "delivered").order("order_date", {"ascending": False}).limit(5).execute()

            return {"recent_returns": return_res.data or [], "eligible_orders": eligible_orders.data or []}
        except Exception as e:
            print(f"Error fetching returns: {e}")
            return {"error": "Could not fetch return info."}

    # general website info (short)
    return {
        "site": "Daksha.ai - products, support, orders, returns. You can ask about products, orders, returns, complaints and schedule meetings with support."
    }


def get_filtered_products(filters: dict, limit: int = 10):
    """
    Safely filter the products table using ilike for fuzzy matching.
    Returns a supabase result object (.data holds list).
    """
    allowed_cols = {"product_id", "name", "description", "price", "stock", "rating", "type", "style", "color", "category", "image_url"}
    q = supabase.table("products").select(
        "product_id, name, description, price, stock, rating, type, style, color, category, image_url"
    )
    try:
        if not filters:
            return q.limit(limit).execute()

        for key, val in filters.items():
            if key not in allowed_cols or val is None:
                continue
            if isinstance(val, (list, tuple)):
                q = q.in_(key, val)
            else:
                q = q.ilike(key, f"%{str(val)}%")
        return q.limit(limit).execute()
    except Exception as e:
        print(f"get_filtered_products error: {e}")
        class EmptyRes:
            data = []
        return EmptyRes()
