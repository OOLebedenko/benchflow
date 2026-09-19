from typing import Protocol


class TransactionManager(Protocol):
    """Define transaction completion operations."""

    async def commit(self) -> None:
        """Commit the current transaction."""

        ...
