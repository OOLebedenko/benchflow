from uuid import UUID

from benchflow.application.ports.bench_repository import BenchRepository
from benchflow.domain.bench import Bench


class BenchNotFoundError(Exception):
    """Raised when the requested bench does not exist."""


class BenchService:
    """Provide bench read operations."""

    def __init__(
            self,
            bench_repository: BenchRepository,
    ) -> None:
        self._bench_repository = bench_repository

    async def list_benches(self) -> list[Bench]:
        """Return all benches."""

        return await self._bench_repository.list_all()

    async def get_bench(
            self,
            bench_id: UUID,
    ) -> Bench:
        """Return a bench by its identifier."""

        bench = await self._bench_repository.find_by_id(
            bench_id
        )

        if bench is None:
            raise BenchNotFoundError

        return bench
