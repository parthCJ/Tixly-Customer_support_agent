"""
User models for authentication and authorization
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class UserRole(str, Enum):
    """User roles for role-based access control"""
    CUSTOMER = "customer"      # Can submit tickets, view their own tickets
    AGENT = "agent"            # Can view/reply to assigned tickets
    MANAGER = "manager"        # Can view all tickets, analytics, forecasts
    ADMIN = "admin"            # Full system access


class UserBase(BaseModel):
    """Base user model with common fields"""
    email: EmailStr
    full_name: str = Field(..., min_length=1, max_length=100)
    role: UserRole = UserRole.CUSTOMER
    is_active: bool = True


class UserCreate(UserBase):
    """Model for creating a new user"""
    password: str = Field(..., min_length=8, max_length=100)
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "agent@tixly.com",
                "full_name": "John Doe",
                "password": "SecurePass123!",
                "role": "agent"
            }
        }


class UserLogin(BaseModel):
    """Model for user login"""
    email: EmailStr
    password: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "agent@tixly.com",
                "password": "SecurePass123!"
            }
        }


class User(UserBase):
    """Full user model (stored in database)"""
    user_id: str
    hashed_password: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None
    
    # Agent-specific fields
    agent_skills: Optional[List[str]] = None  # e.g., ["billing", "technical"]
    team: Optional[str] = None
    
    class Config:
        from_attributes = True


class UserResponse(UserBase):
    """User model for API responses (no password)"""
    user_id: str
    created_at: datetime
    last_login: Optional[datetime] = None
    agent_skills: Optional[List[str]] = None
    team: Optional[str] = None
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "user_id": "USR-20231213-ABCD1234",
                "email": "agent@tixly.com",
                "full_name": "John Doe",
                "role": "agent",
                "is_active": True,
                "created_at": "2023-12-13T10:30:00",
                "last_login": "2023-12-13T14:20:00",
                "agent_skills": ["billing", "technical"],
                "team": "support"
            }
        }


class Token(BaseModel):
    """OAuth 2.0 token response"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int = 3600  # seconds
    user: UserResponse


class TokenData(BaseModel):
    """Data encoded in JWT token"""
    user_id: Optional[str] = None
    email: Optional[str] = None
    role: Optional[str] = None
