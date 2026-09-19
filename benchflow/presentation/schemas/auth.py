from typing import Literal
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    """Represent user registration input."""

    email: EmailStr
    password: str = Field(min_length=8)


class LoginRequest(BaseModel):
    """Represent user login input."""

    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """Represent registered user output."""

    id: UUID
    email: str


class TokenResponse(BaseModel):
    """Represent an issued access token."""

    access_token: str
    token_type: Literal["bearer"] = "bearer"
