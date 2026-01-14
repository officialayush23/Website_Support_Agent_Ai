# app/core/auth.py
from fastapi import Depends, HTTPException, status, WebSocket
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt

from app.core.config import settings

security = HTTPBearer()

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    token = credentials.credentials

    try:
        payload = jwt.decode(
            token,
            settings.SUPABASE_JWT_SECRET,
            algorithms=["HS256"],
            audience="authenticated",
            leeway=10,
        )
    except jwt.PyJWTError as e:
        raise HTTPException(status_code=401, detail=str(e))

    user_id = payload.get("sub")
    email = payload.get("email")

    app_role = (
        payload.get("user_metadata", {}).get("role")
        or payload.get("app_metadata", {}).get("role")
        or "user"
    )

    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")

    return {
        "user_id": user_id,
        "email": email,
        "role": app_role,  # 👈 THIS is what admin checks should use
    }

async def get_user_from_ws(ws: WebSocket):
    token = None

    auth = ws.headers.get("authorization")
    if auth and auth.startswith("Bearer "):
        token = auth.split(" ")[1]

    if not token:
        token = ws.query_params.get("token")

    if not token:
        await ws.close(code=1008)
        raise HTTPException(401, "Missing token")

    try:
        payload = jwt.decode(
            token,
            settings.SUPABASE_JWT_SECRET,
            algorithms=["HS256"],
            audience="authenticated",
        )
    except jwt.PyJWTError:
        await ws.close(code=1008)
        raise HTTPException(401, "Invalid token")

    return {
        "user_id": payload["sub"],
        "email": payload.get("email"),
        "role": payload.get("user_metadata", {}).get("role", "user"),
    }
