from uuid import UUID

from pydantic import BaseModel

from benchflow.domain.user import UserRole


class UserResponse(BaseModel):
    """Represent a user response."""

    id: UUID
    email: str
    role: UserRole