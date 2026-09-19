from uuid import uuid4

import pytest
from pytest_mock import MockerFixture

from benchflow.application.ports.token_provider import (
    InvalidTokenError,
    TokenProvider,
)
from benchflow.application.ports.user_repository import UserRepository
from benchflow.application.services.current_user import (
    AuthenticationError,
    CurrentUserService,
)
from benchflow.domain.user import User


async def test_get_current_user_returns_user(
        mocker: MockerFixture,
) -> None:
    """Return the user identified by a valid access token."""

    user = User(
        id=uuid4(),
        email="user@example.com",
        password_hash="hashed-password",
    )

    token_provider = mocker.create_autospec(
        TokenProvider,
        instance=True,
    )
    token_provider.validate_access_token.return_value = user.id

    repository = mocker.create_autospec(
        UserRepository,
        instance=True,
    )
    repository.find_by_id.return_value = user

    service = CurrentUserService(
        user_repository=repository,
        token_provider=token_provider,
    )

    current_user = await service.get_current_user("access-token")

    assert current_user == user

    # A valid token identifies the user that must be loaded
    # from persistent storage.
    token_provider.validate_access_token.assert_called_once_with(
        "access-token"
    )
    repository.find_by_id.assert_awaited_once_with(user.id)


async def test_get_current_user_rejects_invalid_token(
        mocker: MockerFixture,
) -> None:
    """Reject authentication when the access token is invalid."""

    token_provider = mocker.create_autospec(
        TokenProvider,
        instance=True,
    )
    token_provider.validate_access_token.side_effect = InvalidTokenError

    repository = mocker.create_autospec(
        UserRepository,
        instance=True,
    )

    service = CurrentUserService(
        user_repository=repository,
        token_provider=token_provider,
    )

    # Token validation fails before a user identifier can be resolved.
    with pytest.raises(AuthenticationError):
        await service.get_current_user("invalid-token")

    token_provider.validate_access_token.assert_called_once_with(
        "invalid-token"
    )

    # No database lookup should happen for an invalid token.
    repository.find_by_id.assert_not_awaited()


async def test_get_current_user_rejects_missing_user(
        mocker: MockerFixture,
) -> None:
    """Reject authentication when the token user no longer exists."""

    user_id = uuid4()

    token_provider = mocker.create_autospec(
        TokenProvider,
        instance=True,
    )
    token_provider.validate_access_token.return_value = user_id

    repository = mocker.create_autospec(
        UserRepository,
        instance=True,
    )
    repository.find_by_id.return_value = None

    service = CurrentUserService(
        user_repository=repository,
        token_provider=token_provider,
    )

    # A correctly signed token is not enough if its subject no longer
    # corresponds to an existing user.
    with pytest.raises(AuthenticationError):
        await service.get_current_user("access-token")

    token_provider.validate_access_token.assert_called_once_with(
        "access-token"
    )
    repository.find_by_id.assert_awaited_once_with(user_id)
