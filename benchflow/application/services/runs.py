from uuid import UUID, uuid4

from benchflow.application.ports.bench_lock import BenchLock
from benchflow.application.ports.bench_repository import BenchRepository
from benchflow.application.ports.run_repository import RunRepository
from benchflow.application.ports.unit_of_work import UnitOfWork
from benchflow.application.services.benches import BenchNotFoundError
from benchflow.domain.bench import BenchStatus
from benchflow.domain.run import Run, RunStatus


class BenchUnavailableError(Exception):
    """Raised when a bench cannot start a run."""


class RunService:
    """Provide run operations."""

    def __init__(
            self,
            bench_repository: BenchRepository,
            run_repository: RunRepository,
            unit_of_work: UnitOfWork,
            bench_lock: BenchLock,
    ) -> None:
        self._bench_repository = bench_repository
        self._run_repository = run_repository
        self._unit_of_work = unit_of_work
        self._bench_lock = bench_lock

    async def start_run(
            self,
            bench_id: UUID,
    ) -> Run:
        """Start a run on an available bench."""

        run_id = uuid4()

        acquired = await self._bench_lock.acquire(
            bench_id,
            run_id,
        )

        if not acquired:
            raise BenchUnavailableError

        try:
            bench = await self._bench_repository.find_by_id(
                bench_id,
            )

            if bench is None:
                raise BenchNotFoundError

            if bench.status != BenchStatus.AVAILABLE:
                raise BenchUnavailableError

            run = Run(
                id=run_id,
                bench_id=bench.id,
                status=RunStatus.RUNNING,
            )

            bench.status = BenchStatus.BUSY

            self._run_repository.add(run)
            self._bench_repository.update(bench)

            await self._unit_of_work.flush()
            await self._unit_of_work.commit()

            return run
        finally:
            await self._bench_lock.release(
                bench_id,
                run_id,
            )
