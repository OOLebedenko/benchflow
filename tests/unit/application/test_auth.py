from uuid import uuid4

import pytest
from pytest_mock import MockerFixture

from benchflow.application.ports.flusher import (
    Flusher,
    UniqueConstraintViolationError,
)
from benchflow.application.ports.password_hasher import PasswordHasher
from benchflow.application.ports.transaction_manager import TransactionManager
from benchflow.application.ports.user_repository import UserRepository
from benchflow.application.services.auth import (
    AuthService,
    EmailAlreadyExistsError,
)
from benchflow.domain.user import User


async def test_register_creates_user(
        mocker: MockerFixture,
) -> None:
    """Register a user, hash their password, and persist them."""

    # Simulate that no user with this email exists yet.
    repository = mocker.create_autospec(
        UserRepository,
        instance=True,
    )
    repository.find_by_email.return_value = None

    # Use a deterministic hash so the service result can be verified
    # without running the real password hashing implementation.
    password_hasher = mocker.create_autospec(
        PasswordHasher,
        instance=True,
    )
    password_hasher.hash.return_value = "hashed-password"

    flusher = mocker.create_autospec(
        Flusher,
        instance=True,
    )

    transaction_manager = mocker.create_autospec(
        TransactionManager,
        instance=True,
    )

    service = AuthService(
        user_repository=repository,
        password_hasher=password_hasher,
        flusher=flusher,
        transaction_manager=transaction_manager,
    )

    user = await service.register(
        email="user@example.com",
        password="secret-password",
    )

    # The created domain entity contains the expected application data.
    assert user.email == "user@example.com"
    assert user.password_hash == "hashed-password"

    # Registration must check uniqueness, hash the password,
    # add the created user, flush pending changes, and commit the transaction.
    repository.find_by_email.assert_awaited_once_with(
        "user@example.com"
    )
    password_hasher.hash.assert_awaited_once_with(
        "secret-password"
    )
    repository.add.assert_called_once_with(user)
    flusher.flush.assert_awaited_once_with()
    transaction_manager.commit.assert_awaited_once_with()


async def test_register_rejects_existing_email(
        mocker: MockerFixture,
) -> None:
    """Reject registration when the email already exists."""

    existing_user = User(
        id=uuid4(),
        email="user@example.com",
        password_hash="existing-hash",
    )

    # Simulate that the repository already contains this email.
    repository = mocker.create_autospec(
        UserRepository,
        instance=True,
    )
    repository.find_by_email.return_value = existing_user

    password_hasher = mocker.create_autospec(
        PasswordHasher,
        instance=True,
    )

    flusher = mocker.create_autospec(
        Flusher,
        instance=True,
    )

    transaction_manager = mocker.create_autospec(
        TransactionManager,
        instance=True,
    )

    service = AuthService(
        user_repository=repository,
        password_hasher=password_hasher,
        flusher=flusher,
        transaction_manager=transaction_manager,
    )

    with pytest.raises(EmailAlreadyExistsError):
        await service.register(
            email="user@example.com",
            password="secret-password",
        )

    # Registration must stop immediately after detecting the duplicate:
    # no expensive password hashing, persistence, flush, or commit.
    repository.find_by_email.assert_awaited_once_with(
        "user@example.com"
    )
    password_hasher.hash.assert_not_awaited()
    repository.add.assert_not_called()
    flusher.flush.assert_not_awaited()
    transaction_manager.commit.assert_not_awaited()


async def test_register_rejects_email_conflict_on_flush(
        mocker: MockerFixture,
) -> None:
    """Reject registration when email uniqueness fails during flush."""

    # Simulate the race-condition case: the preliminary lookup finds
    # no user, but another transaction claims the email before our flush.
    repository = mocker.create_autospec(
        UserRepository,
        instance=True,
    )
    repository.find_by_email.return_value = None

    password_hasher = mocker.create_autospec(
        PasswordHasher,
        instance=True,
    )
    password_hasher.hash.return_value = "hashed-password"

    flusher = mocker.create_autospec(
        Flusher,
        instance=True,
    )
    flusher.flush.side_effect = UniqueConstraintViolationError

    transaction_manager = mocker.create_autospec(
        TransactionManager,
        instance=True,
    )

    service = AuthService(
        user_repository=repository,
        password_hasher=password_hasher,
        flusher=flusher,
        transaction_manager=transaction_manager,
    )

    with pytest.raises(EmailAlreadyExistsError):
        await service.register(
            email="user@example.com",
            password="secret-password",
        )

    # The conflict occurs after the user has already been constructed
    # and added to the current unit of work.
    repository.find_by_email.assert_awaited_once_with(
        "user@example.com"
    )
    password_hasher.hash.assert_awaited_once_with(
        "secret-password"
    )
    repository.add.assert_called_once()
    flusher.flush.assert_awaited_once_with()

    # A transaction that failed during flush must never be committed.
    transaction_manager.commit.assert_not_awaited()
