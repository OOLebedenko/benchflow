import pytest

from benchflow.config import load_settings


def test_load_settings_from_environment(
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Load database settings from environment variables."""

    database_url = (
        "postgresql+psycopg://benchflow:benchflow@localhost:5432/benchflow"
    )

    monkeypatch.setenv("DATABASE_URL", database_url)

    settings = load_settings()

    assert settings.database_url == database_url
