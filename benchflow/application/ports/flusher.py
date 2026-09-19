from typing import Protocol


class UniqueConstraintViolationError(Exception):
    """Raised when flushing violates a uniqueness constraint."""


class Flusher(Protocol):
    """Define persistence flushing operations."""

    async def flush(self) -> None:
        """Flush pending changes."""

        ...
