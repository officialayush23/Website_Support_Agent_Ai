import os
from supabase import create_client, Client

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY")  # service key (server side)
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def detect_intent(text: str) -> str:
    t = (text or "").lower()
    
    # New intents
    if "cart" in t or "my cart" in t:
        return "cart"
    if "return" in t or "schedule a return" in t:
        return "returns"
    if "update" in t or "change my" in t or "password" in t:
        return "update_profile"
        
    # Existing intents
    if "product" in t or "price" in t or "available" in t:
        return "products"
    if "complaint" in t or "issue" in t or "problem" in t:
        return "complaints"
    if "order" in t or "tracking" in t or "status" in t:
        return "orders"
    if "account" in t or "profile" in t or "details" in t:
        return "account"
    return "general"

def get_context_data(intent: str, user_id: int | None = None):
    """
    Return a compact JSON-serializable context (not huge dumps) based on intent.
    Keep it small — pass to Gemini as context.
    """
    if not user_id:
        return {"site": "Daksha.ai - Anonymous user. User must be logged in for most actions."}

    if intent == "products":
        # return top 10 product names + price + stock
        res = supabase.table("products").select("product_id,name,price,stock").limit(10).execute()
        return res.data or []
    
    if intent == "complaints":
        res = supabase.table("complaints").select("complaint_id,order_id,status,created_at").eq("user_id", user_id).order("created_at", {"ascending": False}).limit(10).execute()
        return res.data or []
    
    if intent == "orders":
        res = supabase.table("orders").select("order_id,order_date,status,total_amount,expected_delivery").eq("user_id", user_id).order("order_date", {"ascending": False}).limit(10).execute()
        return res.data or []
    
    if intent == "account":
        res = supabase.table("users").select("user_id,name,email,phone,city,state").eq("user_id", user_id).execute()
        return res.data[0] if res.data else {}

    # --- NEW CONTEXT LOGIC ---
    if intent == "cart":
        # Assuming a "cart" is an order with status 'cart'
        cart_order = supabase.table("orders").select("order_id, total_amount").eq("user_id", user_id).eq("status", "cart").limit(1)
        
        try:
            cart_res = cart_order.execute()
            if not cart_res.data:
                return {"cart_items": [], "total": 0}
            
            order_id = cart_res.data[0]['order_id']
            
            # Use a view or RPC in Supabase for this join in production
            items_res = supabase.table("order_items").select("quantity, price_at_order, products(name)").eq("order_id", order_id).execute()
            
            return {"cart_items": items_res.data, "total": cart_res.data[0]['total_amount']}
        except Exception as e:
            print(f"Error fetching cart: {e}")
            return {"error": "Could not fetch cart."}

    if intent == "returns":
        try:
            # 1. Get user's orders
            order_res = supabase.table("orders").select("order_id").eq("user_id", user_id).execute()
            if not order_res.data:
                return {"recent_returns": [], "eligible_orders": []}
            
            order_ids = [o['order_id'] for o in order_res.data]
            
            # 2. Get returns for those orders
            return_res = supabase.table("returns").select("return_id, order_id, product_id, reason, status, requested_date") \
                                 .in_("order_id", order_ids).order("requested_date", {"ascending": False}).limit(5).execute()
            
            # 3. Get eligible orders (e.g., delivered) to *create* a return
            eligible_orders = supabase.table("orders").select("order_id, status, total_amount, order_date") \
                                        .in_("order_id", order_ids).eq("status", "delivered").order("order_date", {"ascending": False}).limit(5).execute()

            return {"recent_returns": return_res.data or [], "eligible_orders": eligible_orders.data or []}
        except Exception as e:
            print(f"Error fetching returns: {e}")
            return {"error": "Could not fetch return info."}
            
    # --- END NEW LOGIC ---

    # general website info (short)
    return {
        "site": "Daksha.ai - products, support, orders, returns. You can ask about products, orders, returns, complaints and schedule meetings with support."
    }
