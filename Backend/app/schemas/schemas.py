# app/schemas/schemas.py

from pydantic import BaseModel
from typing import Optional, Dict, Any
from uuid import UUID
from datetime import datetime


class UserOut(BaseModel):
    id: UUID
    name: Optional[str]
    role: str

    class Config:
        from_attributes = True


class ProductOut(BaseModel):
    id: UUID
    name: str
    description: Optional[str]
    category: Optional[str]
    price: float
    attributes: Optional[Dict[str, Any]]

    class Config:
        from_attributes = True


class MessageCreate(BaseModel):
    content: str


class MessageOut(BaseModel):
    id: UUID
    role: str
    content: str
    created_at: datetime

    class Config:
        from_attributes = True
