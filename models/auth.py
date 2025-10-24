from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class UserRole(str, Enum):
    """User roles for role-based access control"""
    ADMIN = "admin"
    USER = "user"
    MODERATOR = "moderator"


class UserAuth(BaseModel):
    """User authentication model"""
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)
    role: UserRole = UserRole.USER


class UserCreateWithAuth(UserAuth):
    """User creation model with authentication"""
    name: str = Field(..., min_length=2, max_length=100)
    age: Optional[int] = Field(None, ge=0, le=150)
    phone: Optional[str] = Field(None, min_length=10, max_length=15)
    address: Optional[str] = Field(None, max_length=500)


class LoginRequest(BaseModel):
    """Login request model"""
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """Token response model"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user_id: str
    user_email: str
    user_role: str


class TokenData(BaseModel):
    """Token data model for JWT payload"""
    user_id: str
    email: str
    role: str
    exp: datetime


class PasswordResetRequest(BaseModel):
    """Password reset request model"""
    email: EmailStr


class PasswordReset(BaseModel):
    """Password reset model"""
    token: str
    new_password: str = Field(..., min_length=8, max_length=100)


class ChangePassword(BaseModel):
    """Change password model"""
    current_password: str
    new_password: str = Field(..., min_length=8, max_length=100)


class UserWithAuth(BaseModel):
    """User model with authentication data"""
    id: str
    name: str
    email: str
    age: Optional[int]
    phone: Optional[str]
    address: Optional[str]
    is_active: bool
    role: UserRole
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime] = None


class AuthResponse(BaseModel):
    """Authentication response model"""
    user: UserWithAuth
    token: TokenResponse
