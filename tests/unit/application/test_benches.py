from unittest.mock import MagicMock
from uuid import uuid4

import pytest
from pytest_mock import MockerFixture

from benchflow.application.ports.bench_repository import BenchRepository
from benchflow.application.ports.unit_of_work import UnitOfWork
from benchflow.application.services.benches import (
    BenchNotFoundError,
    BenchService,
)
from benchflow.domain.bench import Bench, BenchStatus


@pytest.fixture
def repository(
        mocker: MockerFixture,
) -> MagicMock:
    """Provide a mocked bench repository."""

    return mocker.create_autospec(
        BenchRepository,
        instance=True,
    )


@pytest.fixture
def unit_of_work(
        mocker: MockerFixture,
) -> MagicMock:
    """Provide a mocked unit of work."""

    return mocker.create_autospec(
        UnitOfWork,
        instance=True,
    )


@pytest.fixture
def service(
        repository: MagicMock,
        unit_of_work: MagicMock,
) -> BenchService:
    """Provide a bench service with mocked dependencies."""

    return BenchService(
        bench_repository=repository,
        unit_of_work=unit_of_work,
    )


async def test_list_benches_returns_all_benches(
        service: BenchService,
        repository: MagicMock,
) -> None:
    """Return all benches."""

    benches = [
        Bench(
            id=uuid4(),
            name="Bench 1",
            status=BenchStatus.AVAILABLE,
        ),
        Bench(
            id=uuid4(),
            name="Bench 2",
            status=BenchStatus.MAINTENANCE,
        ),
    ]

    repository.list_all.return_value = benches

    result = await service.list_benches()

    assert result == benches
    repository.list_all.assert_awaited_once_with()


async def test_get_bench_returns_bench(
        service: BenchService,
        repository: MagicMock,
) -> None:
    """Return the requested bench."""

    bench = Bench(
        id=uuid4(),
        name="Bench 1",
        status=BenchStatus.AVAILABLE,
    )

    repository.find_by_id.return_value = bench

    result = await service.get_bench(bench.id)

    assert result == bench
    repository.find_by_id.assert_awaited_once_with(
        bench.id
    )


async def test_get_bench_rejects_unknown_id(
        service: BenchService,
        repository: MagicMock,
) -> None:
    """Reject a request for an unknown bench."""

    bench_id = uuid4()

    repository.find_by_id.return_value = None

    with pytest.raises(BenchNotFoundError):
        await service.get_bench(bench_id)

    repository.find_by_id.assert_awaited_once_with(
        bench_id
    )


async def test_create_bench(
        service: BenchService,
        repository: MagicMock,
        unit_of_work: MagicMock,
) -> None:
    """Create and persist a bench."""

    bench = await service.create_bench(
        name="Bench 1",
        status=BenchStatus.MAINTENANCE,
    )

    assert bench.name == "Bench 1"
    assert bench.status is BenchStatus.MAINTENANCE

    repository.add.assert_called_once_with(bench)
    unit_of_work.flush.assert_awaited_once_with()
    unit_of_work.commit.assert_awaited_once_with()


async def test_delete_bench(
        service: BenchService,
        repository: MagicMock,
        unit_of_work: MagicMock,
) -> None:
    """Delete an existing bench."""

    bench = Bench(
        id=uuid4(),
        name="Bench 1",
        status=BenchStatus.AVAILABLE,
    )

    repository.find_by_id.return_value = bench

    await service.delete_bench(bench.id)

    repository.find_by_id.assert_awaited_once_with(
        bench.id
    )
    repository.delete.assert_called_once_with(bench)
    unit_of_work.flush.assert_awaited_once_with()
    unit_of_work.commit.assert_awaited_once_with()


async def test_delete_bench_rejects_unknown_id(
        service: BenchService,
        repository: MagicMock,
        unit_of_work: MagicMock,
) -> None:
    """Reject deletion of an unknown bench."""

    bench_id = uuid4()

    repository.find_by_id.return_value = None

    with pytest.raises(BenchNotFoundError):
        await service.delete_bench(bench_id)

    repository.find_by_id.assert_awaited_once_with(
        bench_id
    )
    repository.delete.assert_not_called()
    unit_of_work.flush.assert_not_awaited()
    unit_of_work.commit.assert_not_awaited()
