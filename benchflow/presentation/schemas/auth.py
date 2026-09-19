from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    """Represent user registration input."""

    email: EmailStr
    password: str = Field(min_length=8)


class UserResponse(BaseModel):
    """Represent registered user output."""

    id: UUID
    email: str
