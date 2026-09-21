from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from benchflow.domain.bench import BenchStatus
from benchflow.domain.run import Run, RunStatus
from benchflow.infrastructure.db.models.bench import BenchModel
from benchflow.infrastructure.db.models.run import RunModel
from benchflow.infrastructure.db.unit_of_work import SqlAlchemyUnitOfWork
from benchflow.infrastructure.repositories.run import SqlAlchemyRunRepository


async def test_add_persists_run(
        session_factory: async_sessionmaker[AsyncSession],
) -> None:
    """Persist a staged run addition."""

    bench_id = uuid4()

    async with session_factory() as session:
        # Persist the parent bench directly because this integration test
        # exercises run persistence rather than bench creation.
        session.add(
            BenchModel(
                id=bench_id,
                name="Bench 1",
                status=BenchStatus.AVAILABLE.value,
            )
        )
        await session.commit()

    run = Run(
        id=uuid4(),
        bench_id=bench_id,
        status=RunStatus.RUNNING,
    )

    async with session_factory() as session:
        unit_of_work = SqlAlchemyUnitOfWork(session)
        repository = SqlAlchemyRunRepository(
            unit_of_work,
        )

        repository.add(run)
        await unit_of_work.commit()

    async with session_factory() as session:
        model = await session.get(
            RunModel,
            run.id,
        )

        assert model is not None
        assert model.id == run.id
        assert model.bench_id == run.bench_id
        assert model.status == run.status.value
