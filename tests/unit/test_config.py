import pytest

from benchflow.config import load_settings


def test_load_settings_from_environment(
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Load application settings from environment variables."""

    database_url = (
        "postgresql+psycopg://benchflow:benchflow@localhost:5432/benchflow"
    )
    jwt_secret = "a" * 32

    monkeypatch.setenv(
        "DATABASE_URL",
        database_url,
    )
    monkeypatch.setenv(
        "JWT_SECRET",
        jwt_secret,
    )

    settings = load_settings()

    assert settings.database_url == database_url
    assert settings.jwt_secret.get_secret_value() == jwt_secret
    assert settings.jwt_algorithm == "HS256"
    assert settings.access_token_expire_minutes == 15
