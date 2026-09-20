from typing import Protocol


class UniqueConstraintViolationError(Exception):
    """Raised when a unit of work violates a uniqueness constraint."""


class UnitOfWork(Protocol):
    """Define transactional unit-of-work operations."""

    async def flush(self) -> None:
        """Synchronize pending changes with persistent storage."""
        ...

    async def commit(self) -> None:
        """Commit the current unit of work."""
        ...

    async def rollback(self) -> None:
        """Roll back the current unit of work."""
        ...
