from typing import Protocol
from uuid import UUID

from benchflow.domain.bench import Bench


class BenchRepository(Protocol):
    """Define persistence operations for benches."""

    async def list_all(self) -> list[Bench]:
        """Return all benches."""
        ...

    async def find_by_id(
            self,
            bench_id: UUID,
    ) -> Bench | None:
        """Find a bench by its identifier."""
        ...

    def add(self, bench: Bench) -> None:
        """Add a bench to the current unit of work."""
        ...
