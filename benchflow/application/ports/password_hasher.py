from typing import Protocol


class PasswordHasher(Protocol):
    """Define password hashing operations."""

    async def hash(self, password: str) -> str:
        """Hash a plaintext password."""

        ...
