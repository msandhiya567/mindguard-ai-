"""
MindGuard AI - User Schemas
==============================
Pydantic models define the shape of API requests/responses. These are
separate from the SQLAlchemy models (app/models/models.py) on purpose -
schemas control what the API accepts/returns, models control what's
stored in the database. Keeping them separate means we never
accidentally leak a field like hashed_password in an API response.
"""

from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    full_name: str | None = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: int
    email: EmailStr
    full_name: str | None
    role: str
    created_at: datetime

    class Config:
        from_attributes = True  # allows creating this from a SQLAlchemy model instance


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    refresh_token: str