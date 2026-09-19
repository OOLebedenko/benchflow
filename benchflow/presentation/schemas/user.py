from uuid import UUID

from pydantic import BaseModel


class UserResponse(BaseModel):
    """Represent user output."""

    id: UUID
    email: str
