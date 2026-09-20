from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from benchflow.application.ports.unit_of_work import (
    UniqueConstraintViolationError,
)
from benchflow.domain.user import User
from benchflow.infrastructure.db.unit_of_work import (
    SqlAlchemyUnitOfWork,
)
from benchflow.infrastructure.repositories.user import (
    SqlAlchemyUserRepository,
)


async def test_add_and_find_user(
        session_factory: async_sessionmaker[AsyncSession],
) -> None:
    """Add a user and find them by email."""

    user = User(
        id=uuid4(),
        email="user@example.com",
        password_hash="hashed-password",
    )

    async with session_factory() as session:
        repository = SqlAlchemyUserRepository(session)
        unit_of_work = SqlAlchemyUnitOfWork(session)

        # add() only places the model into the current unit of work.
        # flush() sends the pending INSERT to PostgreSQL.
        repository.add(user)
        await unit_of_work.flush()

        # The current transaction can read its own flushed changes
        # even though they have not been committed yet.
        stored_user = await repository.find_by_email(user.email)

        assert stored_user == user


async def test_find_by_email_returns_none(
        session_factory: async_sessionmaker[AsyncSession],
) -> None:
    """Return None when no user has the requested email."""

    async with session_factory() as session:
        repository = SqlAlchemyUserRepository(session)

        user = await repository.find_by_email(
            "missing@example.com"
        )

        assert user is None


async def test_flush_rejects_duplicate_email(
        session_factory: async_sessionmaker[AsyncSession],
) -> None:
    """Reject duplicate email when pending changes are flushed."""

    first_user = User(
        id=uuid4(),
        email="user@example.com",
        password_hash="first-hash",
    )
    second_user = User(
        id=uuid4(),
        email="user@example.com",
        password_hash="second-hash",
    )

    async with session_factory() as session:
        repository = SqlAlchemyUserRepository(session)
        unit_of_work = SqlAlchemyUnitOfWork(session)

        # The first flush sends the first INSERT to PostgreSQL,
        # so its email already participates in the UNIQUE constraint
        # inside the current transaction.
        repository.add(first_user)
        await unit_of_work.flush()

        # add() itself performs no database I/O, so the duplicate is
        # detected only when the pending INSERT is flushed.
        repository.add(second_user)

        with pytest.raises(UniqueConstraintViolationError):
            await unit_of_work.flush()


async def test_commit_makes_flushed_user_visible(
        session_factory: async_sessionmaker[AsyncSession],
) -> None:
    """Make flushed changes visible to other sessions after commit."""

    user = User(
        id=uuid4(),
        email="user@example.com",
        password_hash="hashed-password",
    )

    async with session_factory() as write_session:
        repository = SqlAlchemyUserRepository(write_session)
        unit_of_work = SqlAlchemyUnitOfWork(write_session)

        # Flush sends the INSERT to PostgreSQL but leaves the
        # surrounding transaction open.
        repository.add(user)
        await unit_of_work.flush()

        # A different session uses a different transaction and must not
        # see the writer's uncommitted row.
        async with session_factory() as read_session:
            reader = SqlAlchemyUserRepository(read_session)

            assert await reader.find_by_email(user.email) is None

        # Commit completes the writer transaction and makes its changes
        # visible to subsequent transactions.
        await unit_of_work.commit()

    # A new session can now read the committed user.
    async with session_factory() as read_session:
        reader = SqlAlchemyUserRepository(read_session)
