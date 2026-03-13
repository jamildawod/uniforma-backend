from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class QuoteRequestCreate(BaseModel):
    name: str = Field(min_length=2, max_length=255)
    email: EmailStr
    company: str | None = Field(default=None, max_length=255)
    message: str = Field(min_length=5, max_length=5000)


class QuoteRequestRead(BaseModel):
    id: int
    name: str
    email: EmailStr
    company: str | None
    message: str
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
