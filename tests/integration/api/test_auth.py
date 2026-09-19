from uuid import UUID

from fastapi import status
from fastapi.testclient import TestClient


def test_register_creates_user(
        client: TestClient,
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

    assert data["email"] == "user@example.com"
    assert UUID(data["id"])

    # Neither the plaintext password nor its hash may be exposed
    # through the public API response.
    assert "password" not in data
    assert "password_hash" not in data


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
