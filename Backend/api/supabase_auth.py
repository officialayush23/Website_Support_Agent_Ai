import os
import jwt
from django.http import JsonResponse
from dotenv import load_dotenv

load_dotenv()
SUPABASE_JWT_SECRET = os.getenv("SUPABASE_JWT_SECRET")

def verify_supabase_token(request):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return None, JsonResponse({"error": "Missing or invalid token"}, status=401)

    token = auth_header.split(" ")[1]

    try:
        decoded = jwt.decode(
            token,
            SUPABASE_JWT_SECRET,
            algorithms=["HS256"],
            options={"verify_aud": False}
        )
        print("✅ Decoded token:", decoded)
        return decoded, None

    except jwt.ExpiredSignatureError:
        print("❌ Token expired")
        return None, JsonResponse({"error": "Token expired"}, status=401)

    except jwt.InvalidTokenError as e:
        print("❌ Invalid token:", str(e))
        return None, JsonResponse({"error": f"Invalid or expired token: {str(e)}"}, status=401)
