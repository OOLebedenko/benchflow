from uuid import uuid4

from httpx2 import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from benchflow.domain.bench import BenchStatus
from benchflow.domain.run import RunStatus
from benchflow.infrastructure.db.models.bench import BenchModel
from benchflow.infrastructure.db.models.run import RunModel


async def test_start_run(
        client: AsyncClient,
        session_factory: async_sessionmaker[AsyncSession],
) -> None:
    """Start a run on an available bench."""

    bench_id = uuid4()

    # Persist an available bench required by the start-run use case.
    async with session_factory() as session:
        session.add(
            BenchModel(
                id=bench_id,
                name="Bench 1",
                status=BenchStatus.AVAILABLE.value,
            )
        )
        await session.commit()

    response = await client.post(
        f"/benches/{bench_id}/runs",
    )

    assert response.status_code == 201

    body = response.json()

    assert body["bench_id"] == str(bench_id)
    assert body["status"] == RunStatus.RUNNING.value

    run_id = body["id"]

    # Verify that the API call persisted the run and marked the bench busy.
    async with session_factory() as session:
        run = await session.get(
            RunModel,
            run_id,
        )
        bench = await session.get(
            BenchModel,
            bench_id,
        )

        assert run is not None
        assert run.bench_id == bench_id
        assert run.status == RunStatus.RUNNING.value

        assert bench is not None
        assert bench.status == BenchStatus.BUSY.value
