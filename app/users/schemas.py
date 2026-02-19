"""
User Pydantic schemas for request/response validation.
"""
from pydantic import BaseModel, Field, EmailStr, ConfigDict
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    """Base user schema with common fields."""
    email: EmailStr = Field(..., description="User email address")
    name: str = Field(..., min_length=1, max_length=100, description="User display name")
    student_id: Optional[str] = Field(None, max_length=20, description="Student ID (optional)")


class UserCreate(UserBase):
    """Schema for user registration."""
    password: str = Field(..., min_length=8, max_length=128, description="User password")


class UserLogin(BaseModel):
    """Schema for user login."""
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., description="User password")


class UserUpdate(BaseModel):
    """Schema for updating user profile. All fields optional."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    student_id: Optional[str] = Field(None, max_length=20)


class UserInDB(UserBase):
    """Schema for user as stored in database (without password)."""
    id: int
    is_active: bool
    is_admin: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    """Schema for JWT token response."""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Schema for decoded token data."""
    sub: str  # user email
    user_id: int
    is_admin: bool = False
