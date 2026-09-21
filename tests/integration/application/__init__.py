import asyncio
from uuid import uuid4

from redis.asyncio import Redis
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from benchflow.application.services.runs import (
    BenchUnavailableError,
    RunService,
)
from benchflow.domain.bench import BenchStatus
from benchflow.domain.run import Run
from benchflow.infrastructure.db.models.bench import BenchModel
from benchflow.infrastructure.db.models.run import RunModel
from benchflow.infrastructure.db.unit_of_work import SqlAlchemyUnitOfWork
from benchflow.infrastructure.redis.bench_lock import RedisBenchLock
from benchflow.infrastructure.repositories.bench import (
    SqlAlchemyBenchRepository,
)
from benchflow.infrastructure.repositories.run import (
    SqlAlchemyRunRepository,
)


async def test_concurrent_start_creates_single_run(
        session_factory: async_sessionmaker[AsyncSession],
        redis_client: Redis,
) -> None:
    """Allow only one concurrent run to start on a bench."""

    bench_id = uuid4()

    # Persist one available bench shared by both concurrent attempts.
    async with session_factory() as session:
        session.add(
            BenchModel(
                id=bench_id,
                name="Bench 1",
                status=BenchStatus.AVAILABLE.value,
            )
        )
        await session.commit()

    async def start_run() -> Run:
        # Each concurrent operation needs its own SQLAlchemy session
        # and unit of work, while both share the same Redis instance.
        async with session_factory() as session:
            unit_of_work = SqlAlchemyUnitOfWork(session)

            bench_repository = SqlAlchemyBenchRepository(
                session,
                unit_of_work,
            )
            run_repository = SqlAlchemyRunRepository(
                unit_of_work,
            )
            bench_lock = RedisBenchLock(
                redis=redis_client,
                ttl_seconds=30,
            )

            service = RunService(
                bench_repository=bench_repository,
                run_repository=run_repository,
                unit_of_work=unit_of_work,
                bench_lock=bench_lock,
            )

            return await service.start_run(bench_id)

    results = await asyncio.gather(
        start_run(),
        start_run(),
        return_exceptions=True,
    )

    successful_runs = [
        result
        for result in results
        if isinstance(result, Run)
    ]
    unavailable_errors = [
        result
        for result in results
        if isinstance(result, BenchUnavailableError)
    ]

    assert len(successful_runs) == 1
    assert len(unavailable_errors) == 1

    # Verify the final durable state independently of both start attempts.
    async with session_factory() as session:
        result = await session.execute(
            select(RunModel).where(
                RunModel.bench_id == bench_id,
            )
        )
        runs = result.scalars().all()

        bench = await session.get(
            BenchModel,
            bench_id,
        )

        assert len(runs) == 1

        assert bench is not None
        assert bench.status == BenchStatus.BUSY.value
