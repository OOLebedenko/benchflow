from uuid import uuid4

from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from benchflow.domain.bench import BenchStatus
from benchflow.infrastructure.db.models.bench import BenchModel


async def test_list_benches_returns_all_benches(
        client: TestClient,
        session_factory: async_sessionmaker[AsyncSession],
) -> None:
    """Return all persisted test benches."""

    first_id = uuid4()
    second_id = uuid4()

    async with session_factory() as session:
        # Seed persistence directly because the write API does not exist yet.
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

    response = client.get("/test-benches")

    assert response.status_code == status.HTTP_200_OK

    benches = {
        bench["id"]: bench
        for bench in response.json()
    }

    assert benches[str(first_id)] == {
        "id": str(first_id),
        "name": "Bench 1",
        "status": "available",
    }
    assert benches[str(second_id)] == {
        "id": str(second_id),
        "name": "Bench 2",
        "status": "maintenance",
    }


async def test_get_bench_returns_bench(
        client: TestClient,
        session_factory: async_sessionmaker[AsyncSession],
) -> None:
    """Return the requested test bench."""

    bench_id = uuid4()

    async with session_factory() as session:
        # Seed the bench that the public read endpoint should retrieve.
        session.add(
            BenchModel(
                id=bench_id,
                name="Bench 1",
                status=BenchStatus.OFFLINE.value,
            )
        )
        await session.commit()

    response = client.get(
        f"/test-benches/{bench_id}"
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "id": str(bench_id),
        "name": "Bench 1",
        "status": "offline",
    }


async def test_get_bench_returns_not_found(
        client: TestClient,
) -> None:
    """Return 404 when the requested test bench does not exist."""

    bench_id = uuid4()

    response = client.get(
        f"/test-benches/{bench_id}"
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {
        "detail": "Bench not found"
    }
