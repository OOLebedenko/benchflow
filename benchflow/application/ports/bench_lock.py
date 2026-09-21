from typing import Protocol
from uuid import UUID


class BenchLock(Protocol):
    """Coordinate exclusive access to a bench."""

    async def acquire(
            self,
            bench_id: UUID,
            run_id: UUID,
    ) -> bool:
        """Try to acquire exclusive access to a bench."""
        ...

    async def release(
            self,
            bench_id: UUID,
            run_id: UUID,
    ) -> None:
        """Release access owned by the run."""
        ...
