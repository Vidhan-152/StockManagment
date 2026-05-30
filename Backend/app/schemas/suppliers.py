from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class SupplierBase(BaseModel):
    name: str
    contact_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    avg_lead_days: int = Field(ge=0)
    reliability_score: float = Field(ge=0, le=1)


class SupplierCreate(SupplierBase):
    pass


class SupplierUpdate(BaseModel):
    name: Optional[str] = None
    contact_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    avg_lead_days: Optional[int] = Field(default=None, ge=0)
    reliability_score: Optional[float] = Field(default=None, ge=0, le=1)


class SupplierOut(SupplierBase):
    id: int
    created_at: datetime
