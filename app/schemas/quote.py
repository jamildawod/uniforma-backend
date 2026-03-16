import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class QuoteRequestCreate(BaseModel):
    product_id: uuid.UUID | None = None
    variant_id: int | None = None
    name: str = Field(min_length=2, max_length=255)
    email: EmailStr
    company: str | None = Field(default=None, max_length=255)
    message: str = Field(min_length=5, max_length=5000)


class QuoteRequestRead(BaseModel):
    id: int
    product_id: uuid.UUID | None
    variant_id: int | None
    name: str
    email: EmailStr
    company: str | None
    message: str
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
