from uuid import UUID, uuid4

from benchflow.application.ports.bench_repository import BenchRepository
from benchflow.application.ports.unit_of_work import UnitOfWork
from benchflow.domain.bench import Bench, BenchStatus


class BenchNotFoundError(Exception):
    """Raised when the requested bench does not exist."""


class BenchService:
    """Provide bench operations."""

    def __init__(
            self,
            bench_repository: BenchRepository,
            unit_of_work: UnitOfWork,
    ) -> None:
        self._bench_repository = bench_repository
        self._unit_of_work = unit_of_work

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

    async def create_bench(
            self,
            name: str,
            status: BenchStatus,
    ) -> Bench:
        """Create a new bench."""

        bench = Bench(
            id=uuid4(),
            name=name,
            status=status,
        )

        self._bench_repository.add(bench)

        await self._unit_of_work.flush()
        await self._unit_of_work.commit()

        return bench

    async def update_bench(
            self,
            bench_id: UUID,
            name: str | None,
            status: BenchStatus | None,
    ) -> Bench:
        """Update an existing bench."""

        bench = await self._bench_repository.find_by_id(
            bench_id
        )

        if bench is None:
            raise BenchNotFoundError

        if name is not None:
            bench.name = name

        if status is not None:
            bench.status = status

        self._bench_repository.update(bench)

        await self._unit_of_work.flush()
        await self._unit_of_work.commit()

        return bench
