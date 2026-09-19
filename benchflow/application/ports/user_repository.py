from typing import Protocol
from uuid import UUID

from benchflow.domain.user import User


class UserRepository(Protocol):
    """Define persistence operations for users."""

    async def find_by_id(self, user_id: UUID) -> User | None:
        """Find a user by identifier."""

        ...

    async def find_by_email(self, email: str) -> User | None:
        """Find a user by email."""

        ...

    def add(self, user: User) -> None:
        """Add a user to the current unit of work."""

        ...
