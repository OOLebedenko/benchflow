from uuid import uuid4

import pytest
from psycopg.errors import UniqueViolation
from pytest_mock import MockerFixture
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from benchflow.application.ports.unit_of_work import (
    UniqueConstraintViolationError,
)
from benchflow.infrastructure.db.models.bench import BenchModel
from benchflow.infrastructure.db.unit_of_work import (
    SqlAlchemyUnitOfWork,
)


async def test_flush_flushes_session(
        mocker: MockerFixture,
) -> None:
    """Flush the current SQLAlchemy session."""

    session = mocker.create_autospec(
        AsyncSession,
        instance=True,
    )
    unit_of_work = SqlAlchemyUnitOfWork(session)

    await unit_of_work.flush()

    session.flush.assert_awaited_once_with()
    session.rollback.assert_not_awaited()


async def test_commit_commits_session(
        mocker: MockerFixture,
) -> None:
    """Commit the current SQLAlchemy session."""

    session = mocker.create_autospec(
        AsyncSession,
        instance=True,
    )
    unit_of_work = SqlAlchemyUnitOfWork(session)

    await unit_of_work.commit()

    session.commit.assert_awaited_once_with()
    session.rollback.assert_not_awaited()


async def test_rollback_rolls_back_session(
        mocker: MockerFixture,
) -> None:
    """Roll back the current SQLAlchemy session."""

    session = mocker.create_autospec(
        AsyncSession,
        instance=True,
    )
    unit_of_work = SqlAlchemyUnitOfWork(session)

    await unit_of_work.rollback()

    session.rollback.assert_awaited_once_with()


async def test_flush_applies_staged_delete(
        mocker: MockerFixture,
) -> None:
    """Apply staged deletions before flushing the session."""

    session = mocker.create_autospec(
        AsyncSession,
        instance=True,
    )

    model_id = uuid4()
    model = mocker.Mock(spec=BenchModel)
    session.get.return_value = model

    unit_of_work = SqlAlchemyUnitOfWork(session)

    unit_of_work.stage_delete(
        BenchModel,
        model_id,
    )
    await unit_of_work.flush()

    session.get.assert_awaited_once_with(
        BenchModel,
        model_id,
    )
    session.delete.assert_awaited_once_with(model)
    session.flush.assert_awaited_once_with()


async def test_rollback_discards_staged_delete(
        mocker: MockerFixture,
) -> None:
    """Discard staged deletions when rolling back."""

    session = mocker.create_autospec(
        AsyncSession,
        instance=True,
    )

    model_id = uuid4()

    unit_of_work = SqlAlchemyUnitOfWork(session)

    unit_of_work.stage_delete(
        BenchModel,
        model_id,
    )
    await unit_of_work.rollback()
    await unit_of_work.flush()

    session.get.assert_not_awaited()
    session.delete.assert_not_awaited()
    session.flush.assert_awaited_once_with()


async def test_flush_rolls_back_on_failure(
        mocker: MockerFixture,
) -> None:
    """Roll back the unit of work when flushing fails."""

    session = mocker.create_autospec(
        AsyncSession,
        instance=True,
    )
    error = RuntimeError("flush failed")
    session.flush.side_effect = error

    unit_of_work = SqlAlchemyUnitOfWork(session)

    with pytest.raises(RuntimeError, match="flush failed"):
        await unit_of_work.flush()

    session.rollback.assert_awaited_once_with()


async def test_flush_translates_unique_violation(
        mocker: MockerFixture,
) -> None:
    """Translate uniqueness violations after rolling back."""

    session = mocker.create_autospec(
        AsyncSession,
        instance=True,
    )
    session.flush.side_effect = IntegrityError(
        statement="INSERT",
        params={},
        orig=UniqueViolation("duplicate key"),
    )

    unit_of_work = SqlAlchemyUnitOfWork(session)

    with pytest.raises(UniqueConstraintViolationError):
        await unit_of_work.flush()

    session.rollback.assert_awaited_once_with()


async def test_flush_preserves_rollback_failure(
        mocker: MockerFixture,
) -> None:
    """Preserve the original failure when rollback also fails."""

    session = mocker.create_autospec(
        AsyncSession,
        instance=True,
    )

    operation_error = RuntimeError("flush failed")
    rollback_error = RuntimeError("rollback failed")

    session.flush.side_effect = operation_error
    session.rollback.side_effect = rollback_error

    unit_of_work = SqlAlchemyUnitOfWork(session)

    with pytest.raises(
            RuntimeError,
            match="rollback failed",
    ) as exc_info:
        await unit_of_work.flush()

    assert exc_info.value.__cause__ is operation_error
