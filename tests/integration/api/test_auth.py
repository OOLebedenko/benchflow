from uuid import UUID

from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from benchflow.domain.user import UserRole
from benchflow.infrastructure.db.models.user import UserModel


async def test_register_creates_user(
        client: TestClient,
        session_factory: async_sessionmaker[AsyncSession],
) -> None:
    """Register a new user."""

    response = client.post(
        "/auth/register",
        json={
            "email": "user@example.com",
            "password": "secret-password",
        },
    )

    assert response.status_code == status.HTTP_201_CREATED

    data = response.json()
    user_id = UUID(data["id"])

    assert data["email"] == "user@example.com"

    # Neither the plaintext password nor its hash may be exposed
    # through the public API response.
    assert "password" not in data
    assert "password_hash" not in data

    async with session_factory() as session:
        user = await session.get(
            UserModel,
            user_id,
        )

        assert user is not None
        assert user.role == UserRole.USER.value


def test_register_rejects_existing_email(
        client: TestClient,
) -> None:
    """Reject registration when the email already exists."""

    payload = {
        "email": "user@example.com",
        "password": "secret-password",
    }

    # The first request persists the user and commits the transaction.
    first_response = client.post(
        "/auth/register",
        json=payload,
    )

    # A second request with the same email must detect the persisted user.
    second_response = client.post(
        "/auth/register",
        json=payload,
    )

    assert first_response.status_code == status.HTTP_201_CREATED
    assert second_response.status_code == status.HTTP_409_CONFLICT

    assert second_response.json() == {
        "detail": "User with this email already exists"
    }


def test_register_rejects_invalid_email(
        client: TestClient,
) -> None:
    """Reject registration when the email is invalid."""

    response = client.post(
        "/auth/register",
        json={
            "email": "not-an-email",
            "password": "secret-password",
        },
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


def test_register_rejects_short_password(
        client: TestClient,
) -> None:
    """Reject registration when the password is too short."""

    response = client.post(
        "/auth/register",
        json={
            "email": "user@example.com",
            "password": "short",
        },
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


def test_login_returns_access_token(
        client: TestClient,
) -> None:
    """Return an access token for valid credentials."""

    credentials = {
        "email": "user@example.com",
        "password": "secret-password",
    }

    # Register through the public API so the login test exercises
    # the same persisted password hash used by the real application.
    register_response = client.post(
        "/auth/register",
        json=credentials,
    )

    assert register_response.status_code == status.HTTP_201_CREATED

    response = client.post(
        "/auth/login",
        json=credentials,
    )

    assert response.status_code == status.HTTP_200_OK

    data = response.json()

    assert isinstance(data["access_token"], str)
    assert data["access_token"]
    assert data["token_type"] == "bearer"


def test_login_rejects_unknown_email(
        client: TestClient,
) -> None:
    """Reject login when the email does not exist."""

    response = client.post(
        "/auth/login",
        json={
            "email": "missing@example.com",
            "password": "secret-password",
        },
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {
        "detail": "Invalid email or password"
    }


def test_login_rejects_wrong_password(
        client: TestClient,
) -> None:
    """Reject login when the password is incorrect."""

    register_response = client.post(
        "/auth/register",
        json={
            "email": "user@example.com",
            "password": "secret-password",
        },
    )

    assert register_response.status_code == status.HTTP_201_CREATED

    response = client.post(
        "/auth/login",
        json={
            "email": "user@example.com",
            "password": "wrong-password",
        },
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {
        "detail": "Invalid email or password"
    }
