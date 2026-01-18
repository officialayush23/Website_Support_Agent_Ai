# app/api/routers/leads.py
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import uuid4

from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.models import Lead
from app.schema.schemas import LeadCreate, LeadOut
from app.utils.api_error import forbidden

router = APIRouter(prefix="/leads", tags=["Leads"])

# PUBLIC: Submit "Contact Us" Form
@router.post("/", response_model=LeadOut)
async def create_lead(
    payload: LeadCreate,
    db: AsyncSession = Depends(get_db),
):
    lead = Lead(
        id=uuid4(),
        email=payload.email,
        requirements=payload.requirements,
    )
    db.add(lead)
    await db.commit()
    await db.refresh(lead)
    return lead

# ADMIN: View all leads
@router.get("/", response_model=list[LeadOut])
async def list_leads(
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    if user["role"] != "admin":
        forbidden()
    
    res = await db.execute(select(Lead).order_by(Lead.created_at.desc()))
    return res.scalars().all()