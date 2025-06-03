from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, EmailStr


class UserBase(BaseModel):
    """Base user model with common fields"""
    email: EmailStr
    username: str = Field(min_length=3, max_length=50)
    full_name: Optional[str] = None
    is_active: bool = True


class UserCreate(UserBase):
    """Model for creating a user"""
    password: str = Field(min_length=8)


class UserUpdate(BaseModel):
    """Model for updating a user"""
    email: Optional[EmailStr] = None
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    full_name: Optional[str] = None
    is_active: Optional[bool] = None
    password: Optional[str] = Field(None, min_length=8)


class UserInDB(UserBase):
    """User model as stored in the database"""
    id: str = Field(alias="_id")
    hashed_password: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None
    roles: List[str] = Field(default_factory=lambda: ["user"])

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "_id": "60d6ec9f7c213e1a1c9c1e1b",
                "email": "user@example.com",
                "username": "username",
                "full_name": "User Name",
                "is_active": True,
                "hashed_password": "hashedpassword",
                "created_at": "2023-01-01T00:00:00",
                "updated_at": "2023-01-01T00:00:00",
                "last_login": "2023-01-01T00:00:00",
                "roles": ["user"]
            }
        }


class User(UserBase):
    """User model returned to clients (without sensitive data)"""
    id: str
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime] = None
    roles: List[str]

    class Config:
        json_schema_extra = {
            "example": {
                "id": "60d6ec9f7c213e1a1c9c1e1b",
                "email": "user@example.com",
                "username": "username",
                "full_name": "User Name",
                "is_active": True,
                "created_at": "2023-01-01T00:00:00",
                "updated_at": "2023-01-01T00:00:00",
                "last_login": "2023-01-01T00:00:00",
                "roles": ["user"]
            }
        }


class Token(BaseModel):
    """Token model for JWT authentication"""
    access_token: str
    token_type: str = "bearer"
    expires_at: int  # Unix timestamp


class TokenData(BaseModel):
    """Data decoded from JWT token"""
    user_id: str
    roles: List[str] = []
    exp: Optional[int] = None 