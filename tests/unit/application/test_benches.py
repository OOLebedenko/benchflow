from uuid import uuid4

import pytest
from pytest_mock import MockerFixture

from benchflow.application.ports.bench_repository import BenchRepository
from benchflow.application.ports.unit_of_work import UnitOfWork
from benchflow.application.services.benches import (
    BenchNotFoundError,
    BenchService,
    BenchWriteService,
)
from benchflow.domain.bench import Bench, BenchStatus


async def test_list_benches_returns_all_benches(
        mocker: MockerFixture,
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

    repository = mocker.create_autospec(
        BenchRepository,
        instance=True,
    )
    repository.list_all.return_value = benches

    service = BenchService(repository)

    # The read use case should return the domain objects supplied
    # by the repository without introducing persistence concerns.
    result = await service.list_benches()

    assert result == benches
    repository.list_all.assert_awaited_once_with()


async def test_get_bench_returns_bench(
        mocker: MockerFixture,
) -> None:
    """Return the requested bench."""

    bench = Bench(
        id=uuid4(),
        name="Bench 1",
        status=BenchStatus.AVAILABLE,
    )

    repository = mocker.create_autospec(
        BenchRepository,
        instance=True,
    )
    repository.find_by_id.return_value = bench

    service = BenchService(repository)

    result = await service.get_bench(bench.id)

    assert result == bench
    repository.find_by_id.assert_awaited_once_with(
        bench.id
    )


async def test_get_bench_rejects_unknown_id(
        mocker: MockerFixture,
) -> None:
    """Reject a request for an unknown bench."""

    bench_id = uuid4()

    repository = mocker.create_autospec(
        BenchRepository,
        instance=True,
    )
    repository.find_by_id.return_value = None

    service = BenchService(repository)

    # Missing persistence data becomes an application-level error;
    # the HTTP layer will later translate it into 404.
    with pytest.raises(BenchNotFoundError):
        await service.get_bench(bench_id)

    repository.find_by_id.assert_awaited_once_with(
        bench_id
    )


async def test_create_bench(
        mocker: MockerFixture,
) -> None:
    """Create and persist a bench."""

    repository = mocker.create_autospec(
        BenchRepository,
        instance=True,
    )

    unit_of_work = mocker.create_autospec(
        UnitOfWork,
        instance=True,
    )

    service = BenchWriteService(
        bench_repository=repository,
        unit_of_work=unit_of_work,
    )

    bench = await service.create_bench(
        name="Bench 1",
        status=BenchStatus.MAINTENANCE,
    )

    assert bench.name == "Bench 1"
    assert bench.status is BenchStatus.MAINTENANCE

    repository.add.assert_called_once_with(bench)
    unit_of_work.flush.assert_awaited_once_with()
    unit_of_work.commit.assert_awaited_once_with()
