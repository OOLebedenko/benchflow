from dataclasses import dataclass
from enum import StrEnum
from uuid import UUID


class UserRole(StrEnum):
    """Represent a user role."""

    USER = "user"
    ADMIN = "admin"


@dataclass(slots=True)
class User:
    """Represent a user in the domain."""

    id: UUID
    email: str
    password_hash: str
    role: UserRole = UserRole.USER
