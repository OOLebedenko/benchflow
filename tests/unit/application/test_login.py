from uuid import uuid4

import pytest
from pytest_mock import MockerFixture

from benchflow.application.ports.password_hasher import PasswordHasher
from benchflow.application.ports.token_provider import TokenProvider
from benchflow.application.ports.user_repository import UserRepository
from benchflow.application.services.login import (
    InvalidCredentialsError,
    LoginService,
)
from benchflow.domain.user import User


async def test_login_returns_access_token(
        mocker: MockerFixture,
) -> None:
    """Return an access token for valid credentials."""

    user = User(
        id=uuid4(),
        email="user@example.com",
        password_hash="hashed-password",
    )

    repository = mocker.create_autospec(
        UserRepository,
        instance=True,
    )
    repository.find_by_email.return_value = user

    password_hasher = mocker.create_autospec(
        PasswordHasher,
        instance=True,
    )
    password_hasher.verify.return_value = True

    token_provider = mocker.create_autospec(
        TokenProvider,
        instance=True,
    )
    token_provider.create_access_token.return_value = "access-token"

    service = LoginService(
        user_repository=repository,
        password_hasher=password_hasher,
        token_provider=token_provider,
    )

    # Valid credentials should reach the token issuing step.
    token = await service.login(
        email="user@example.com",
        password="secret-password",
    )

    assert token == "access-token"

    # The service must authenticate against the persisted user data
    # before issuing a token for that user's identifier.
    repository.find_by_email.assert_awaited_once_with(
        "user@example.com"
    )
    password_hasher.verify.assert_awaited_once_with(
        "secret-password",
        "hashed-password",
    )
    token_provider.create_access_token.assert_called_once_with(
        user.id
    )


async def test_login_rejects_unknown_email(
        mocker: MockerFixture,
) -> None:
    """Reject login when the email does not exist."""

    repository = mocker.create_autospec(
        UserRepository,
        instance=True,
    )
    repository.find_by_email.return_value = None

    password_hasher = mocker.create_autospec(
        PasswordHasher,
        instance=True,
    )

    token_provider = mocker.create_autospec(
        TokenProvider,
        instance=True,
    )

    service = LoginService(
        user_repository=repository,
        password_hasher=password_hasher,
        token_provider=token_provider,
    )

    # Unknown users are rejected before password verification.
    with pytest.raises(InvalidCredentialsError):
        await service.login(
            email="missing@example.com",
            password="secret-password",
        )

    repository.find_by_email.assert_awaited_once_with(
        "missing@example.com"
    )

    # No password check or token creation should happen
    # when there is no matching user.
    password_hasher.verify.assert_not_awaited()
    token_provider.create_access_token.assert_not_called()


async def test_login_rejects_wrong_password(
        mocker: MockerFixture,
) -> None:
    """Reject login when the password is incorrect."""

    user = User(
        id=uuid4(),
        email="user@example.com",
        password_hash="hashed-password",
    )

    repository = mocker.create_autospec(
        UserRepository,
        instance=True,
    )
    repository.find_by_email.return_value = user

    password_hasher = mocker.create_autospec(
        PasswordHasher,
        instance=True,
    )
    password_hasher.verify.return_value = False

    token_provider = mocker.create_autospec(
        TokenProvider,
        instance=True,
    )

    service = LoginService(
        user_repository=repository,
        password_hasher=password_hasher,
        token_provider=token_provider,
    )

    # An existing user with an invalid password must still be rejected
    # with the same application-level credentials error.
    with pytest.raises(InvalidCredentialsError):
        await service.login(
            email="user@example.com",
            password="wrong-password",
        )

    repository.find_by_email.assert_awaited_once_with(
        "user@example.com"
    )
    password_hasher.verify.assert_awaited_once_with(
        "wrong-password",
        "hashed-password",
    )

    # A failed password check must never result in a token.
    token_provider.create_access_token.assert_not_called()
