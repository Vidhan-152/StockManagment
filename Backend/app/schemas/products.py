from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, model_validator


class ProductBase(BaseModel):
    user_id: int = Field(ge=1)
    category_id: Optional[int] = Field(default=None, ge=1)
    name: str
    sku: str
    description: Optional[str] = None
    unit_price: float = Field(ge=0)
    stock: int = Field(ge=0)
    reorder_threshold: int = Field(ge=0)
    overstock_threshold: int = Field(ge=0)

    @model_validator(mode="after")
    def validate_thresholds(self):
        if self.overstock_threshold < self.reorder_threshold:
            raise ValueError("overstock_threshold must be >= reorder_threshold")
        return self


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    user_id: Optional[int] = Field(default=None, ge=1)
    category_id: Optional[int] = Field(default=None, ge=1)
    name: Optional[str] = None
    sku: Optional[str] = None
    description: Optional[str] = None
    unit_price: Optional[float] = Field(default=None, ge=0)
    stock: Optional[int] = Field(default=None, ge=0)
    reorder_threshold: Optional[int] = Field(default=None, ge=0)
    overstock_threshold: Optional[int] = Field(default=None, ge=0)

    @model_validator(mode="after")
    def validate_thresholds(self):
        if self.reorder_threshold is None or self.overstock_threshold is None:
            return self
        if self.overstock_threshold < self.reorder_threshold:
            raise ValueError("overstock_threshold must be >= reorder_threshold")
        return self


class ProductOut(ProductBase):
    id: int
    created_at: datetime