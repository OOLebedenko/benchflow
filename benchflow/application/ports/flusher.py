from typing import Protocol


class Flusher(Protocol):
    """Define persistence flushing operations."""

    async def flush(self) -> None:
        """Flush pending changes."""

        ...
