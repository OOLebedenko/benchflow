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
    redis_url = "redis://localhost:6379/0"

    monkeypatch.setenv(
        "DATABASE_URL",
        database_url,
    )
    monkeypatch.setenv(
        "JWT_SECRET",
        jwt_secret,
    )
    monkeypatch.setenv(
        "JWT_ALGORITHM",
        "HS256",
    )
    monkeypatch.setenv(
        "ACCESS_TOKEN_EXPIRE_MINUTES",
        "15",
    )
    monkeypatch.setenv(
        "REDIS_URL",
        redis_url,
    )
    monkeypatch.setenv(
        "BENCH_LOCK_TTL_SECONDS",
        "30",
    )

    settings = load_settings()

    assert settings.database_url == database_url
    assert settings.jwt_secret.get_secret_value() == jwt_secret
    assert settings.jwt_algorithm == "HS256"
    assert settings.access_token_expire_minutes == 15
    assert settings.redis_url == redis_url
    assert settings.bench_lock_ttl_seconds == 30
