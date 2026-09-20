from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from benchflow.domain.bench import Bench, BenchStatus
from benchflow.infrastructure.db.models.bench import BenchModel
from benchflow.infrastructure.repositories.bench import (
    SqlAlchemyBenchRepository,
)


async def test_list_all_returns_benches(
        session_factory: async_sessionmaker[AsyncSession],
) -> None:
    """Return all persisted benches."""

    first_id = uuid4()
    second_id = uuid4()

    async with session_factory() as session:
        # Persist test data directly because this integration test exercises
        # the read-only repository rather than a bench creation use case.
        session.add_all(
            [
                BenchModel(
                    id=first_id,
                    name="Bench 1",
                    status=BenchStatus.AVAILABLE.value,
                ),
                BenchModel(
                    id=second_id,
                    name="Bench 2",
                    status=BenchStatus.MAINTENANCE.value,
                ),
            ]
        )
        await session.commit()

        repository = SqlAlchemyBenchRepository(session)

        benches = await repository.list_all()

        benches_by_id = {
            bench.id: bench
            for bench in benches
        }

        assert benches_by_id[first_id] == Bench(
            id=first_id,
            name="Bench 1",
            status=BenchStatus.AVAILABLE,
        )
        assert benches_by_id[second_id] == Bench(
            id=second_id,
            name="Bench 2",
            status=BenchStatus.MAINTENANCE,
        )


async def test_find_by_id_returns_bench(
        session_factory: async_sessionmaker[AsyncSession],
) -> None:
    """Return the bench with the requested identifier."""

    bench_id = uuid4()

    async with session_factory() as session:
        session.add(
            BenchModel(
                id=bench_id,
                name="Bench 1",
                status=BenchStatus.OFFLINE.value,
            )
        )
        await session.commit()

        repository = SqlAlchemyBenchRepository(session)

        bench = await repository.find_by_id(bench_id)

        assert bench == Bench(
            id=bench_id,
            name="Bench 1",
            status=BenchStatus.OFFLINE,
        )


async def test_find_by_id_returns_none(
        session_factory: async_sessionmaker[AsyncSession],
) -> None:
    """Return None when the requested bench does not exist."""

    async with session_factory() as session:
        repository = SqlAlchemyBenchRepository(session)

        bench = await repository.find_by_id(uuid4())

        assert bench is None
