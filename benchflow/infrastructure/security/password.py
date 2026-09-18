import asyncio

from pwdlib import PasswordHash


class PwdlibPasswordHasher:
    """Hash passwords using pwdlib."""

    def __init__(self) -> None:
        self.password_hash = PasswordHash.recommended()

    async def hash(self, password: str) -> str:
        """Hash a password without blocking the event loop."""

        return await asyncio.to_thread(
            self.password_hash.hash,
            password,
        )
