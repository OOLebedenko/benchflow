from typing import Protocol


class PasswordHasher(Protocol):
    """Define password hashing operations."""

    async def hash(self, password: str) -> str:
        """Hash a plaintext password."""
        ...

    async def verify(
            self,
            password: str,
            password_hash: str,
    ) -> bool:
        """Verify a plaintext password against its hash."""
        ...
