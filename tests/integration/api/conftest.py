from collections.abc import Callable, Generator
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

import benchflow.presentation.lifespan as lifespan_module
from benchflow.config import Settings
from benchflow.domain.user import User, UserRole
from benchflow.main import app
from benchflow.presentation.dependencies.auth import get_current_user


@pytest.fixture
def client(
        migrated_database_url: str,
        redis_url: str,
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
        redis_url=redis_url,
        bench_lock_ttl_seconds=30,
    )

    # Redirect the application lifespan from the local database configured
    # in .env to the isolated PostgreSQL database created for integration tests.
    monkeypatch.setattr(
        lifespan_module,
        "load_settings",
        lambda: settings,
    )

    # Using TestClient as a context manager runs the real FastAPI lifespan:
    # startup creates application resources and shutdown disposes them.
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def authorize_as() -> Generator[
    Callable[[UserRole], None],
    None,
    None,
]:
    """Override the authenticated user for authorization tests."""

    def authorize(role: UserRole) -> None:
        user = User(
            id=uuid4(),
            email=f"{role.value}@example.com",
            password_hash="hashed-password",
            role=role,
        )

        async def override_current_user() -> User:
            return user

        app.dependency_overrides[
            get_current_user
        ] = override_current_user

    try:
        yield authorize
    finally:
        app.dependency_overrides.pop(
            get_current_user,
            None,
        )
