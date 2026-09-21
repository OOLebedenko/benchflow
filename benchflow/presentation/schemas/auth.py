from typing import Literal

from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    """Represent user registration input."""

    email: EmailStr
    password: str = Field(min_length=8)


class LoginRequest(BaseModel):
    """Represent user login input."""

    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """Represent an issued access token."""

    access_token: str
    token_type: Literal["bearer"] = "bearer"
