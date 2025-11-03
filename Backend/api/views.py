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
from .chatbot_logic import detect_intent, get_context_data
from asgiref.sync import async_to_sync
from datetime import datetime, timezone # --- NEW: Import for timestamp ---

# -------------------------------
# INITIAL SETUP
# -------------------------------
SUPABASE_URL = settings.SUPABASE_URL
SUPABASE_SERVICE_KEY = settings.SUPABASE_SERVICE_KEY
SUPABASE_JWT_SECRET = settings.SUPABASE_JWT_SECRET

# Ensure SUPABASE_URL and SUPABASE_SERVICE_KEY are set
if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
    raise ValueError("Supabase URL and Service Key must be set in settings.")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

if os.getenv("GEMINI_API_KEY"):
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# -------------------------------
# JWT VERIFICATION (LOCAL)
# -------------------------------
def verify_supabase_jwt(token: str) -> Optional[dict]:
    try:
        # We don't verify the signature, just decode.
        # Supabase (GoTrue) microservice is the source of truth.
        decoded = jwt.decode(token, options={"verify_signature": False})
        print("✅ Decoded token:", decoded)
        return decoded
    except Exception as e:
        print("❌ Invalid token:", str(e))
        return None

# -------------------------------
# ASYNC SUPABASE HELPERS
# -------------------------------
# These helpers remain async, we will call them from sync views
async def supabase_select_one(table: str, select: str, eq_col: str, eq_val) -> Optional[dict]:
    def _fn():
        return supabase.table(table).select(select).eq(eq_col, eq_val).limit(1).execute()
    res = await asyncio.to_thread(_fn)
    return res.data[0] if res.data else None

# --- NEW: More flexible select helper ---
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
        # --- FIX: Let database assign serial keys. Return new data. ---
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

# --- NEW: Delete helper ---
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


# --- DELETED: get_next_user_id function is removed. ---
# The database 'serial' type handles this automatically.

# --- NEW: Get chat history ---
async def get_recent_chat_history(user_id: int) -> List[dict]:
    """
    Fetches the last 5 messages for a user to provide context.
    """
    def _fn():
        # --- FIX: Corrected table name ---
        return supabase.table("chat_logs_updated").select("user_message, bot_response").eq("user_id", user_id).order("timestamp", desc=True).limit(5).execute()
    
    res = await asyncio.to_thread(_fn)
    # Return in reverse order to be chronological (oldest to newest)
    return (res.data or [])[::-1]

# --- NEW: Log chat message ---
async def log_chat_message(user_id: Optional[int], user_message: str, bot_response: str, intent: str):
    """
    Logs the conversation to the chat_logs_updated table.
    """
    log_payload = {
        "user_id": user_id,
        "user_message": user_message,
        "bot_response": bot_response, # This is the JSON string of the response
        "intent_detected": intent,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    # Fire-and-forget logging
    try:
        # --- FIX: Corrected table name ---
        await supabase_insert("chat_logs_updated", log_payload)
        print(f"Logged chat for user {user_id}")
    except Exception as e:
        print(f"Failed to log chat: {e}")


# -------------------------------
# USER AUTH ROUTES
# -------------------------------

@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request): # --- FIX: Changed to sync 'def' ---
    """Signup: Register new user into Supabase 'users' table."""
    data = request.data
    try:
        # --- FIX: Use async_to_sync to call async helper ---
        existing = async_to_sync(supabase_select_one)("users", "user_id", "email", data["email"])
        if existing:
            return JsonResponse({"error": "User already exists"}, status=400)

        # --- FIX: Removed get_next_user_id ---
        payload = {
            # --- FIX: Removed "user_id": next_id. DB will assign it. ---
            "name": data.get("username"),
            "email": data.get("email"),
            "password_hash": data.get("password"), # Hash in production
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
def login_user(request): # --- FIX: Changed to sync 'def' ---
    """
    Login route — Supabase Auth handles the JWT issuance on frontend.
    This backend view is for manual (email/pass) auth if not using Supabase client.
    """
    data = request.data
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return JsonResponse({"error": "Email and password required"}, status=400)

    # Manual DB check (NOTE: In production, use hashed passwords)
    # --- FIX: Use async_to_sync to call async helper ---
    user = async_to_sync(supabase_select_one)("users", "user_id,email", "email", email)
    if not user:
        return JsonResponse({"error": "Invalid credentials"}, status=401)
    
    # We aren't checking password here, this is just a stub.
    # A real implementation would check the hash.
    # This is also NOT how Supabase auth works (it uses its own auth.users table).
    # We are simulating a local JWT for our local 'users' table.

    payload = {"email": email, "sub": user["user_id"], "user_metadata": user}
    token = jwt.encode(payload, SUPABASE_JWT_SECRET, algorithm="HS26")

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
def get_profile(request): # --- FIX: Made sync 'def' ---
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
        
        # --- FIX: Call async helper from sync context ---
        user = async_to_sync(supabase_select_one)("users", "*", "email", email) 
        
        if not user:
             return JsonResponse({"error": "User not found in DB, though token is valid"}, status=404) # 404
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
        return None # No JSON found
    
    json_str = text[start:end]
    try:
        # Try to parse the extracted string
        obj = json.loads(json_str)
        return obj # Return the parsed JSON object
    except json.JSONDecodeError:
        print(f"Failed to decode JSON: {json_str}")
        pass
    return None


async def call_gemini(prompt: str) -> str:
    """Call Gemini asynchronously."""
    def _fn():
        try:
            # --- FIX: Update model name ---
            model = genai.GenerativeModel("gemini-2.5-flash-preview-09-2025")
            res = model.generate_content(prompt)
            return getattr(res, "text", str(res))
        except Exception as e:
            print(f"GEMINI ERROR: {e}")
            return json.dumps({"type": "text", "payload": "Sorry, I'm having trouble connecting to my brain. Please try again."})

    return await asyncio.to_thread(_fn)


# --- NEW: Helper function for creating an order ---
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
        
        if not price:
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
        "status": "Pending", # Or "Confirmed"
        "total_amount": total_amount,
        "shipping_address": shipping_address,
        "payment_method": "Pending" # Assuming payment is handled elsewhere
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
@api_view(['POST']) # Add the decorator
def chatbot(request): # --- FIX: Changed to sync 'def' ---
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
            context = async_to_sync(asyncio.to_thread)(get_context_data, intent, user_id)
        except Exception as e:
            print(f"Context/Intent Error: {e}")
            intent = "general_error"
            context = {"error": "Failed to get context."}
        
        # --- NEW: Get chat history ---
        chat_history_list = async_to_sync(get_recent_chat_history)(user_id)
        chat_history_string = "\n".join([
            f"User: {msg['user_message']}\nBot: {msg['bot_response']}" 
            for msg in chat_history_list
        ])


        # ------------------------
        # 4️⃣ Build prompt for Gemini (JSON Mode)
        # ------------------------
        prompt = f"""
You are Daksha.ai, a helpful customer support assistant.
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
                            "order_id": order_id, # This is fine if it's None, assuming DB allows null
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
                    params = payload.get("params", {})
                    product_id = params.get("product_id")
                    quantity = params.get("quantity", 1)
                    
                    if not product_id:
                         response_data = {"type": "text", "payload": "You mentioned adding a product, but I'm missing the product ID."}
                    else:
                        # --- FIX: Check if product exists FIRST ---
                        product_info = async_to_sync(supabase_select_one)("products", "name", "product_id", product_id)
                        if not product_info:
                            response_data = {"type": "text", "payload": f"I'm sorry, I can't find a product with ID {product_id}."}
                        else:
                            # Product exists, now check cart
                            existing_item_list = async_to_sync(supabase_select)(
                                "cart_items", 
                                "cart_item_id, quantity", 
                                {"user_id": user_id, "product_id": product_id}
                            )
                            existing_item = existing_item_list[0] if existing_item_list else None
                            
                            if existing_item:
                                new_quantity = existing_item['quantity'] + quantity
                                update_payload = {"quantity": new_quantity}
                                res = async_to_sync(supabase_update)("cart_items", update_payload, "cart_item_id", existing_item['cart_item_id'])
                            else:
                                cart_payload = {
                                    "user_id": user_id,
                                    "product_id": product_id,
                                    "quantity": quantity
                                }
                                res = async_to_sync(supabase_insert)("cart_items", cart_payload)
                            
                            if res.get("success"):
                                product_name = product_info.get("name")
                                response_data = {"type": "text", "payload": f"I've added {quantity} of {product_name} to your cart."}
                            else:
                                response_data = {"type": "text", "payload": f"I failed to add the item to your cart: {res.get('error')}"}

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

