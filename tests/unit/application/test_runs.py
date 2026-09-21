from unittest.mock import AsyncMock, Mock
from uuid import uuid4

from benchflow.application.services.runs import RunService
from benchflow.domain.bench import Bench, BenchStatus
from benchflow.domain.run import RunStatus


async def test_start_run() -> None:
    """Start a run on an available bench."""

    bench_id = uuid4()

    bench = Bench(
        id=bench_id,
        name="Bench 1",
        status=BenchStatus.AVAILABLE,
    )

    bench_repository = Mock()
    bench_repository.find_by_id = AsyncMock(
        return_value=bench,
    )

    run_repository = Mock()

    unit_of_work = Mock()
    unit_of_work.flush = AsyncMock()
    unit_of_work.commit = AsyncMock()

    bench_lock = Mock()
    bench_lock.acquire = AsyncMock(
        return_value=True,
    )
    bench_lock.release = AsyncMock()

    service = RunService(
        bench_repository=bench_repository,
        run_repository=run_repository,
        unit_of_work=unit_of_work,
        bench_lock=bench_lock,
    )

    run = await service.start_run(bench_id)

    assert run.bench_id == bench_id
    assert run.status is RunStatus.RUNNING
    assert bench.status is BenchStatus.BUSY

    run_repository.add.assert_called_once_with(run)
    bench_repository.update.assert_called_once_with(bench)

    unit_of_work.flush.assert_awaited_once()
    unit_of_work.commit.assert_awaited_once()

    bench_lock.acquire.assert_awaited_once_with(
        bench_id,
        run.id,
    )
    bench_lock.release.assert_awaited_once_with(
        bench_id,
        run.id,
    )
