from fastapi import status
from fastapi.testclient import TestClient


def test_get_me_returns_current_user(
        client: TestClient,
) -> None:
    """Return the authenticated user."""

    credentials = {
        "email": "user@example.com",
        "password": "secret-password",
    }

    register_response = client.post(
        "/auth/register",
        json=credentials,
    )

    assert register_response.status_code == status.HTTP_201_CREATED

    login_response = client.post(
        "/auth/login",
        json=credentials,
    )

    assert login_response.status_code == status.HTTP_200_OK

    access_token = login_response.json()["access_token"]

    response = client.get(
        "/users/me",
        headers={
            "Authorization": f"Bearer {access_token}",
        },
    )

    assert response.status_code == status.HTTP_200_OK

    data = response.json()

    assert data["id"] == register_response.json()["id"]
    assert data["email"] == credentials["email"]


def test_get_me_rejects_missing_token(
        client: TestClient,
) -> None:
    """Reject access when no bearer token is provided."""

    response = client.get("/users/me")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {
        "detail": "Not authenticated"
    }
    assert response.headers["WWW-Authenticate"] == "Bearer"


def test_get_me_rejects_invalid_token(
        client: TestClient,
) -> None:
    """Reject access when the bearer token is invalid."""

    response = client.get(
        "/users/me",
        headers={
            "Authorization": "Bearer invalid-token",
        },
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {
        "detail": "Invalid authentication credentials"
    }
    assert response.headers["WWW-Authenticate"] == "Bearer"
