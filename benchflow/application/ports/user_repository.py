from typing import Protocol

from benchflow.domain.user import User


class UserRepository(Protocol):
    """Define persistence operations for users."""

    async def find_by_email(self, email: str) -> User | None:
        """Find a user by email."""

        ...

    async def add(self, user: User) -> None:
        """Persist a user."""

        ...
