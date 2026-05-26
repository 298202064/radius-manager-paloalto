from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=64)
    password: str = Field(..., min_length=6, max_length=128)
    email: Optional[str] = None
    role: str = Field(default="user", pattern="^(admin|user)$")
    enabled: bool = True
    note: Optional[str] = None


class UserUpdate(BaseModel):
    email: Optional[str] = None
    password: Optional[str] = Field(None, min_length=6, max_length=128)
    role: Optional[str] = Field(None, pattern="^(admin|user)$")
    enabled: Optional[bool] = None
    note: Optional[str] = None


class UserResponse(BaseModel):
    id: int
    username: str
    email: Optional[str] = None
    role: str
    enabled: bool
    note: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    has_otp: bool = False

    model_config = {"from_attributes": True}


class UserPage(BaseModel):
    items: list[UserResponse]
    total: int
    page: int
    page_size: int


class PasswordReset(BaseModel):
    new_password: str = Field(..., min_length=6, max_length=128)


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=6, max_length=128)
