# app/core/auth.py

from fastapi import Depends, HTTPException, status,WebSocket
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
        )
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )

    user_id = payload.get("sub")
    role = payload.get("role")

    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token payload")

    return {
        "user_id": user_id,
        "role": role,
        "email": payload.get("email"),
    }
async def get_user_from_ws(ws: WebSocket):
    """
    Authenticate WebSocket using Supabase JWT.
    Expects:
      Authorization: Bearer <token>
    OR
      ?token=<jwt>
    """

    token = None

    # 1. Header
    auth = ws.headers.get("authorization")
    if auth and auth.startswith("Bearer "):
        token = auth.split(" ")[1]

    # 2. Query param fallback
    if not token:
        token = ws.query_params.get("token")

    if not token:
        await ws.close(code=1008)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing auth token",
        )

    try:
        payload = jwt.decode(
            token,
            settings.SUPABASE_JWT_SECRET,
            algorithms=["HS256"],
            audience="authenticated",
        )
    except jwt.PyJWTError:
        await ws.close(code=1008)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )

    return {
        "user_id": payload.get("sub"),
        "role": payload.get("role"),
        "email": payload.get("email"),
    }