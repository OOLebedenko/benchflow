from collections.abc import Callable
from uuid import uuid4

import pytest
from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from benchflow.domain.bench import BenchStatus
from benchflow.domain.user import UserRole
from benchflow.infrastructure.db.models.bench import BenchModel


async def test_list_benches_returns_all_benches(
        client: TestClient,
        session_factory: async_sessionmaker[AsyncSession],
) -> None:
    """Return all persisted benches."""

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

    response = client.get("/benches")

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
    """Return the requested bench."""

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
        f"/benches/{bench_id}"
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
    """Return 404 when the requested bench does not exist."""

    bench_id = uuid4()

    response = client.get(
        f"/benches/{bench_id}"
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {
        "detail": "Bench not found"
    }


@pytest.mark.parametrize(
    ("method", "path", "payload"),
    [
        (
                "POST",
                "/benches",
                {
                    "name": "Bench 1",
                },
        ),
        (
                "PATCH",
                "/benches/00000000-0000-0000-0000-000000000001",
                {
                    "status": "offline",
                },
        ),
        (
                "DELETE",
                "/benches/00000000-0000-0000-0000-000000000001",
                None,
        ),
    ],
)
def test_bench_writes_require_authentication(
        client: TestClient,
        method: str,
        path: str,
        payload: dict[str, str] | None,
) -> None:
    """Require authentication for bench writes."""

    response = client.request(
        method,
        path,
        json=payload,
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {
        "detail": "Not authenticated",
    }


@pytest.mark.parametrize(
    ("method", "path", "payload"),
    [
        (
                "POST",
                "/benches",
                {
                    "name": "Bench 1",
                },
        ),
        (
                "PATCH",
                "/benches/00000000-0000-0000-0000-000000000001",
                {
                    "status": "offline",
                },
        ),
        (
                "DELETE",
                "/benches/00000000-0000-0000-0000-000000000001",
                None,
        ),
    ],
)
def test_bench_writes_reject_regular_user(
        client: TestClient,
        authorize_as: Callable[[UserRole], None],
        method: str,
        path: str,
        payload: dict[str, str] | None,
) -> None:
    """Reject regular users from bench writes."""

    authorize_as(UserRole.USER)

    response = client.request(
        method,
        path,
        json=payload,
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json() == {
        "detail": "Insufficient permissions",
    }


async def test_create_bench(
        client: TestClient,
        session_factory: async_sessionmaker[AsyncSession],
        authorize_as: Callable[[UserRole], None],
) -> None:
    """Create and persist a bench."""

    authorize_as(UserRole.ADMIN)

    response = client.post(
        "/benches",
        json={
            "name": "Bench 1",
            "status": "maintenance",
        },
    )

    assert response.status_code == status.HTTP_201_CREATED

    data = response.json()

    assert data["name"] == "Bench 1"
    assert data["status"] == "maintenance"

    async with session_factory() as session:
        model = await session.get(
            BenchModel,
            data["id"],
        )

        assert model is not None
        assert model.name == "Bench 1"
        assert model.status == BenchStatus.MAINTENANCE.value


async def test_create_bench_uses_available_status_by_default(
        client: TestClient,
        authorize_as: Callable[[UserRole], None],
) -> None:
    """Use available status when it is omitted."""

    authorize_as(UserRole.ADMIN)

    response = client.post(
        "/benches",
        json={
            "name": "Bench 1",
        },
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["status"] == "available"


def test_update_bench_returns_not_found(
        client: TestClient,
        authorize_as: Callable[[UserRole], None],
) -> None:
    """Return 404 when updating an unknown bench."""

    authorize_as(UserRole.ADMIN)

    bench_id = uuid4()

    response = client.patch(
        f"/benches/{bench_id}",
        json={
            "status": "offline",
        },
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {
        "detail": "Bench not found",
    }


def test_delete_bench(
        client: TestClient,
        authorize_as: Callable[[UserRole], None],
) -> None:
    """Delete an existing bench."""

    authorize_as(UserRole.ADMIN)

    create_response = client.post(
        "/benches",
        json={
            "name": "Bench 1",
            "status": "available",
        },
    )
    bench_id = create_response.json()["id"]

    response = client.delete(
        f"/benches/{bench_id}"
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT

    get_response = client.get(
        f"/benches/{bench_id}"
    )

    assert get_response.status_code == status.HTTP_404_NOT_FOUND


def test_delete_bench_returns_not_found(
        client: TestClient,
        authorize_as: Callable[[UserRole], None],
) -> None:
    """Return 404 when deleting an unknown bench."""

    authorize_as(UserRole.ADMIN)

    bench_id = uuid4()

    response = client.delete(
        f"/benches/{bench_id}"
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {
        "detail": "Bench not found",
    }
