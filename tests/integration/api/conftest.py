from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

import benchflow.presentation.lifespan as lifespan_module
from benchflow.config import Settings
from benchflow.main import app


@pytest.fixture
def client(
        migrated_database_url: str,
        session_factory: async_sessionmaker[AsyncSession],
        monkeypatch: pytest.MonkeyPatch,
) -> Generator[TestClient, None, None]:
    """Provide FastAPI client connected to the integration database."""

    # Request session_factory so the existing integration fixture performs
    # database cleanup after this API test finishes.
    _ = session_factory

    settings = Settings(
        database_url=migrated_database_url,
        jwt_secret="a" * 32,
        jwt_algorithm="HS256",
        access_token_expire_minutes=15,
    )

    # Redirect the application lifespan from the local database configured
    # in .env to the isolated PostgreSQL database created for integration tests.
    monkeypatch.setattr(
        lifespan_module,
        "load_settings",
        lambda: settings,
    )

    # Using TestClient as a context manager runs the real FastAPI lifespan:
    # startup creates the engine and session factory, shutdown disposes them.
    with TestClient(app) as test_client:
        yield test_client
