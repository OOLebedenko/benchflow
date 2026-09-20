from uuid import uuid4

import pytest
from pytest_mock import MockerFixture

from benchflow.application.ports.bench_repository import BenchRepository
from benchflow.application.services.benches import (
    BenchNotFoundError,
    BenchService,
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
