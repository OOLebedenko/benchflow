from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from benchflow.domain.bench import Bench, BenchStatus
from benchflow.infrastructure.db.models.bench import BenchModel
from benchflow.infrastructure.db.unit_of_work import SqlAlchemyUnitOfWork
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

        unit_of_work = SqlAlchemyUnitOfWork(session)
        repository = SqlAlchemyBenchRepository(
            session,
            unit_of_work,
        )

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

        unit_of_work = SqlAlchemyUnitOfWork(session)
        repository = SqlAlchemyBenchRepository(
            session,
            unit_of_work,
        )

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
        unit_of_work = SqlAlchemyUnitOfWork(session)
        repository = SqlAlchemyBenchRepository(
            session,
            unit_of_work,
        )

        bench = await repository.find_by_id(uuid4())

        assert bench is None


async def test_add_persists_bench(
        session_factory: async_sessionmaker[AsyncSession],
) -> None:
    """Persist a bench through the repository."""

    bench = Bench(
        id=uuid4(),
        name="Bench 1",
        status=BenchStatus.AVAILABLE,
    )

    async with session_factory() as session:
        unit_of_work = SqlAlchemyUnitOfWork(session)
        repository = SqlAlchemyBenchRepository(
            session,
            unit_of_work,
        )

        repository.add(bench)
        await session.commit()

    async with session_factory() as session:
        model = await session.get(
            BenchModel,
            bench.id,
        )

        assert model is not None
        assert model.id == bench.id
        assert model.name == bench.name
        assert model.status == bench.status.value

        await session.delete(model)
        await session.commit()


async def test_update_persists_bench(
        session_factory: async_sessionmaker[AsyncSession],
) -> None:
    """Persist a staged bench update."""

    bench_id = uuid4()

    async with session_factory() as session:
        session.add(
            BenchModel(
                id=bench_id,
                name="Bench 1",
                status=BenchStatus.AVAILABLE.value,
            )
        )
        await session.commit()

    bench = Bench(
        id=bench_id,
        name="Updated bench",
        status=BenchStatus.OFFLINE,
    )

    async with session_factory() as session:
        unit_of_work = SqlAlchemyUnitOfWork(session)
        repository = SqlAlchemyBenchRepository(
            session,
            unit_of_work,
        )

        repository.update(bench)
        await unit_of_work.commit()

    async with session_factory() as session:
        model = await session.get(BenchModel, bench_id)

        assert model is not None
        assert model.name == "Updated bench"
        assert model.status == BenchStatus.OFFLINE.value
