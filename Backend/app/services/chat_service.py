# app/services/chat_service.py
from uuid import uuid4
from app.models.models import ChatSession


async def create_chat_session(db, user_id):
    s = ChatSession(
        id=uuid4(),
        user_id=user_id,
        is_active=True,
    )
    db.add(s)
    await db.commit()
    return s
