from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional
from uuid import UUID


class UserCreate(BaseModel):
    """Schema for creating a new user"""
    name: str = Field(..., min_length=1, max_length=255, description="User's full name")
    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(..., min_length=8, description="User's password (min 8 characters)")
    avatar: Optional[str] = Field(None, max_length=500, description="URL to user's avatar image")
    bio: Optional[str] = Field(None, description="User's bio/description")
    timezone: Optional[str] = Field("UTC", max_length=50, description="User's timezone")
    date_format: Optional[str] = Field("YYYY-MM-DD", max_length=20, description="Preferred date format")
    time_format: Optional[str] = Field("24h", pattern="^(12h|24h)$", description="Preferred time format")


class UserUpdate(BaseModel):
    """Schema for updating user information"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    avatar: Optional[str] = Field(None, max_length=500)
    bio: Optional[str] = None
    timezone: Optional[str] = Field(None, max_length=50)
    date_format: Optional[str] = Field(None, max_length=20)
    time_format: Optional[str] = Field(None, pattern="^(12h|24h)$")


class UserOut(BaseModel):
    """Schema for user output (public information)"""
    id: UUID
    name: str
    email: EmailStr
    avatar: Optional[str]
    bio: Optional[str]
    is_active: bool
    is_verified: bool
    timezone: str
    date_format: str
    time_format: str
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime]

    class Config:
        from_attributes = True


class UserProfile(BaseModel):
    """Schema for detailed user profile"""
    id: UUID
    name: str
    email: EmailStr
    avatar: Optional[str]
    bio: Optional[str]
    is_active: bool
    is_verified: bool
    timezone: str
    date_format: str
    time_format: str
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime]

    # Statistics (would be calculated)
    total_activities: Optional[int] = 0
    total_schedules: Optional[int] = 0
    total_insights: Optional[int] = 0

    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    """Schema for user login"""
    email: EmailStr
    password: str


class UserPasswordChange(BaseModel):
    """Schema for changing user password"""
    current_password: str
    new_password: str = Field(..., min_length=8, description="New password (min 8 characters)")


class UserEmailVerification(BaseModel):
    """Schema for email verification"""
    token: str
