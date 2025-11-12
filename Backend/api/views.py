
# import os
# import json
# import asyncio
# import jwt
# from jwt.exceptions import InvalidTokenError
# from django.http import JsonResponse
# from django.conf import settings
# from django.views.decorators.csrf import csrf_exempt
# from rest_framework.decorators import api_view, permission_classes
# from rest_framework.permissions import AllowAny
# from supabase import create_client, Client
# from typing import Optional, Any, Dict, List
# import google.generativeai as genai
# # from .chatbot_logic import detect_intent, get_context_data
# from .chatbot_logic import detect_intent, get_context_data, get_filtered_products

# from asgiref.sync import async_to_sync
# from datetime import datetime, timezone # --- NEW: Import for timestamp ---

# # -------------------------------
# # INITIAL SETUP
# # -------------------------------
# SUPABASE_URL = settings.SUPABASE_URL
# SUPABASE_SERVICE_KEY = settings.SUPABASE_SERVICE_KEY
# SUPABASE_JWT_SECRET = settings.SUPABASE_JWT_SECRET

# #  SUPABASE_URL and SUPABASE_SERVICE_KEY
# if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
#     raise ValueError("Supabase URL and Service Key must be set in settings.")

# supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

# if os.getenv("GEMINI_API_KEY"):
#     genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# # -------------------------------
# # JWT VERIFICATION (LOCAL)
# # -------------------------------
# def verify_supabase_jwt(token: str) -> Optional[dict]:
#     """
#     Verify Supabase JWT using configured secret (HS256).
#     Returns decoded payload dict on success, else None.
#     """
#     if not token:
#         return None

#     try:
#         decoded = jwt.decode(
#             token,
#             SUPABASE_JWT_SECRET,
#             algorithms=["HS256"],
#             options={"verify_aud": False} 
#         )
#         print("✅ Decoded token:", decoded)
#         return decoded
#     except jwt.ExpiredSignatureError:
#         print("❌ Token expired")
#         return None
#     except jwt.InvalidTokenError as e:
#         # If verification fails
#         try:
#             decoded = jwt.decode(token, options={"verify_signature": False})
#             print("⚠️ Token signature invalid, decoded without verification:", decoded)
#             return None
#         except Exception:
#             print("❌ Invalid token:", str(e))
#             return None

# # -------------------------------
# # ASYNC SUPABASE HELPERS
# # -------------------------------

# async def supabase_select_one(table: str, select: str, eq_col: str, eq_val) -> Optional[dict]:
#     def _fn():
#         return supabase.table(table).select(select).eq(eq_col, eq_val).limit(1).execute()
#     res = await asyncio.to_thread(_fn)
#     return res.data[0] if res.data else None


# async def supabase_select(table: str, select: str = "*", filters: Dict[str, Any] = None) -> List[dict]:
#     """
#     Selects data from a table with multiple .eq() filters.
#     """
#     def _fn():
#         query = supabase.table(table).select(select)
#         if filters:
#             for col, val in filters.items():
#                 query = query.eq(col, val)
#         return query.execute()
#     res = await asyncio.to_thread(_fn)
#     return res.data or []


# async def supabase_insert(table: str, payload: dict) -> dict:
#     def _fn():
     
#         return supabase.table(table).insert(payload).execute()
#     res = await asyncio.to_thread(_fn)
#     if hasattr(res, "data") and res.data:
#         return {"success": True, "data": res.data}
#     return {"success": False, "error": getattr(res, "error", str(res))}

# async def supabase_update(table: str, payload: dict, eq_col: str, eq_val) -> dict:
#     def _fn():
#         return supabase.table(table).update(payload).eq(eq_col, eq_val).execute()
#     res = await asyncio.to_thread(_fn)
#     if hasattr(res, "data") and res.data:
#         return {"success": True, "data": res.data}
#     return {"success": False, "error": getattr(res, "error", str(res))}


# async def supabase_delete(table: str, filters: Dict[str, Any] = None) -> dict:
#     """
#     Deletes data from a table with multiple .eq() filters.
#     """
#     def _fn():
#         query = supabase.table(table).delete()
#         if filters:
#             for col, val in filters.items():
#                 query = query.eq(col, val)
#         return query.execute()
#     res = await asyncio.to_thread(_fn)
#     if hasattr(res, "data") and res.data:
#         return {"success": True, "data": res.data}
#     return {"success": False, "error": getattr(res, "error", str(res))}






# # ---  Get chat history ---
# async def get_recent_chat_history(user_id: int) -> List[dict]:
#     """
#     Fetches the last 5 messages for a user to provide context.
#     """
#     def _fn():

#         return supabase.table("chat_logs_updated").select("user_message, bot_response").eq("user_id", user_id).order("timestamp", desc=True).limit(5).execute()
    
#     res = await asyncio.to_thread(_fn)
#     # Return in reverse order to be chronological (oldest to newest)
#     return (res.data or [])[::-1]

# # ---  Log chat message ---
# async def log_chat_message(user_id: Optional[int], user_message: str, bot_response: str, intent: str):
#     """
#     Logs the conversation to the chat_logs_updated table.
#     """
#     log_payload = {
#         "user_id": user_id,
#         "user_message": user_message,
#         "bot_response": bot_response, # This is the JSON string of the response
#         "intent_detected": intent,
#         "timestamp": datetime.now(timezone.utc).isoformat()
#     }
#     # Fire-and-forget logging
#     try:

#         await supabase_insert("chat_logs_updated", log_payload)
#         print(f"Logged chat for user {user_id}")
#     except Exception as e:
#         print(f"Failed to log chat: {e}")


# # -------------------------------
# # USER AUTH ROUTES
# # -------------------------------

# @api_view(['POST'])
# @permission_classes([AllowAny])
# def register_user(request): 
#     """Signup: Register new user into Supabase 'users' table."""
#     data = request.data
#     try:

#         existing = async_to_sync(supabase_select_one)("users", "user_id", "email", data["email"])
#         if existing:
#             return JsonResponse({"error": "User already exists"}, status=400)


#         payload = {
#             # --- FIX: Removed "user_id": next_id. DB will assign it. ---
#             "name": data.get("username"),
#             "email": data.get("email"),
#             "password_hash": data.get("password"), # Hash in production
#             "phone": "",
#             "address": "",
#             "city": "",
#             "state": "",
#             "pincode": "",
#         }
#         # --- FIX: Use async_to_sync to call async helper ---
#         result = async_to_sync(supabase_insert)("users", payload)
        
#         if not result.get("success"):
#             return JsonResponse({"error": str(result.get("error"))}, status=400)

#         return JsonResponse({"message": "User registered successfully"}, status=201)
#     except Exception as e:
#         return JsonResponse({"error": str(e)}, status=400)


# @api_view(['POST'])
# @permission_classes([AllowAny])
# def login_user(request): 
#     """
#     Login route — Supabase Auth handles the JWT issuance on frontend.
#     This backend view is for manual (email/pass) auth if not using Supabase client.
#     """
#     data = request.data
#     email = data.get("email")
#     password = data.get("password")

#     if not email or not password:
#         return JsonResponse({"error": "Email and password required"}, status=400)


#     user = async_to_sync(supabase_select_one)("users", "user_id,email", "email", email)
#     if not user:
#         return JsonResponse({"error": "Invalid credentials"}, status=401)
    


#     payload = {"email": email, "sub": user["user_id"], "user_metadata": user}
#     token = jwt.encode(payload, SUPABASE_JWT_SECRET, algorithm="HS256")

#     return JsonResponse({"access_token": token, "message": "Login successful"})


# @api_view(['POST'])
# @permission_classes([AllowAny])
# def forgot_password(request):
#     """Stub forgot password API (to be expanded later)."""
#     email = request.data.get("email")
#     if not email:
#         return JsonResponse({"error": "Email required"}, status=400)
#     # You can trigger Supabase reset email here using supabase.auth.reset_password_for_email(email)
#     return JsonResponse({"message": f"Password reset link sent to {email}"})


# @api_view(['GET'])
# def get_profile(request): # --- FIX: Made sync 'def' ---
#     """Get user profile after verifying Supabase JWT."""
#     auth_header = request.headers.get("Authorization")

#     if not auth_header or not auth_header.startswith("Bearer "):
#         return JsonResponse({"error": "Missing or invalid token"}, status=401)

#     token = auth_header.split(" ")[1]
#     decoded = verify_supabase_jwt(token)

#     if not decoded:
#         return JsonResponse({"error": "Invalid or expired token"}, status=401)

#     # The profile data is already in the token.
#     user_data = decoded.get("user_metadata")

#     if not user_data:
#         # Fallback if user_metadata isn't in the token
#         email = decoded.get("email")
#         if not email:
#             return JsonResponse({"error": "Invalid token payload"}, status=400)
        
 
#         user = async_to_sync(supabase_select_one)("users", "*", "email", email) 
        
#         if not user:
#              return JsonResponse({"error": "User not found in DB, though token is valid"}, status=404) # 404
#         user_data = user
    
#     if 'id' not in user_data:
#         user_data['id'] = decoded.get('sub')
#     if 'email' not in user_data:
#          user_data['email'] = decoded.get('email')

#     return JsonResponse(user_data, status=200)



# # -------------------------------
# # GEMINI + CHATBOT SECTION
# # -------------------------------

# def extract_json_action(text: str) -> Optional[dict]:
#     """Extract embedded JSON action block from model response."""
#     if not text:
#         return None
#     text = text.strip()
#     # Find the first { and the last }
#     start = text.find("{")
#     end = text.rfind("}") + 1
#     if start == -1 or end == -1:
#         return None # No JSON found
    
#     json_str = text[start:end]
#     try:
#         # Try to parse the extracted string
#         obj = json.loads(json_str)
#         return obj # Return the parsed JSON object
#     except json.JSONDecodeError:
#         print(f"Failed to decode JSON: {json_str}")
#         pass
#     return None


# async def call_gemini(prompt: str) -> str:
#     """Call Gemini asynchronously."""
#     def _fn():
#         try:
     
#             model = genai.GenerativeModel("gemini-2.5-flash-preview-09-2025")
#             res = model.generate_content(prompt)
#             return getattr(res, "text", str(res))
#         except Exception as e:
#             print(f"GEMINI ERROR: {e}")
#             return json.dumps({"type": "text", "payload": "Sorry, I'm having trouble connecting to my brain. Please try again."})

#     return await asyncio.to_thread(_fn)



# async def create_order_from_cart(user_id: int) -> dict:
#     """
#     Complex action:
#     1. Read user's cart
#     2. Get product prices
#     3. Calculate total
#     4. Create 'orders' entry
#     5. Create 'order_items' entries
#     6. Clear user's cart
#     """
#     # 1. Read cart
#     cart_items = await supabase_select("cart_items", "product_id,quantity", {"user_id": user_id})
#     if not cart_items:
#         return {"success": False, "error": "Your cart is empty."}

#     # 2. Get product prices
#     product_ids = [item['product_id'] for item in cart_items]
    
#     def _get_products():
#         return supabase.table("products").select("product_id, name, price").in_("product_id", product_ids).execute()
    
#     product_res = await asyncio.to_thread(_get_products)
#     if not product_res.data:
#         return {"success": False, "error": "Could not find product details for items in your cart."}
    
#     product_price_map = {p['product_id']: p['price'] for p in product_res.data}
#     product_name_map = {p['product_id']: p['name'] for p in product_res.data}

#     # 3. Calculate total
#     total_amount = 0
#     order_items_payload = []
    
#     for item in cart_items:
#         product_id = item['product_id']
#         quantity = item['quantity']
#         price = product_price_map.get(product_id)
        
#         if not price:
#             print(f"Price for product_id {product_id} not found. Skipping.")
#             continue
            
#         total_amount += price * quantity
#         order_items_payload.append({
#             # "order_id" will be added after we create the order
#             "product_id": product_id,
#             "quantity": quantity,
#             "price_at_order": price
#         })

#     if not order_items_payload:
#         return {"success": False, "error": "No valid items to order."}

#     # 4. Create 'orders' entry
#     user_profile = await supabase_select_one("users", "address,city,state,pincode", "user_id", user_id)
#     shipping_address = f"{user_profile.get('address', '')}, {user_profile.get('city', '')}, {user_profile.get('state', '')} {user_profile.get('pincode', '')}"
    
#     order_payload = {
#         "user_id": user_id,
#         "status": "Pending", # Or "Confirmed"
#         "total_amount": total_amount,
#         "shipping_address": shipping_address,
#         "payment_method": "Pending" # Assuming payment is handled elsewhere
#     }
    
#     order_res = await supabase_insert("orders", order_payload)
#     if not order_res.get("success"):
#         return {"success": False, "error": f"Failed to create order: {order_res.get('error')}"}
    
#     new_order_id = order_res['data'][0]['order_id']
    
#     # 5. Create 'order_items' entries
#     for item in order_items_payload:
#         item['order_id'] = new_order_id
        
#     insert_items_res = await supabase_insert("order_items", order_items_payload)
#     if not insert_items_res.get("success"):
#         # This is bad, we created an order with no items.
#         # A real app would "roll back" the order creation.
#         print(f"Failed to insert order_items: {insert_items_res.get('error')}")
#         return {"success": False, "error": "Created order but failed to add items."}

#     # 6. Clear user's cart
#     await supabase_delete("cart_items", {"user_id": user_id})
    
#     return {"success": True, "order_id": new_order_id, "total": total_amount}


# @csrf_exempt
# @api_view(['POST']) # Add the decorator
# def chatbot(request): # --- FIX: Changed to sync 'def' ---
#     """Daksha.ai chatbot endpoint."""
    
#     # Define early for logging
#     user_id = None
#     intent = "unknown"
#     message = ""

#     try:
#         # ------------------------
#         # 1️⃣ Parse input
#         # ------------------------
#         try:
#             body = json.loads(request.body.decode("utf-8"))
#             message = body.get("message", "").strip()
#         except Exception:
#             response_data = {"error": "Invalid JSON"}
#             async_to_sync(log_chat_message)(user_id, message, json.dumps(response_data), intent)
#             return JsonResponse(response_data, status=400)

#         if not message:
#             response_data = {"error": "Message required"}
#             async_to_sync(log_chat_message)(user_id, message, json.dumps(response_data), intent)
#             return JsonResponse(response_data, status=400)

#         # ------------------------
#         # 2️⃣ Verify JWT and Get User
#         # ------------------------
#         auth_header = request.headers.get("Authorization", "")
#         user_info = None
#         user_email = None

#         if not auth_header.startswith("Bearer "):
#             response_data = {"error": "Authorization token missing"}
#             async_to_sync(log_chat_message)(user_id, message, json.dumps(response_data), intent)
#             return JsonResponse(response_data, status=401)
        
#         token = auth_header.split(" ")[1]
#         user_info = verify_supabase_jwt(token)

#         if not user_info:
#             response_data = {"error": "Invalid or expired token"}
#             async_to_sync(log_chat_message)(user_id, message, json.dumps(response_data), intent)
#             return JsonResponse(response_data, status=401)

#         user_email = user_info.get("email")
#         if not user_email:
#             response_data = {"error": "Invalid token payload, email missing"}
#             async_to_sync(log_chat_message)(user_id, message, json.dumps(response_data), intent)
#             return JsonResponse(response_data, status=400)

#         # --- JIT User Provisioning ---
#         row = async_to_sync(supabase_select_one)("users", "user_id,email", "email", user_email)
        
#         if not row:
#             print(f"User not found in 'users' table. Provisioning: {user_email}")
#             try:
#                 # --- FIX: Removed get_next_user_id ---
#                 new_user_payload = {
#                     # --- FIX: Removed "user_id". DB will assign it. ---
#                     "email": user_email,
#                     "name": user_info.get("user_metadata", {}).get("name", "New User"),
#                 }
#                 insert_res = async_to_sync(supabase_insert)("users", new_user_payload)
                
#                 if not insert_res.get("success"):
#                     print(f"Failed to provision user: {insert_res.get('error')}")
#                     response_data = {"error": "User provisioning failed."}
#                     async_to_sync(log_chat_message)(user_id, message, json.dumps(response_data), intent)
#                     return JsonResponse(response_data, status=500)
                
#                 # --- FIX: Get the new user_id from the insert response ---
#                 user_id = insert_res['data'][0]['user_id']
#                 print(f"Provisioned new user with user_id: {user_id}")
            
#             except Exception as e:
#                 print(f"Error during JIT provisioning: {e}")
#                 response_data = {"error": "Error creating user profile."}
#                 async_to_sync(log_chat_message)(user_id, message, json.dumps(response_data), intent)
#                 return JsonResponse(response_data, status=500)
#         else:
#             user_id = row.get("user_id")

#         if not user_id:
#             response_data = {"error": "Could not determine user ID"}
#             async_to_sync(log_chat_message)(user_id, message, json.dumps(response_data), intent)
#             return JsonResponse(response_data, status=500)


#         # ------------------------
#         # 3️⃣ Intent detection & context
#         # ------------------------
#         try:
#             intent = detect_intent(message)
#             # get_context_data is synchronous in chatbot_logic.py — call it via async_to_sync
#             context = async_to_sync(get_context_data)(intent, user_id)
#         except Exception as e:
#             print(f"Context/Intent Error: {e}")
#             intent = "general_error"
#             context = {"error": "Failed to get context."}

#         # ------------------------
#         # Short-circuit common read-only intents to avoid LLM involvement
#         # ------------------------
#         if intent in ("cart", "orders", "account", "shipping", "cart_total"):
#             try:
#                 # CART — frontend expects payload to be an array for cart_items
#                 if intent == "cart":
#                     # get_context_data returns {"cart_items": [...], "total": n} or {"error": "..."}
#                     cart_ctx = context if isinstance(context, dict) else {}
#                     items = cart_ctx.get("cart_items", []) if isinstance(cart_ctx, dict) else []
#                     total = cart_ctx.get("total", 0)
#                     # Normalize: frontend RenderCartItems expects payload = array of items
#                     response_data = {"type": "cart_items", "payload": items, "total": total}

#                 # ORDERS — return list of orders (frontend uses order_list renderer)
#                 elif intent == "orders":
#                     orders = context if isinstance(context, list) else (context.get("orders") if isinstance(context, dict) else [])
#                     # If get_context_data returned a list, use it; if it returned a dict (rare), try common keys
#                     if isinstance(context, dict) and not orders:
#                         # some implementations return {"orders": [...]} or {"error": ...}
#                         orders = context.get("orders") or context.get("order_list") or []
#                     response_data = {"type": "order_list", "payload": orders}

#                 # ACCOUNT / PROFILE
#                 elif intent == "account":
#                     profile = context if isinstance(context, dict) else {}
#                     response_data = {"type": "profile_data", "payload": profile}

#                 # CART TOTAL (explicit)
#                 elif intent == "cart_total":
#                     cart_ctx = context if isinstance(context, dict) else {}
#                     total = cart_ctx.get("total", 0)
#                     response_data = {"type": "text", "payload": f"Your cart total is ${float(total):.2f}"}

#                 # SHIPPING: try to parse an order id from the message; else return recent orders
#                 elif intent == "shipping":
#                     import re
#                     m = re.search(r"order\s*#?\s*(\d+)", message, re.IGNORECASE)
#                     if m:
#                         order_id = int(m.group(1))
#                         # Use existing helper to fetch a single order
#                         order_row = async_to_sync(supabase_select_one)("orders", "*", "order_id", order_id)
#                         if order_row and order_row.get("user_id") == user_id:
#                             ship_addr = order_row.get("shipping_address") or "N/A"
#                             expect = order_row.get("expected_delivery")
#                             response_data = {"type": "text", "payload": f"Order {order_id} — Shipping address: {ship_addr}. Expected delivery: {expect}"}
#                         else:
#                             response_data = {"type": "text", "payload": f"Order {order_id} not found (or doesn't belong to you)."}
#                     else:
#                         # No order id — show recent orders (reuse 'orders' intent context)
#                         orders_list = context if isinstance(context, list) else []
#                         response_data = {"type": "order_list", "payload": orders_list}

#                 # Log and return the short-circuited response
#                 async_to_sync(log_chat_message)(user_id, message, json.dumps(response_data), intent)
#                 return JsonResponse(response_data, status=200)

#             except Exception as e:
#                 # If short-circuit fails, print and fall through to LLM handling
#                 print("Short-circuit read-intent error:", e)

        
        
#                 # --- SHORT-CIRCUIT: For read/display intents, return DB data directly (avoid LLM hallucination) ---
#         # try:
#         #     # get_context_data is synchronous; call via async_to_sync for consistency
#         #     db_context = async_to_sync(get_context_data)(intent, user_id)

#         #     if intent == "cart":
#         #         # get_context_data returns {"cart_items": [...], "total": n} on success
#         #         if isinstance(db_context, dict):
#         #             payload = db_context.get("cart_items", [])
#         #             total = db_context.get("total", 0)
#         #         else:
#         #             payload = []
#         #             total = 0
#         #         response_data = {"type": "cart_items", "payload": payload, "total": total}
#         #         async_to_sync(log_chat_message)(user_id, message, json.dumps(response_data), intent)
#         #         return JsonResponse(response_data, status=200)

#         #     if intent == "orders":
#         #         # Expecting list of orders
#         #         if isinstance(db_context, list):
#         #             payload = db_context
#         #         elif isinstance(db_context, dict) and db_context.get("error"):
#         #             payload = []
#         #         else:
#         #             # some branches return a single dict
#         #             payload = db_context if db_context else []
#         #         response_data = {"type": "order_list", "payload": payload}
#         #         async_to_sync(log_chat_message)(user_id, message, json.dumps(response_data), intent)
#         #         return JsonResponse(response_data, status=200)

#         #     if intent == "account":
#         #         # profile object
#         #         response_data = {"type": "profile_data", "payload": db_context or {}}
#         #         async_to_sync(log_chat_message)(user_id, message, json.dumps(response_data), intent)
#         #         return JsonResponse(response_data, status=200)

#         #     if intent == "products":
#         #         # get_context_data for products returns a list (top N)
#         #         response_data = {"type": "product_list", "payload": db_context if isinstance(db_context, list) else []}
#         #         async_to_sync(log_chat_message)(user_id, message, json.dumps(response_data), intent)
#         #         return JsonResponse(response_data, status=200)

#         #     if intent == "returns":
#         #         # returns handler returns dict with recent_returns & eligible_orders
#         #         response_data = {"type": "return_list", "payload": db_context}
#         #         async_to_sync(log_chat_message)(user_id, message, json.dumps(response_data), intent)
#         #         return JsonResponse(response_data, status=200)

#         #     if intent == "complaints":
#         #         # complaints handler should return a list (or dict), normalize to array
#         #         if isinstance(db_context, list):
#         #             payload = db_context
#         #         elif isinstance(db_context, dict) and db_context.get("error"):
#         #             payload = []
#         #         elif isinstance(db_context, dict):
#         #             # if single-object, wrap
#         #             payload = db_context.get("complaints", []) or []
#         #         else:
#         #             payload = []
#         #         response_data = {"type": "complaint_list", "payload": payload}
#         #         async_to_sync(log_chat_message)(user_id, message, json.dumps(response_data), intent)
#         #         return JsonResponse(response_data, status=200)
#         # except Exception as e:
#         #     # If anything fails here, fall back to continuing with Gemini flow below
#         #     print(f"Short-circuit read-intent error: {e}")



#         product_schema_info = """
# Product Table Schema:
# - product_id: integer primary key
# - name: string
# - description: text
# - price: numeric
# - stock: integer
# - rating: numeric
# - type: textual type (e.g., Kurta, Shirt, Jeans)
# - style: style (Ethnic, Western, Formal, Casual, Fusion)
# - color: color name (Black, Blue, etc.)
# - category: Men/Women/Kids/Unisex
# - image_url: url to product image (frontend can render)
# When asking for product recommendations, prefer the fields: name, price, style, color, image_url.
# If user asks "show ethnic black wear", return a "product_list" type with payload being filter criteria, e.g. {"style":"Ethnic","color":"Black"}.
# """

#         # ------------------------
#         # 4️⃣ Build prompt for Gemini (JSON Mode)
#         # ------------------------
#         prompt = f"""
# You are Daksha, a helpful customer support assistant and a Product recommender for an e-commerce website called Dukaan.
# {product_schema_info}
# You MUST ONLY respond with a valid JSON object.
# Your goal is to either DISPLAY information or perform an ACTION.

# SCHEMA:
# {{"type": "response_type", "payload": "response_payload"}}

# ## 1. DISPLAYING INFORMATION
# If the user asks for data (like "show my profile", "what's in my cart"), respond with a display type.
# - "type" can be: "text", "profile_data", "product_list", "cart_items", "order_list", "complaint_list", "return_list", "action_options".
# - "payload" contains the data for the frontend to render.

# EXAMPLES (DISPLAY):
# User: "Hi" -> {{"type": "text", "payload": "Hello! How can I help you today?"}}
# User: "Show my profile" -> {{"type": "profile_data", "payload": {{"name": "Jane Doe", "email": "jane@example.com"}}}}
# User: "What can I do?" -> {{"type": "action_options", "payload": ["View Profile", "Check Orders", "See Cart", "File Complaint"]}}

# ## 2. PERFORMING ACTIONS
# If the user's message is a clear, actionable request (like "update my profile", "add to cart", "checkout"), respond with type "action".
# - "type" MUST be "action".
# - "payload" MUST contain:
#     - "action_name": The action to perform (e.g., "update_profile", "schedule_return", "schedule_meeting", "create_complaint", "add_to_cart", "create_order").
#     - "updates" or "params": The data extracted from the user's message.

# * For "update_profile", valid keys for "updates" are: "name", "phone", "address", "city", "state", "pincode".
# * For "add_to_cart", get "product_id" and "quantity" (default 1).
# * For "create_complaint", get "description". If "order_id" is mentioned, get it.
# * For "create_order", the user just needs to say "checkout" or "order my cart". No params needed.

# EXAMPLES (ACTION):
# User: "Please update my address to 22, east street, pune"
# Response:
# {{"type": "action", "payload": {{"action_name": "update_profile", "updates": {{"address": "22, east street, pune", "city": "pune"}}}}}}

# User: "add product 10 to my cart"
# Response:
# {{"type": "action", "payload": {{"action_name": "add_to_cart", "params": {{"product_id": 10, "quantity": 1}}}}}}

# User: "I want to checkout" or "I want to order my cart"
# Response:
# {{"type": "action", "payload": {{"action_name": "create_order", "params": {{}}}}}}

# ## 3. MULTI-TURN CONVERSATIONS (Slot-filling)
# Use the RECENT CHAT HISTORY to understand context for multi-turn requests.
# If the user's request is an action but is missing information, ask a follow-up question using the "text" type.

# User: "I want to update my profile"
# Response:
# {{"type": "text", "payload": "Great, what information would you like to update?"}}

# User: "my shipping address"
# Response:
# {{"type": "text", "payload": "Okay, what is the new shipping address?"}}

# User: "22, east street, pune"
# Response:
# {{"type": "action", "payload": {{"action_name": "update_profile", "updates": {{"address": "22, east street, pune", "city": "pune"}}}}}}

# User: "I want to file a complaint."
# Response:
# {{"type": "text", "payload": "I can help with that. What is the complaint about?"}}

# User: "My order 123 was damaged."
# Response:
# {{"type": "action", "payload": {{"action_name": "create_complaint", "params": {{"order_id": 123, "description": "Order 123 was damaged"}}}}}}

# User: "The website is slow."
# Response:
# {{"type": "action", "payload": {{"action_name": "create_complaint", "params": {{"description": "The website is slow"}}}}}} 

# ## 4. CONTEXT
# - User ID: {user_id}
# - User Intent: {intent}
# - Database Context: {json.dumps(context)}

# ## 5. RECENT CHAT HISTORY (Oldest to Newest)
# {chat_history_string}


# ## 6. CURRENT USER MESSAGE
# "{message}"

# JSON RESPONSE:
# """

#         # ------------------------
#         # 5️⃣ Call Gemini safely
#         # ------------------------
#         try:
#             bot_reply_text = async_to_sync(call_gemini)(prompt)
#         except Exception as e:
#             print(f"Gemini Error: {e}")
#             response_data = {"type": "text", "payload": "Sorry, I'm having an issue connecting. Please try again."}
#             async_to_sync(log_chat_message)(user_id, message, json.dumps(response_data), intent)
#             return JsonResponse(response_data, status=500)

#         print(f"Gemini Raw: {bot_reply_text}")
        
#         # ------------------------
#         # 6️⃣ Parse Gemini's JSON Response
#         # ------------------------
#         json_response = extract_json_action(bot_reply_text)

#         if not json_response:
#             print("Failed to parse JSON from Gemini. Sending text fallback.")
#             fallback_text = bot_reply_text.strip().strip("`").replace("json", "").strip()
#             response_data = {"type": "text", "payload": fallback_text or "Sorry, I had a problem with my response. Could you rephrase?"}
#             async_to_sync(log_chat_message)(user_id, message, json.dumps(response_data), intent)
#             return JsonResponse(response_data, status=200)

#         # ------------------------
#         # 7️⃣ --- ACTION HANDLER ---
#         # ------------------------
#         # ------------------------
# # product_list handler (fixed)
# # ------------------------
#         # ---------- REPLACE your existing product_list handler with this block ----------
#         if json_response and json_response.get("type") == "product_list":
#             payload = json_response.get("payload", {})

#             try:
#                 products_data = []

#                 # CASE A: payload is a list of dicts (Gemini returned full product objects)
#                 if isinstance(payload, list) and payload and isinstance(payload[0], dict):
#                     # Validate & normalize minimal fields so frontend gets consistent shapes
#                     normalized = []
#                     for p in payload:
#                         normalized.append({
#                             "product_id": p.get("product_id"),
#                             "name": p.get("name"),
#                             "description": p.get("description"),
#                             "price": p.get("price"),
#                             "stock": p.get("stock"),
#                             "rating": p.get("rating"),
#                             "type": p.get("type"),
#                             "style": p.get("style"),
#                             "color": p.get("color"),
#                             "category": p.get("category"),
#                             "image_url": p.get("image_url"),
#                         })
#                     products_data = normalized

#                 # CASE B: payload is a list of ids (e.g. [1,2,3])
#                 elif isinstance(payload, list) and payload and all(isinstance(x, (int, str)) for x in payload):
#                     def _fetch_by_ids():
#                         return supabase.table("products").select(
#                             "product_id, name, description, price, stock, rating, type, style, color, category, image_url"
#                         ).in_("product_id", payload).execute()
#                     # _fetch_by_ids is synchronous, so call via async_to_sync wrapper and call it
#                     res = async_to_sync(_fetch_by_ids)()
#                     products_data = res.data or []

#                 # CASE C: payload is a dict with filters -> use existing filter function
#                 elif isinstance(payload, dict):
#                     res = async_to_sync(get_filtered_products)(payload)
#                     # get_filtered_products returns a supabase result object; normalize
#                     products_data = getattr(res, "data", res) or []

#                 else:
#                     # Unknown payload shape -> fallback to top N products
#                     def _top10():
#                         return supabase.table("products").select(
#                             "product_id, name, description, price, stock, rating, type, style, color, category, image_url"
#                         ).limit(10).execute()
#                     res = async_to_sync(_top10)()
#                     products_data = res.data or []

#             except Exception as e:
#                 print(f"Product_list handler error: {e}")
#                 response_data = {"type": "text", "payload": "Sorry, I couldn't fetch the products right now."}
#                 async_to_sync(log_chat_message)(user_id, message, json.dumps(response_data), intent)
#                 return JsonResponse(response_data, status=500)

#             response_data = {"type": "product_list", "payload": products_data}
#             async_to_sync(log_chat_message)(user_id, message, json.dumps(response_data), intent)
#             return JsonResponse(response_data, status=200)
#         # ---------- end replacement ----------



#         if json_response.get("type") == "action":
#             payload = json_response.get("payload", {})
#             action_name = payload.get("action_name")
            
#             try:
#                 if action_name == "update_profile":
#                     updates = payload.get("updates", {})
#                     if not updates:
#                         response_data = {"type": "text", "payload": "I'm not sure what you wanted to update. Please be more specific."}
#                     else:
#                         res = async_to_sync(supabase_update)("users", updates, "user_id", user_id)
#                         if res.get("success"):
#                             response_data = {"type": "text", "payload": "I've successfully updated your profile."}
#                         else:
#                             response_data = {"type": "text", "payload": f"I failed to update your profile: {res.get('error')}"}

#                 elif action_name == "create_complaint":
#                     params = payload.get("params", {})
#                     description = params.get("description")
#                     order_id = params.get("order_id")

#                     if not description:
#                         # If description is missing, ask for it.
#                         response_data = {"type": "text", "payload": "I can help you file a complaint. Could you please describe the issue you are facing?"}
#                     else:
#                         # Description is present, proceed with filing.
#                         complaint_payload = {
#                             "user_id": user_id,
#                             "order_id": order_id, # This is fine if it's None, assuming DB allows null
#                             "description": description,
#                             "status": "open",
#                         }
#                         res = async_to_sync(supabase_insert)("complaints_updated", complaint_payload)
#                         if res.get("success"):
#                             response_data = {"type": "text", "payload": f"I've filed your complaint. The reference ID is {res['data'][0].get('complaint_id')}."}
#                         else:
#                             response_data = {"type": "text", "payload": f"I failed to file your complaint: {res.get('error')}"}

#                 elif action_name == "schedule_meeting":
#                     params = payload.get("params", {})
#                     meeting_payload = {
#                         "user_id": user_id,
#                         "support_person": params.get("support_person", "Support Team"),
#                         "scheduled_time": params.get("scheduled_time"),
#                         "status": "scheduled",
#                     }
#                     res = async_to_sync(supabase_insert)("meeting", meeting_payload)
#                     if res.get("success"):
#                         response_data = {"type": "text", "payload": "Your meeting has been scheduled."}
#                     else:
#                         response_data = {"type": "text", "payload": f"I failed to schedule your meeting: {res.get('error')}"}

#                 elif action_name == "schedule_return":
#                     params = payload.get("params", {})
#                     return_payload = {
#                         "user_id": user_id,
#                         "order_id": params.get("order_id"),
#                         "product_id": params.get("product_id"),
#                         "reason": params.get("reason"),
#                         "status": "requested",
#                     }
#                     res = async_to_sync(supabase_insert)("returns", return_payload)
#                     if res.get("success"):
#                         response_data = {"type": "text", "payload": "Your return request has been submitted."}
#                     else:
#                         response_data = {"type": "text", "payload": f"I failed to submit your return request: {res.get('error')}"}
                
#                 elif action_name == "add_to_cart":
#                     params = payload.get("params", {}) or {}
#                     product_id = params.get("product_id")
#                     try:
#                         quantity = int(params.get("quantity", 1))
#                     except (TypeError, ValueError):
#                         quantity = 1

#                     if not product_id:
#                         response_data = {"type": "text", "payload": "You mentioned adding a product, but I'm missing the product ID."}
#                         async_to_sync(log_chat_message)(user_id, message, json.dumps(response_data), intent)
#                         return JsonResponse(response_data, status=200)
#                     else:
#                         # --- FIX: Check if product exists FIRST ---
#                         product_info = async_to_sync(supabase_select_one)("products", "name, price, stock", "product_id", product_id)
#                         if not product_info:
#                             response_data = {"type": "text", "payload": f"I'm sorry, I can't find a product with ID {product_id}."}
#                             async_to_sync(log_chat_message)(user_id, message, json.dumps(response_data), intent)
#                             return JsonResponse(response_data, status=200)
#                         else:
#                             try:
#                                 # See if item already in cart
#                                 existing_item_list = async_to_sync(supabase_select)(
#                                     "cart_items",
#                                     "cart_item_id, quantity",
#                                     {"user_id": user_id, "product_id": product_id}
#                                 )
#                                 existing_item = existing_item_list[0] if existing_item_list else None

#                                 if existing_item:
#                                     new_quantity = int(existing_item.get('quantity', 0)) + quantity
#                                     update_payload = {"quantity": new_quantity}
#                                     res = async_to_sync(supabase_update)("cart_items", update_payload, "cart_item_id", existing_item['cart_item_id'])
#                                 else:
#                                     cart_payload = {
#                                         "user_id": user_id,
#                                         "product_id": product_id,
#                                         "quantity": quantity
#                                     }
#                                     res = async_to_sync(supabase_insert)("cart_items", cart_payload)

#                                 # Check DB response
#                                 if not res or not res.get("success"):
#                                     # Log DB error and return friendly message
#                                     err = res.get("error") if isinstance(res, dict) else str(res)
#                                     print("Add to cart DB error:", err)
#                                     response_data = {"type": "text", "payload": f"I failed to add the item to your cart: {err}"}
#                                     async_to_sync(log_chat_message)(user_id, message, json.dumps(response_data), intent)
#                                     return JsonResponse(response_data, status=500)

#                                 # Success — now fetch and return the current cart items for this user (normalized array)
#                                 def _fetch_cart():
#                                     # select cart_items and nested product fields: this matches your cart_items FK to products
#                                     return supabase.table("cart_items").select(
#                                         "cart_item_id, product_id, quantity, products(product_id, name, price, image_url, stock)"
#                                     ).eq("user_id", user_id).execute()

#                                 # Call the sync supabase client directly (this is not async in your setup)
#                                 cart_res = _fetch_cart()
#                                 cart_rows = getattr(cart_res, "data", []) or []

#                                 normalized = []
#                                 total = 0.0
#                                 for r in cart_rows:
#                                     prod = r.get("products") or {}
#                                     # Safe parsing
#                                     try:
#                                         price = float(prod.get("price") or 0.0)
#                                     except (TypeError, ValueError):
#                                         price = 0.0
#                                     try:
#                                         qty = int(r.get("quantity") or 0)
#                                     except (TypeError, ValueError):
#                                         qty = 0
#                                     subtotal = price * qty
#                                     total += subtotal

#                                     normalized.append({
#                                         "cart_item_id": r.get("cart_item_id"),
#                                         "product_id": r.get("product_id"),
#                                         "product_name": prod.get("name"),
#                                         "quantity": qty,
#                                         "price": price,
#                                         "image_url": prod.get("image_url"),
#                                         "stock": prod.get("stock"),
#                                         "subtotal": round(subtotal, 2)
#                                     })

#                                 # --- IMPORTANT: frontend expects payload to be an array (RenderCartItems checks Array.isArray)
#                                 response_data = {"type": "cart_items", "payload": normalized, "total": round(total, 2)}
#                                 async_to_sync(log_chat_message)(user_id, message, json.dumps(response_data), intent)
#                                 return JsonResponse(response_data, status=200)

#                             except Exception as e:
#                                 print(f"Add to cart handler error: {e}")
#                                 response_data = {"type": "text", "payload": "Something went wrong while adding the item to the cart."}
#                                 async_to_sync(log_chat_message)(user_id, message, json.dumps(response_data), intent)
#                                 return JsonResponse(response_data, status=500)

#                 elif action_name == "create_order":
#                     res = async_to_sync(create_order_from_cart)(user_id)
#                     if res.get("success"):
#                         response_data = {"type": "text", "payload": f"Success! Your order (ID: {res['order_id']}) has been placed for a total of ${res['total']:.2f}."}
#                     else:
#                         response_data = {"type": "text", "payload": f"I failed to create your order: {res.get('error')}"}

#                 else:
#                     response_data = {"type": "text", "payload": f"I understood you wanted an action ({action_name}), but I don't know how to do that yet."}

#             except Exception as e:
#                 print(f"Action Handler Error: {e}")
#                 response_data = {"type": "text", "payload": "Something went wrong while I was trying to complete that action."}
            
#             # This is now an action response, log it and return
#             async_to_sync(log_chat_message)(user_id, message, json.dumps(response_data), intent)
#             return JsonResponse(response_data, status=200)

#         # ------------------------
#         # 8️⃣ Return the valid (non-action) JSON to the frontend
#         # ------------------------
#         async_to_sync(log_chat_message)(user_id, message, json.dumps(json_response), intent)
#         return JsonResponse(json_response, status=200)

#     except Exception as e:
#         # --- FINAL CATCH-ALL ---
#         print(f"Unhandled server error: {e}")
#         response_data = {"type": "text", "payload": "A critical server error occurred. Please contact support."}
#         # Try to log one last time
#         try:
#             async_to_sync(log_chat_message)(user_id, message, json.dumps(response_data), "critical_error")
#         except Exception as log_e:
#             print(f"Failed to log critical error: {log_e}")
#         return JsonResponse(response_data, status=500)


import os
import json
import asyncio
import jwt
from jwt.exceptions import InvalidTokenError
from django.http import JsonResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from supabase import create_client, Client
from typing import Optional, Any, Dict, List
import google.generativeai as genai
# from .chatbot_logic import detect_intent, get_context_data
from .chatbot_logic import detect_intent, get_context_data, get_filtered_products

from asgiref.sync import async_to_sync
from datetime import datetime, timezone  # --- NEW: Import for timestamp ---


# -------------------------------
# INITIAL SETUP
# -------------------------------
SUPABASE_URL = settings.SUPABASE_URL
SUPABASE_SERVICE_KEY = settings.SUPABASE_SERVICE_KEY
SUPABASE_JWT_SECRET = settings.SUPABASE_JWT_SECRET

#  SUPABASE_URL and SUPABASE_SERVICE_KEY
if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
    raise ValueError("Supabase URL and Service Key must be set in settings.")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

if os.getenv("GEMINI_API_KEY"):
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))


# -------------------------------
# JWT VERIFICATION (LOCAL)
# -------------------------------
def verify_supabase_jwt(token: str) -> Optional[dict]:
    """
    Verify Supabase JWT using configured secret (HS256).
    Returns decoded payload dict on success, else None.
    """
    if not token:
        return None

    try:
        decoded = jwt.decode(
            token,
            SUPABASE_JWT_SECRET,
            algorithms=["HS256"],
            options={"verify_aud": False}
        )
        print("✅ Decoded token:", decoded)
        return decoded
    except jwt.ExpiredSignatureError:
        print("❌ Token expired")
        return None
    except jwt.InvalidTokenError as e:
        # If verification fails
        try:
            decoded = jwt.decode(token, options={"verify_signature": False})
            print("⚠️ Token signature invalid, decoded without verification:", decoded)
            return None
        except Exception:
            print("❌ Invalid token:", str(e))
            return None


# -------------------------------
# ASYNC SUPABASE HELPERS
# -------------------------------

async def supabase_select_one(table: str, select: str, eq_col: str, eq_val) -> Optional[dict]:
    def _fn():
        return supabase.table(table).select(select).eq(eq_col, eq_val).limit(1).execute()
    res = await asyncio.to_thread(_fn)
    return res.data[0] if res.data else None


async def supabase_select(table: str, select: str = "*", filters: Dict[str, Any] = None) -> List[dict]:
    """
    Selects data from a table with multiple .eq() filters.
    """
    def _fn():
        query = supabase.table(table).select(select)
        if filters:
            for col, val in filters.items():
                query = query.eq(col, val)
        return query.execute()
    res = await asyncio.to_thread(_fn)
    return res.data or []


async def supabase_insert(table: str, payload: dict) -> dict:
    def _fn():
        return supabase.table(table).insert(payload).execute()
    res = await asyncio.to_thread(_fn)
    if hasattr(res, "data") and res.data:
        return {"success": True, "data": res.data}
    return {"success": False, "error": getattr(res, "error", str(res))}


async def supabase_update(table: str, payload: dict, eq_col: str, eq_val) -> dict:
    def _fn():
        return supabase.table(table).update(payload).eq(eq_col, eq_val).execute()
    res = await asyncio.to_thread(_fn)
    if hasattr(res, "data") and res.data:
        return {"success": True, "data": res.data}
    return {"success": False, "error": getattr(res, "error", str(res))}


async def supabase_delete(table: str, filters: Dict[str, Any] = None) -> dict:
    """
    Deletes data from a table with multiple .eq() filters.
    """
    def _fn():
        query = supabase.table(table).delete()
        if filters:
            for col, val in filters.items():
                query = query.eq(col, val)
        return query.execute()
    res = await asyncio.to_thread(_fn)
    if hasattr(res, "data") and res.data:
        return {"success": True, "data": res.data}
    return {"success": False, "error": getattr(res, "error", str(res))}


# ---  Get chat history ---
async def get_recent_chat_history(user_id: int) -> List[dict]:
    """
    Fetches the last 5 messages for a user to provide context.
    """
    def _fn():
        return supabase.table("chat_logs_updated").select("user_message, bot_response").eq("user_id", user_id).order("timestamp", desc=True).limit(5).execute()

    res = await asyncio.to_thread(_fn)
    # Return in reverse order to be chronological (oldest to newest)
    return (res.data or [])[::-1]


# ---  Log chat message ---
async def log_chat_message(user_id: Optional[int], user_message: str, bot_response: str, intent: str):
    """
    Logs the conversation to the chat_logs_updated table.
    """
    log_payload = {
        "user_id": user_id,
        "user_message": user_message,
        "bot_response": bot_response,  # This is the JSON string of the response
        "intent_detected": intent,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    # Fire-and-forget logging
    try:
        await supabase_insert("chat_logs_updated", log_payload)
        print(f"Logged chat for user {user_id}")
    except Exception as e:
        print(f"Failed to log chat: {e}")


# -------------------------------
# USER AUTH ROUTES
# -------------------------------

@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    """Signup: Register new user into Supabase 'users' table."""
    data = request.data
    try:
        existing = async_to_sync(supabase_select_one)("users", "user_id", "email", data["email"])
        if existing:
            return JsonResponse({"error": "User already exists"}, status=400)

        payload = {
            # --- FIX: Removed "user_id": next_id. DB will assign it. ---
            "name": data.get("username"),
            "email": data.get("email"),
            "password_hash": data.get("password"),  # Hash in production
            "phone": "",
            "address": "",
            "city": "",
            "state": "",
            "pincode": "",
        }
        # --- FIX: Use async_to_sync to call async helper ---
        result = async_to_sync(supabase_insert)("users", payload)

        if not result.get("success"):
            return JsonResponse({"error": str(result.get("error"))}, status=400)

        return JsonResponse({"message": "User registered successfully"}, status=201)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)


@api_view(['POST'])
@permission_classes([AllowAny])
def login_user(request):
    """
    Login route — Supabase Auth handles the JWT issuance on frontend.
    This backend view is for manual (email/pass) auth if not using Supabase client.
    """
    data = request.data
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return JsonResponse({"error": "Email and password required"}, status=400)

    user = async_to_sync(supabase_select_one)("users", "user_id,email", "email", email)
    if not user:
        return JsonResponse({"error": "Invalid credentials"}, status=401)

    payload = {"email": email, "sub": user["user_id"], "user_metadata": user}
    token = jwt.encode(payload, SUPABASE_JWT_SECRET, algorithm="HS256")

    return JsonResponse({"access_token": token, "message": "Login successful"})


@api_view(['POST'])
@permission_classes([AllowAny])
def forgot_password(request):
    """Stub forgot password API (to be expanded later)."""
    email = request.data.get("email")
    if not email:
        return JsonResponse({"error": "Email required"}, status=400)
    # You can trigger Supabase reset email here using supabase.auth.reset_password_for_email(email)
    return JsonResponse({"message": f"Password reset link sent to {email}"})


@api_view(['GET'])
def get_profile(request):  # --- FIX: Made sync 'def' ---
    """Get user profile after verifying Supabase JWT."""
    auth_header = request.headers.get("Authorization")

    if not auth_header or not auth_header.startswith("Bearer "):
        return JsonResponse({"error": "Missing or invalid token"}, status=401)

    token = auth_header.split(" ")[1]
    decoded = verify_supabase_jwt(token)

    if not decoded:
        return JsonResponse({"error": "Invalid or expired token"}, status=401)

    # The profile data is already in the token.
    user_data = decoded.get("user_metadata")

    if not user_data:
        # Fallback if user_metadata isn't in the token
        email = decoded.get("email")
        if not email:
            return JsonResponse({"error": "Invalid token payload"}, status=400)

        user = async_to_sync(supabase_select_one)("users", "*", "email", email)

        if not user:
            return JsonResponse({"error": "User not found in DB, though token is valid"}, status=404)  # 404
        user_data = user

    if 'id' not in user_data:
        user_data['id'] = decoded.get('sub')
    if 'email' not in user_data:
        user_data['email'] = decoded.get('email')

    return JsonResponse(user_data, status=200)


# -------------------------------
# GEMINI + CHATBOT SECTION
# -------------------------------

def extract_json_action(text: str) -> Optional[dict]:
    """Extract embedded JSON action block from model response."""
    if not text:
        return None
    text = text.strip()
    # Find the first { and the last }
    start = text.find("{")
    end = text.rfind("}") + 1
    if start == -1 or end == -1:
        return None  # No JSON found

    json_str = text[start:end]
    try:
        # Try to parse the extracted string
        obj = json.loads(json_str)
        return obj  # Return the parsed JSON object
    except json.JSONDecodeError:
        print(f"Failed to decode JSON: {json_str}")
        pass
    return None


async def call_gemini(prompt: str) -> str:
    """Call Gemini asynchronously."""
    def _fn():
        try:
            model = genai.GenerativeModel("gemini-2.5-flash-preview-09-2025")
            res = model.generate_content(prompt)
            return getattr(res, "text", str(res))
        except Exception as e:
            print(f"GEMINI ERROR: {e}")
            return json.dumps({"type": "text", "payload": "Sorry, I'm having trouble connecting to my brain. Please try again."})

    return await asyncio.to_thread(_fn)


async def create_order_from_cart(user_id: int) -> dict:
    """
    Complex action:
    1. Read user's cart
    2. Get product prices
    3. Calculate total
    4. Create 'orders' entry
    5. Create 'order_items' entries
    6. Clear user's cart
    """
    # 1. Read cart
    cart_items = await supabase_select("cart_items", "product_id,quantity", {"user_id": user_id})
    if not cart_items:
        return {"success": False, "error": "Your cart is empty."}

    # 2. Get product prices
    product_ids = [item['product_id'] for item in cart_items]

    def _get_products():
        return supabase.table("products").select("product_id, name, price").in_("product_id", product_ids).execute()

    product_res = await asyncio.to_thread(_get_products)
    if not product_res.data:
        return {"success": False, "error": "Could not find product details for items in your cart."}

    product_price_map = {p['product_id']: p['price'] for p in product_res.data}
    product_name_map = {p['product_id']: p['name'] for p in product_res.data}

    # 3. Calculate total
    total_amount = 0
    order_items_payload = []

    for item in cart_items:
        product_id = item['product_id']
        quantity = item['quantity']
        price = product_price_map.get(product_id)

        if not price and price != 0:
            print(f"Price for product_id {product_id} not found. Skipping.")
            continue

        total_amount += price * quantity
        order_items_payload.append({
            # "order_id" will be added after we create the order
            "product_id": product_id,
            "quantity": quantity,
            "price_at_order": price
        })

    if not order_items_payload:
        return {"success": False, "error": "No valid items to order."}

    # 4. Create 'orders' entry
    user_profile = await supabase_select_one("users", "address,city,state,pincode", "user_id", user_id)
    shipping_address = f"{user_profile.get('address', '')}, {user_profile.get('city', '')}, {user_profile.get('state', '')} {user_profile.get('pincode', '')}"

    order_payload = {
        "user_id": user_id,
        "status": "Pending",  # Or "Confirmed"
        "total_amount": total_amount,
        "shipping_address": shipping_address,
        "payment_method": "Pending"  # Assuming payment is handled elsewhere
    }

    order_res = await supabase_insert("orders", order_payload)
    if not order_res.get("success"):
        return {"success": False, "error": f"Failed to create order: {order_res.get('error')}"}

    new_order_id = order_res['data'][0]['order_id']

    # 5. Create 'order_items' entries
    for item in order_items_payload:
        item['order_id'] = new_order_id

    insert_items_res = await supabase_insert("order_items", order_items_payload)
    if not insert_items_res.get("success"):
        # This is bad, we created an order with no items.
        # A real app would "roll back" the order creation.
        print(f"Failed to insert order_items: {insert_items_res.get('error')}")
        return {"success": False, "error": "Created order but failed to add items."}

    # 6. Clear user's cart
    await supabase_delete("cart_items", {"user_id": user_id})

    return {"success": True, "order_id": new_order_id, "total": total_amount}


@csrf_exempt
@api_view(['POST'])  # Add the decorator
def chatbot(request):  # --- FIX: Changed to sync 'def' ---
    """Daksha.ai chatbot endpoint."""

    # Define early for logging
    user_id = None
    intent = "unknown"
    message = ""

    try:
        # ------------------------
        # 1️⃣ Parse input
        # ------------------------
        try:
            body = json.loads(request.body.decode("utf-8"))
            message = body.get("message", "").strip()
        except Exception:
            response_data = {"error": "Invalid JSON"}
            async_to_sync(log_chat_message)(user_id, message, json.dumps(response_data), intent)
            return JsonResponse(response_data, status=400)

        if not message:
            response_data = {"error": "Message required"}
            async_to_sync(log_chat_message)(user_id, message, json.dumps(response_data), intent)
            return JsonResponse(response_data, status=400)

        # ------------------------
        # 2️⃣ Verify JWT and Get User
        # ------------------------
        auth_header = request.headers.get("Authorization", "")
        user_info = None
        user_email = None

        if not auth_header.startswith("Bearer "):
            response_data = {"error": "Authorization token missing"}
            async_to_sync(log_chat_message)(user_id, message, json.dumps(response_data), intent)
            return JsonResponse(response_data, status=401)

        token = auth_header.split(" ")[1]
        user_info = verify_supabase_jwt(token)

        if not user_info:
            response_data = {"error": "Invalid or expired token"}
            async_to_sync(log_chat_message)(user_id, message, json.dumps(response_data), intent)
            return JsonResponse(response_data, status=401)

        user_email = user_info.get("email")
        if not user_email:
            response_data = {"error": "Invalid token payload, email missing"}
            async_to_sync(log_chat_message)(user_id, message, json.dumps(response_data), intent)
            return JsonResponse(response_data, status=400)

        # --- JIT User Provisioning ---
        row = async_to_sync(supabase_select_one)("users", "user_id,email", "email", user_email)

        if not row:
            print(f"User not found in 'users' table. Provisioning: {user_email}")
            try:
                # --- FIX: Removed get_next_user_id ---
                new_user_payload = {
                    # --- FIX: Removed "user_id". DB will assign it. ---
                    "email": user_email,
                    "name": user_info.get("user_metadata", {}).get("name", "New User"),
                }
                insert_res = async_to_sync(supabase_insert)("users", new_user_payload)

                if not insert_res.get("success"):
                    print(f"Failed to provision user: {insert_res.get('error')}")
                    response_data = {"error": "User provisioning failed."}
                    async_to_sync(log_chat_message)(user_id, message, json.dumps(response_data), intent)
                    return JsonResponse(response_data, status=500)

                # --- FIX: Get the new user_id from the insert response ---
                user_id = insert_res['data'][0]['user_id']
                print(f"Provisioned new user with user_id: {user_id}")

            except Exception as e:
                print(f"Error during JIT provisioning: {e}")
                response_data = {"error": "Error creating user profile."}
                async_to_sync(log_chat_message)(user_id, message, json.dumps(response_data), intent)
                return JsonResponse(response_data, status=500)
        else:
            user_id = row.get("user_id")

        if not user_id:
            response_data = {"error": "Could not determine user ID"}
            async_to_sync(log_chat_message)(user_id, message, json.dumps(response_data), intent)
            return JsonResponse(response_data, status=500)

        # ------------------------
        # 3️⃣ Intent detection & context
        # ------------------------
        try:
            intent = detect_intent(message)
            # get_context_data is synchronous in chatbot_logic.py — call it directly
            context = get_context_data(intent, user_id)
        except Exception as e:
            print(f"Context/Intent Error: {e}")
            intent = "general_error"
            context = {"error": "Failed to get context."}

        # ------------------------
        # Short-circuit common read-only intents to avoid LLM involvement
        # ------------------------
        if intent in ("cart", "orders", "account", "shipping", "cart_total"):
            try:
                # CART — frontend expects payload to be an array for cart_items
                if intent == "cart":
                    # get_context_data returns {"cart_items": [...], "total": n} or {"error": "..."}
                    cart_ctx = context if isinstance(context, dict) else {}
                    items = cart_ctx.get("cart_items", []) if isinstance(cart_ctx, dict) else []
                    total = cart_ctx.get("total", 0)
                    # Normalize: frontend RenderCartItems expects payload = array of items
                    response_data = {"type": "cart_items", "payload": items, "total": total}

                # ORDERS — return list of orders (frontend uses order_list renderer)
                elif intent == "orders":
                    orders = context if isinstance(context, list) else (context.get("orders") if isinstance(context, dict) else [])
                    # If get_context_data returned a dict, try common keys
                    if isinstance(context, dict) and not orders:
                        orders = context.get("orders") or context.get("order_list") or []
                    response_data = {"type": "order_list", "payload": orders}

                # ACCOUNT / PROFILE
                elif intent == "account":
                    profile = context if isinstance(context, dict) else {}
                    response_data = {"type": "profile_data", "payload": profile}

                # CART TOTAL (explicit)
                elif intent == "cart_total":
                    cart_ctx = context if isinstance(context, dict) else {}
                    total = cart_ctx.get("total", 0)
                    response_data = {"type": "text", "payload": f"Your cart total is ${float(total):.2f}"}

                # SHIPPING: try to parse an order id from the message; else return recent orders
                elif intent == "shipping":
                    import re
                    m = re.search(r"order\s*#?\s*(\d+)", message, re.IGNORECASE)
                    if m:
                        order_id = int(m.group(1))
                        # Use existing helper to fetch a single order
                        order_row = async_to_sync(supabase_select_one)("orders", "*", "order_id", order_id)
                        if order_row and order_row.get("user_id") == user_id:
                            ship_addr = order_row.get("shipping_address") or "N/A"
                            expect = order_row.get("expected_delivery")
                            response_data = {"type": "text", "payload": f"Order {order_id} — Shipping address: {ship_addr}. Expected delivery: {expect}"}
                        else:
                            response_data = {"type": "text", "payload": f"Order {order_id} not found (or doesn't belong to you)."}
                    else:
                        # No order id — show recent orders (reuse 'orders' intent context)
                        orders_list = context if isinstance(context, list) else []
                        response_data = {"type": "order_list", "payload": orders_list}

                # Log and return the short-circuited response
                async_to_sync(log_chat_message)(user_id, message, json.dumps(response_data), intent)
                return JsonResponse(response_data, status=200)

            except Exception as e:
                # If short-circuit fails, print and fall through to LLM handling
                print("Short-circuit read-intent error:", e)

        product_schema_info = """
Product Table Schema:
- product_id: integer primary key
- name: string
- description: text
- price: numeric
- stock: integer
- rating: numeric
- type: textual type (e.g., Kurta, Shirt, Jeans)
- style: style (Ethnic, Western, Formal, Casual, Fusion)
- color: color name (Black, Blue, etc.)
- category: Men/Women/Kids/Unisex
- image_url: url to product image (frontend can render)
When asking for product recommendations, prefer the fields: name, price, style, color, image_url.
If user asks "show ethnic black wear", return a "product_list" type with payload being filter criteria, e.g. {"style":"Ethnic","color":"Black"}.
"""
        # --- FIX: Fetch and format chat history ---
        chat_history_list = async_to_sync(get_recent_chat_history)(user_id)
        chat_history_string = ""
        if chat_history_list:
            for entry in chat_history_list:
                chat_history_string += f"User: {entry.get('user_message')}\n"
                chat_history_string += f"Bot: {entry.get('bot_response')}\n"
        else:
            chat_history_string = "No recent history."
        # --- END FIX ---

        # ------------------------
        # 4️⃣ Build prompt for Gemini (JSON Mode)
        # ------------------------
        prompt = f"""
You are Daksha, a helpful customer support assistant and a Product recommender for an e-commerce website called Dukaan.
{product_schema_info}
You MUST ONLY respond with a valid JSON object.
Your goal is to either DISPLAY information or perform an ACTION.

SCHEMA:
{{"type": "response_type", "payload": "response_payload"}}

## 1. DISPLAYING INFORMATION
If the user asks for data (like "show my profile", "what's in my cart"), respond with a display type.
- "type" can be: "text", "profile_data", "product_list", "cart_items", "order_list", "complaint_list", "return_list", "action_options".
- "payload" contains the data for the frontend to render.

EXAMPLES (DISPLAY):
User: "Hi" -> {{"type": "text", "payload": "Hello! How can I help you today?"}}
User: "Show my profile" -> {{"type": "profile_data", "payload": {{"name": "Jane Doe", "email": "jane@example.com"}}}}
User: "What can I do?" -> {{"type": "action_options", "payload": ["View Profile", "Check Orders", "See Cart", "File Complaint"]}}

## 2. PERFORMING ACTIONS
If the user's message is a clear, actionable request (like "update my profile", "add to cart", "checkout"), respond with type "action".
- "type" MUST be "action".
- "payload" MUST contain:
    - "action_name": The action to perform (e.g., "update_profile", "schedule_return", "schedule_meeting", "create_complaint", "add_to_cart", "create_order").
    - "updates" or "params": The data extracted from the user's message.

* For "update_profile", valid keys for "updates" are: "name", "phone", "address", "city", "state", "pincode".
* For "add_to_cart", get "product_id" and "quantity" (default 1).
* For "create_complaint", get "description". If "order_id" is mentioned, get it.
* For "create_order", the user just needs to say "checkout" or "order my cart". No params needed.

EXAMPLES (ACTION):
User: "Please update my address to 22, east street, pune"
Response:
{{"type": "action", "payload": {{"action_name": "update_profile", "updates": {{"address": "22, east street, pune", "city": "pune"}}}}}}

User: "add product 10 to my cart"
Response:
{{"type": "action", "payload": {{"action_name": "add_to_cart", "params": {{"product_id": 10, "quantity": 1}}}}}}

User: "I want to checkout" or "I want to order my cart"
Response:
{{"type": "action", "payload": {{"action_name": "create_order", "params": {{}}}}}}

## 3. MULTI-TURN CONVERSATIONS (Slot-filling)
Use the RECENT CHAT HISTORY to understand context for multi-turn requests.
If the user's request is an action but is missing information, ask a follow-up question using the "text" type.

User: "I want to update my profile"
Response:
{{"type": "text", "payload": "Great, what information would you like to update?"}}

User: "my shipping address"
Response:
{{"type": "text", "payload": "Okay, what is the new shipping address?"}}

User: "22, east street, pune"
Response:
{{"type": "action", "payload": {{"action_name": "update_profile", "updates": {{"address": "22, east street, pune", "city": "pune"}}}}}}

User: "I want to file a complaint."
Response:
{{"type": "text", "payload": "I can help with that. What is the complaint about?"}}

User: "My order 123 was damaged."
Response:
{{"type": "action", "payload": {{"action_name": "create_complaint", "params": {{"order_id": 123, "description": "Order 123 was damaged"}}}}}}

User: "The website is slow."
Response:
{{"type": "action", "payload": {{"action_name": "create_complaint", "params": {{"description": "The website is slow"}}}}}} 

## 4. CONTEXT
- User ID: {user_id}
- User Intent: {intent}
- Database Context: {json.dumps(context)}

## 5. RECENT CHAT HISTORY (Oldest to Newest)
{chat_history_string}


## 6. CURRENT USER MESSAGE
"{message}"

JSON RESPONSE:
"""

        # ------------------------
        # 5️⃣ Call Gemini safely
        # ------------------------
        try:
            bot_reply_text = async_to_sync(call_gemini)(prompt)
        except Exception as e:
            print(f"Gemini Error: {e}")
            response_data = {"type": "text", "payload": "Sorry, I'm having an issue connecting. Please try again."}
            async_to_sync(log_chat_message)(user_id, message, json.dumps(response_data), intent)
            return JsonResponse(response_data, status=500)

        print(f"Gemini Raw: {bot_reply_text}")

        # ------------------------
        # 6️⃣ Parse Gemini's JSON Response
        # ------------------------
        json_response = extract_json_action(bot_reply_text)

        if not json_response:
            print("Failed to parse JSON from Gemini. Sending text fallback.")
            fallback_text = bot_reply_text.strip().strip("`").replace("json", "").strip()
            response_data = {"type": "text", "payload": fallback_text or "Sorry, I had a problem with my response. Could you rephrase?"}
            async_to_sync(log_chat_message)(user_id, message, json.dumps(response_data), intent)
            return JsonResponse(response_data, status=200)

        # ------------------------
        # 7️⃣ --- ACTION HANDLER ---
        # ------------------------
        # ------------------------
        # product_list handler (fixed)
        # ------------------------
        # ---------- REPLACE your existing product_list handler with this block ----------
        if json_response and json_response.get("type") == "product_list":
            payload = json_response.get("payload", {})

            try:
                products_data = []

                # CASE A: payload is a list of dicts (Gemini returned full product objects)
                if isinstance(payload, list) and payload and isinstance(payload[0], dict):
                    # Validate & normalize minimal fields so frontend gets consistent shapes
                    normalized = []
                    for p in payload:
                        normalized.append({
                            "product_id": p.get("product_id"),
                            "name": p.get("name"),
                            "description": p.get("description"),
                            "price": p.get("price"),
                            "stock": p.get("stock"),
                            "rating": p.get("rating"),
                            "type": p.get("type"),
                            "style": p.get("style"),
                            "color": p.get("color"),
                            "category": p.get("category"),
                            "image_url": p.get("image_url"),
                        })
                    products_data = normalized

                # CASE B: payload is a list of ids (e.g. [1,2,3])
                elif isinstance(payload, list) and payload and all(isinstance(x, (int, str)) for x in payload):
                    def _fetch_by_ids():
                        return supabase.table("products").select(
                            "product_id, name, description, price, stock, rating, type, style, color, category, image_url"
                        ).in_("product_id", payload).execute()
                    # _fetch_by_ids is synchronous, so call via async_to_sync wrapper and call it
                    res = async_to_sync(_fetch_by_ids)()
                    products_data = res.data or []

                # CASE C: payload is a dict with filters -> use existing filter function
                elif isinstance(payload, dict):
                    res = async_to_sync(get_filtered_products)(payload)
                    # get_filtered_products returns a supabase result object; normalize
                    products_data = getattr(res, "data", res) or []

                else:
                    # Unknown payload shape -> fallback to top N products
                    def _top10():
                        return supabase.table("products").select(
                            "product_id, name, description, price, stock, rating, type, style, color, category, image_url"
                        ).limit(10).execute()
                    res = async_to_sync(_top10)()
                    products_data = res.data or []

            except Exception as e:
                print(f"Product_list handler error: {e}")
                response_data = {"type": "text", "payload": "Sorry, I couldn't fetch the products right now."}
                async_to_sync(log_chat_message)(user_id, message, json.dumps(response_data), intent)
                return JsonResponse(response_data, status=500)

            response_data = {"type": "product_list", "payload": products_data}
            async_to_sync(log_chat_message)(user_id, message, json.dumps(response_data), intent)
            return JsonResponse(response_data, status=200)
        # ---------- end replacement ----------

        if json_response.get("type") == "action":
            payload = json_response.get("payload", {})
            action_name = payload.get("action_name")

            try:
                if action_name == "update_profile":
                    updates = payload.get("updates", {})
                    if not updates:
                        response_data = {"type": "text", "payload": "I'm not sure what you wanted to update. Please be more specific."}
                    else:
                        res = async_to_sync(supabase_update)("users", updates, "user_id", user_id)
                        if res.get("success"):
                            response_data = {"type": "text", "payload": "I've successfully updated your profile."}
                        else:
                            response_data = {"type": "text", "payload": f"I failed to update your profile: {res.get('error')}"}

                elif action_name == "create_complaint":
                    params = payload.get("params", {})
                    description = params.get("description")
                    order_id = params.get("order_id")

                    if not description:
                        # If description is missing, ask for it.
                        response_data = {"type": "text", "payload": "I can help you file a complaint. Could you please describe the issue you are facing?"}
                    else:
                        # Description is present, proceed with filing.
                        complaint_payload = {
                            "user_id": user_id,
                            "order_id": order_id,  # This is fine if it's None, assuming DB allows null
                            "description": description,
                            "status": "open",
                        }
                        res = async_to_sync(supabase_insert)("complaints_updated", complaint_payload)
                        if res.get("success"):
                            response_data = {"type": "text", "payload": f"I've filed your complaint. The reference ID is {res['data'][0].get('complaint_id')}."}
                        else:
                            response_data = {"type": "text", "payload": f"I failed to file your complaint: {res.get('error')}"}

                elif action_name == "schedule_meeting":
                    params = payload.get("params", {})
                    meeting_payload = {
                        "user_id": user_id,
                        "support_person": params.get("support_person", "Support Team"),
                        "scheduled_time": params.get("scheduled_time"),
                        "status": "scheduled",
                    }
                    res = async_to_sync(supabase_insert)("meeting", meeting_payload)
                    if res.get("success"):
                        response_data = {"type": "text", "payload": "Your meeting has been scheduled."}
                    else:
                        response_data = {"type": "text", "payload": f"I failed to schedule your meeting: {res.get('error')}"}

                elif action_name == "schedule_return":
                    params = payload.get("params", {})
                    return_payload = {
                        "user_id": user_id,
                        "order_id": params.get("order_id"),
                        "product_id": params.get("product_id"),
                        "reason": params.get("reason"),
                        "status": "requested",
                    }
                    res = async_to_sync(supabase_insert)("returns", return_payload)
                    if res.get("success"):
                        response_data = {"type": "text", "payload": "Your return request has been submitted."}
                    else:
                        response_data = {"type": "text", "payload": f"I failed to submit your return request: {res.get('error')}"}

                elif action_name == "add_to_cart":
                    params = payload.get("params", {}) or {}
                    product_id = params.get("product_id")
                    try:
                        quantity = int(params.get("quantity", 1))
                    except (TypeError, ValueError):
                        quantity = 1

                    if not product_id:
                        response_data = {"type": "text", "payload": "You mentioned adding a product, but I'm missing the product ID."}
                        async_to_sync(log_chat_message)(user_id, message, json.dumps(response_data), intent)
                        return JsonResponse(response_data, status=200)
                    else:
                        # --- FIX: Check if product exists FIRST ---
                        product_info = async_to_sync(supabase_select_one)("products", "name, price, stock", "product_id", product_id)
                        if not product_info:
                            response_data = {"type": "text", "payload": f"I'm sorry, I can't find a product with ID {product_id}."}
                            async_to_sync(log_chat_message)(user_id, message, json.dumps(response_data), intent)
                            return JsonResponse(response_data, status=200)
                        else:
                            try:
                                # See if item already in cart
                                existing_item_list = async_to_sync(supabase_select)(
                                    "cart_items",
                                    "cart_item_id, quantity",
                                    {"user_id": user_id, "product_id": product_id}
                                )
                                existing_item = existing_item_list[0] if existing_item_list else None

                                if existing_item:
                                    new_quantity = int(existing_item.get('quantity', 0)) + quantity
                                    update_payload = {"quantity": new_quantity}
                                    res = async_to_sync(supabase_update)("cart_items", update_payload, "cart_item_id", existing_item['cart_item_id'])
                                else:
                                    cart_payload = {
                                        "user_id": user_id,
                                        "product_id": product_id,
                                        "quantity": quantity
                                    }
                                    res = async_to_sync(supabase_insert)("cart_items", cart_payload)

                                # Check DB response
                                if not res or not res.get("success"):
                                    # Log DB error and return friendly message
                                    err = res.get("error") if isinstance(res, dict) else str(res)
                                    print("Add to cart DB error:", err)
                                    response_data = {"type": "text", "payload": f"I failed to add the item to your cart: {err}"}
                                    async_to_sync(log_chat_message)(user_id, message, json.dumps(response_data), intent)
                                    return JsonResponse(response_data, status=500)

                                # Success — now fetch and return the current cart items for this user (normalized array)
                                def _fetch_cart():
                                    # select cart_items and nested product fields: this matches your cart_items FK to products
                                    return supabase.table("cart_items").select(
                                        "cart_item_id, product_id, quantity, products(product_id, name, price, image_url, stock)"
                                    ).eq("user_id", user_id).execute()

                                # Call the sync supabase client directly (this is not async in your setup)
                                cart_res = _fetch_cart()
                                cart_rows = getattr(cart_res, "data", []) or []

                                normalized = []
                                total = 0.0
                                for r in cart_rows:
                                    prod = r.get("products") or {}
                                    # Safe parsing
                                    try:
                                        price = float(prod.get("price") or 0.0)
                                    except (TypeError, ValueError):
                                        price = 0.0
                                    try:
                                        qty = int(r.get("quantity") or 0)
                                    except (TypeError, ValueError):
                                        qty = 0
                                    subtotal = price * qty
                                    total += subtotal

                                    normalized.append({
                                        "cart_item_id": r.get("cart_item_id"),
                                        "product_id": r.get("product_id"),
                                        "product_name": prod.get("name"),
                                        "quantity": qty,
                                        "price": price,
                                        "image_url": prod.get("image_url"),
                                        "stock": prod.get("stock"),
                                        "subtotal": round(subtotal, 2)
                                    })

                                # --- IMPORTANT: frontend expects payload to be an array (RenderCartItems checks Array.isArray)
                                response_data = {"type": "cart_items", "payload": normalized, "total": round(total, 2)}
                                async_to_sync(log_chat_message)(user_id, message, json.dumps(response_data), intent)
                                return JsonResponse(response_data, status=200)

                            except Exception as e:
                                print(f"Add to cart handler error: {e}")
                                response_data = {"type": "text", "payload": "Something went wrong while adding the item to the cart."}
                                async_to_sync(log_chat_message)(user_id, message, json.dumps(response_data), intent)
                                return JsonResponse(response_data, status=500)

                elif action_name == "create_order":
                    res = async_to_sync(create_order_from_cart)(user_id)
                    if res.get("success"):
                        response_data = {"type": "text", "payload": f"Success! Your order (ID: {res['order_id']}) has been placed for a total of ${res['total']:.2f}."}
                    else:
                        response_data = {"type": "text", "payload": f"I failed to create your order: {res.get('error')}"}

                else:
                    response_data = {"type": "text", "payload": f"I understood you wanted an action ({action_name}), but I don't know how to do that yet."}

            except Exception as e:
                print(f"Action Handler Error: {e}")
                response_data = {"type": "text", "payload": "Something went wrong while I was trying to complete that action."}

            # This is now an action response, log it and return
            async_to_sync(log_chat_message)(user_id, message, json.dumps(response_data), intent)
            return JsonResponse(response_data, status=200)

        # ------------------------
        # 8️⃣ Return the valid (non-action) JSON to the frontend
        # ------------------------
        async_to_sync(log_chat_message)(user_id, message, json.dumps(json_response), intent)
        return JsonResponse(json_response, status=200)

    except Exception as e:
        # --- FINAL CATCH-ALL ---
        print(f"Unhandled server error: {e}")
        response_data = {"type": "text", "payload": "A critical server error occurred. Please contact support."}
        # Try to log one last time
        try:
            async_to_sync(log_chat_message)(user_id, message, json.dumps(response_data), "critical_error")
        except Exception as log_e:
            print(f"Failed to log critical error: {log_e}")
        return JsonResponse(response_data, status=500)
