# app/core/auth.py
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from sqlalchemy.dialects.postgresql import insert
from app.core.database import AsyncSessionLocal
from app.models.models import User 
from app.core.config import settings
from uuid import UUID
import asyncio 

security = HTTPBearer()

async def get_current_user(
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

    # 1. Get the raw role from the token
    raw_role = (
        payload.get("user_metadata", {}).get("role")
        or payload.get("app_metadata", {}).get("role")
    )

    # 2. SANITIZE: If token says "user", force it to "customer"
    if raw_role == "user":
        app_role = "customer"
    else:
        app_role = raw_role or "customer"

    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")


    async def _upsert():
        async with AsyncSessionLocal() as db:
            stmt = (
                insert(User)
                .values(
                    id=UUID(user_id),
                    name = payload.get("user_metadata", {}).get("full_name") or email,
                    role=app_role, 
                )
                .on_conflict_do_update(
                    index_elements=[User.id],
                    set_={
                        "name": payload.get("user_metadata", {}).get("full_name") or email,
                        "role": app_role,
                    },
                )
            )
            await db.execute(stmt)
            await db.commit()

    await _upsert()

    return {
        "user_id": user_id,
        "email": email,
        "role": app_role,
    }